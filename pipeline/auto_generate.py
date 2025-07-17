from netaddr import IPNetwork
from typing import Optional, List, Dict, Any
import random
import json
from network import Network
from ip_handling import generate_all_nmap_options

from netaddr import IPNetwork
import random

def generate_random_cidrs(subnets: int = 2, neighbors: bool = True) -> list[IPNetwork]:
    """
    Generate a list of CIDR blocks in a private IP range using only even-numbered prefix lengths.

    Args:
        subnets (int): Number of CIDR blocks to generate.
        neighbors (bool): Whether the subnets should be adjacent.

    Returns:
        list[IPNetwork]: List of CIDR blocks like ["10.2.3.0/24", "10.2.4.0/24"]
    """
    private_blocks = [
        {
            "base": lambda: (10, random.randint(0, 255), random.randint(0, 255)),
            "min_prefix": 8,
            "max_prefix": 24
        },
        {
            "base": lambda: (172, random.randint(16, 31), random.randint(0, 255)),
            "min_prefix": 12,
            "max_prefix": 24
        },
        {
            "base": lambda: (192, 168, random.randint(0, 255)),
            "min_prefix": 16,
            "max_prefix": 24
        }
    ]

    # Only use even-numbered prefix lengths
    # even_prefixes = [p for p in range(8, 29) if p % 2 == 0]  # up to /28 for realism
    even_prefixes = [8, 12, 16, 24]
    block = random.choice(private_blocks)
    min_p, max_p = block["min_prefix"], block["max_prefix"]

    # Filter even prefixes within this block's allowed range
    valid_prefixes = [p for p in even_prefixes if min_p <= p <= max_p]
    if not valid_prefixes:
        valid_prefixes = [max_p if max_p % 2 == 0 else max_p - 1]

    prefix = random.choice(valid_prefixes)

    a, b, c = block["base"]()
    base_cidr = IPNetwork(f"{a}.{b}.{c}.0/{prefix}").cidr

    cidrs = [base_cidr]

    if neighbors:
        current = base_cidr
        for _ in range(subnets - 1):
            current = current.next()
            cidrs.append(current)
    else:
        seen = {str(base_cidr)}
        while len(cidrs) < subnets:
            a2, b2, c2 = block["base"]()
            new = IPNetwork(f"{a2}.{b2}.{c2}.0/{prefix}").cidr
            if str(new) not in seen:
                cidrs.append(new)
                seen.add(str(new))

    return cidrs


def get_baseline_dict(item_type, name, **kwargs):
    baseline = {
        "type": item_type,
        'name': name,
    }
    ip = kwargs.get("ip")
    if ip:
        baseline["ip"] = ip
    # {'type': 'cluster', 'name': f'switch_cluster{i}', 'cluster_type': 'intermediate', 'nodes': [{'type': 'device', 'name': f'Switch{i}', 'device_type': 'Switch'},]},
    if item_type == "device":
        device_type = kwargs.get("device_type")
        assert(device_type)
        baseline.update({
            'device_type': device_type,  
            "Latency": str(round(random.uniform(0.01, 0.1), 3)),
            "PortsClosed": "",
            "PortsFiltered": "", 
        })
        
        display_name = kwargs.get('display_name')
        if display_name:
            baseline["display_name"] = display_name
        if device_type == "Workstation":
            baseline["PortsOpen"] = "22 53 80 139 443 445"
        elif device_type == "Firewall":
            baseline["PortsOpen"] = "22 53 80 123 389 443"
        elif device_type in ["Switch", "DomainController"]:
            baseline["PortsOpen"] = "22 53 80 88 135 139 389 443 445 464" 
        else:
            baseline["PortsOpen"] = "22 53 80 443" 
    else:
        cluster_type = kwargs.get("cluster_type")
        assert(cluster_type)
        nodes = kwargs.get("nodes")
        assert(nodes)
        baseline.update({
            'cluster_type': cluster_type,
            'nodes': nodes
        })

    return baseline

def generate_network_config(problem_type: str, cidr_blocks: list['IPNetwork']) -> tuple[list, dict]:
    """
    Generate a list of CIDR blocks in a private range.

    Args:
        problem_type (str): What type of problem the network is for (e.g. "Bad Ports")
        cidr_blocks (list['IPNetwork']): CIDR blocks for each subnet in the network

    Returns:
        tuple[list, dict]: list of dictionaries of devices in the network, and dictionary of connections between these devices
    """

    config = [
        get_baseline_dict(item_type="device", device_type="Internet", name="Internet"),
        get_baseline_dict(item_type="device", device_type="Router", name="BorderRouter"),
        get_baseline_dict(item_type="device", device_type="User", name="UserLocation", display_name="You are connected here"),
    ]

    connections: dict[str, list[tuple]] = {
        "Internet": [("BorderRouter", "child", (' 128.237.3.102 ',""))],
    }
    has_user_loc = False
    
    for i in range(len(cidr_blocks)):
        net = cidr_blocks[i]
        config = config + [
            get_baseline_dict(item_type="device", device_type="Firewall", name=f'Firewall{i}'),
            get_baseline_dict(item_type = "cluster", name=f'switch_cluster{i}', cluster_type='intermediate', 
                              nodes= [get_baseline_dict(item_type="device", name=f'Switch{i}', device_type= 'Switch')]),
            get_baseline_dict(item_type = "cluster", name=f'Office{i}', cluster_type='intermediate', ip= str(net),
                              nodes= [get_baseline_dict(item_type="device", name= f'DomainController{i}', device_type="Controller", ip= f'{net[10]}', display_name= 'Domain Controller')])
            ]
        
        connections.setdefault("BorderRouter", []).append((f"Firewall{i}", "child", (f"  {net[1]}  ", f"  {net[3]}  ")))
        connections[f'Firewall{i}'] = [(f'switch_cluster{i}', "same", (f"  {net[5]}  ", ""))]
        
        connections[f'switch_cluster{i}'] = [(f'Office{i}', "above",)]
        if not has_user_loc:
            connections[f'switch_cluster{i}'].append(("UserLocation", "same", ("", f"  {net[20]}  ", "")))
            has_user_loc = True

        offset = random.randint(40, 100)
        for j in range(1,random.randint(2, 4)):
            ip_address = net[offset+j]
            config.append(get_baseline_dict(item_type= "cluster", name=f'ClusterWorkstation{i+j}', cluster_type='endpoint',
                              nodes= [get_baseline_dict(item_type='device', name=f'Workstation{i+j}', device_type="Workstation", ip=f'{ip_address}', display_name=f'User Workstation {i+j}')]))
            connections.setdefault(f'switch_cluster{i}', []).append(( f'ClusterWorkstation{i+j}',))
        
    return config, connections

# subnet: [(number of servers, ports open, number of users, ports open, whether theres a firewall), ...]
    
def generate_network(items: list, connections: dict, output_name: str = "network") -> 'Network':
    """
    Generates a dictionary graph representation of the network, where nodes that are connected by an edge in the map are neighbors

    Args:
        items (list[dict]): A list of items in the network
        connections (dict): Collection of one way connections of devices on the network
    Returns:
        dict: Dictionary representation of network map
    """
    map_rep = Network("ExampleNetwork")
    map_rep.add_items_from_config(items)
    map_rep.connect_items_from_config(connections)

    return map_rep
# exampledata = [{ IP: "172.16.0.1", Latency: "0.062", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 443" }, { IP: "172.16.0.2", Latency: "0.051", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 443" }, { IP: "172.16.0.3", Latency: "0.044", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 123 389 443" }, { IP: "172.16.5.5", Latency: "0.004", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 443" }, { IP: "172.16.9.10", Latency: "0.083", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 88 135 139 389 443 445 464" }, { IP: "172.16.31.100", Latency: "0.039", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 139 443 445" }, { IP: "172.16.31.101", Latency: "0.037", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 139 443 445" }, { IP: "172.16.31.102", Latency: "0.29", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 139 443 445 6886" }];
# IP Address
# Type of Computer (Firewall, Domain Controller, Border Router, Switch, UserLocation, User Workstation, etc)
# Location in the network (edges? neighbors? Clusters?)
# [{ IP: "172.16.0.1", Latency: "0.062", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 443" }, { IP: "172.16.0.2", Latency: "0.051", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 443" }, { IP: "172.16.0.3", Latency: "0.044", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 123 389 443" }, { IP: "172.16.5.5", Latency: "0.004", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 443" }, { IP: "172.16.9.10", Latency: "0.083", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 88 135 139 389 443 445 464" }, { IP: "172.16.31.100", Latency: "0.039", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 139 443 445" }, { IP: "172.16.31.101", Latency: "0.037", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 139 443 445" }, { IP: "172.16.31.102", Latency: "0.29", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 139 443 445 6886" }];
def generate_example_data(prob_type: str, items: list) -> list[dict[str, str]]:
    example_data = []

    for item in items:
        if item['type'] == "device":
            example_data.append({
                "Latency": item["Latency"],
                "PortsClosed": item["PortsClosed"],
                "PortsFiltered": item["PortsFiltered"],
                "PortsOpen": item["PortsOpen"]
            })
        elif item['type'] == "cluster":
            for node in item['nodes']:
                example_data.append({
                "Latency": node["Latency"],
                "PortsClosed": node["PortsClosed"],
                "PortsFiltered": node["PortsFiltered"],
                "PortsOpen": node["PortsOpen"]
            })
            
        else:
            assert(False)
        item_info = dict()
        # don't put cidr blocks in the nmap
        if item["device_type"] == "cluster":
            continue
        item_info['IP'] = item["ip_address"]
        item_info["Latency"] = str(round(random.uniform(0.01, 0.1), 3))
        item_info["PortsClosed"] = ""
        item_info["PortsFiltered"] = ""

        if item['device_type'] == "Workstation":
            item_info["PortsOpen"] = "22 53 80 139 443 445"
        elif item['device_type'] == "Firewall":
            item_info["PortsOpen"] = "22 53 80 123 389 443"
        elif item['device_type'] in ["Switch", "DomainController"]:
            item_info["PortsOpen"] = "22 53 80 88 135 139 389 443 445 464" 
        else:
            item_info["PortsOpen"] = "22 53 80 443" 
        # firewall "22 53 80 123 389 443"
        # DC "22 53 80 88 135 139 389 443 445 464" 
        # workstation "22 53 80 139 443 445"
        example_data.append(item_info)

    return example_data

def get_answer_defaults(prob_type: str) -> dict:
    portscan_defaults = {
        'sudoAnswer': ['sudo'],
        'nmapAnswer': ['nmap'],
        'scanAnswer': ['-sS','-sT',''],
        'pFlagAnswer': ['-p','-pT'],
        'outputAnswer': ['-oN',''],
        'pingAnswer' : ['-Pn',''],
    }
    
    pingscan_defaults = {
        'sudoAnswer': ['sudo'],
        'nmapAnswer': ['nmap'],
        'scanAnswer': ['-sn','-PE',''],
        'portsAnswer': [''],
        'pRangeAnswer': [''],
        'pFlagAnswer': [''],
        'outputAnswer': ['-oN',''],
        'pingAnswer' : [''],
    }

    if prob_type in ["Bad Ports", "Identify Services"]:
        portscan = True
    elif prob_type in ["Rogue Workstations", "Unresponsive Workstations"]:
        portscan = False
    else:
        raise NameError("Problem type not found")
    return portscan_defaults if portscan else pingscan_defaults

def generate_answers(prob_type: str, example_data: list[dict], cidr_blocks) -> dict:
    answers = get_answer_defaults(prob_type)

    # pRangeAnswer = ['6881-6889', '6881,6882,6883,6884,6885,6886,6887,6888,6889']
    # answers["pRangeAnswer"] = pRangeAnswer

    # answers['portsAnswer'] = [item for portRange in pRangeAnswer for item in [f'-p {portRange}', f'-pT {portRange}']]
    answers["portsAnswer"] = ['-p 6881-6889']
    # Scan the relevant cidr blocks, or in this case, all of them
    answers["ipAnswer"] =  [str(block) for block in cidr_blocks] 
    # answers["ipAnswer"] =  generate_all_nmap_options(cidr_blocks)
    

    # Now to actually make the answers there
    # for random.randint(0,1)
    # global leftAnswer = ['172.16.31.102'];
    # global rightAnswer = ['3'];

    return answers

def get_problem_defaults(prob_type: str) -> dict:
    return {}
def gen_problem_file(prob_type: str, items: list) -> list:
    content = get_problem_defaults(prob_type)
    content['probtxt'] = "We have received a DMCA complaint that someone is sharing copyrighted material from our corporate network via bittorrent. Conduct a scan with nmap to find out which workstation is responsible.    ( Bittorrent is known to use TCP ports in the range 6881 – 6889 )"
    content["imgAddress"]
    return []

def dict_to_nools_value(value):
    """Convert Python values to nools-compatible format"""
    if isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, list):
        return json.dumps(value)
    elif isinstance(value, dict):
        return json.dumps(value)
    else:
        return str(value)

def generate_nools_file(data_dict, output_file, imports=None):
    if imports is None:
        imports = [
            "productionRules.nools",
            "SkillDefinitions.nools"
        ]
    
    with open(output_file, 'w') as f:
        # Write imports
        for imp in imports:
            f.write(f'import("{imp}");\n')
        
        # Write globals
        for key, value in data_dict.items():
            nools_value = dict_to_nools_value(value)
            f.write(f'global {key} = {nools_value};\n')

# Usage
your_data = {
    'probType': "Bad Ports",
    'fixLeft': False,
    'oneColumn': False,
    'probtxt': "We have received a DMCA complaint...",
    'imgAdress': "Assets/nmap.png",
    'title': "Tutor2: NMAP problem 1",
    'sudoAnswer': ['sudo'],
    'nmapAnswer': ['nmap'],
    'exampledata': [
        {"IP": "172.16.0.1", "Latency": "0.062", "PortsOpen": "22 53 80 443"},
        # ... more data
    ]
}



if __name__ == "__main__":
    # Pipeline: Generate # number of CIDR blocks to match # of subnets
    # Generate sub CIDR blocks for sections of the subnet
    # Generate Configuration of Network (How many computers, of what type)
    # Generate Connections
    # Generate Network
    # Generate Network Map
    # Generate Example Data
    # Generate Answers
    # Generate Problem File

    prob_type = "Bad Ports"
    cidr_blocks = generate_random_cidrs(subnets= 1, neighbors=True)
    print("Cidr:", cidr_blocks)

    config, connections = generate_network_config("Bad Ports", cidr_blocks)
    print("Configuration: ", config)
    print("Connecions: ", connections)

    print("Generating Network")
    network = generate_network(config, connections, "example_network")

    print("Generating network map")
    nmap = network.generate_map('OutputImage')

    print("Generating Example Data")
    example_data = generate_example_data(prob_type, network.all_ips)
    print(example_data)

    # Generate problem file

    # generate_nools_file(your_data, "output.nools")

