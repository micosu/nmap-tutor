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


def get_baseline_dict(item_type, name, **kwargs) -> dict[str, Any]:
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
            'properties': {
                "Latency": str(round(random.uniform(0.01, 0.1), 3)),
                "PortsClosed": "",
                "PortsFiltered": "", 
            }
        })
        
        display_name = kwargs.get('display_name')
        if display_name:
            baseline["display_name"] = display_name
        if device_type == "Workstation":
            baseline['properties']["PortsOpen"] = "22 53 80 139 443 445"
        elif device_type == "Firewall":
            baseline['properties']["PortsOpen"] = "22 53 80 123 389 443"
        elif device_type in ["Switch", "DomainController"]:
            baseline['properties']["PortsOpen"] = "22 53 80 88 135 139 389 443 445 464" 
        else:
            baseline['properties']["PortsOpen"] = "22 53 80 443" 
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

def generate_network_config(problem_type: str, cidr_blocks: list['IPNetwork']) -> list:
    """
    Generate a list of CIDR blocks in a private range.

    Args:
        problem_type (str): What type of problem the network is for (e.g. "Bad Ports")
        cidr_blocks (list['IPNetwork']): CIDR blocks for each subnet in the network

    Returns:
        tuple[list, dict]: list of dictionaries of devices in the network, and dictionary of connections between these devices
    """
    internet = get_baseline_dict(item_type="device", device_type="Internet", name="Internet")
    router = get_baseline_dict(item_type="device", device_type="Router", name="BorderRouter")
    user = get_baseline_dict(item_type="device", device_type="User", name="UserLocation", display_name="You are connected here")
    config = [
        internet,
        router,
        user
    ]
    internet["connections"] = [("BorderRouter", "child", (' 128.237.3.102 ',""))]

    # connections: dict[str, list[tuple]] = {
    #     "Internet": [("BorderRouter", "child", (' 128.237.3.102 ',""))],
    # }
    has_user_loc = False
    
    for i in range(len(cidr_blocks)):
        net = cidr_blocks[i]
        firewall = get_baseline_dict(item_type="device", device_type="Firewall", name=f'Firewall{i}')
        switch = get_baseline_dict(item_type = "cluster", name=f'switch_cluster{i}', cluster_type='intermediate', 
                              nodes= [get_baseline_dict(item_type="device", name=f'Switch{i}', device_type= 'Switch')])
        office = get_baseline_dict(item_type = "cluster", name=f'Office{i}', cluster_type='intermediate', ip= str(net),
                              nodes= [get_baseline_dict(item_type="device", name= f'DomainController{i}', device_type="Controller", ip= f'{net[10]}', display_name= 'Domain Controller')])
        config = config + [
            firewall,
            switch,
            office
            ]
        
        router.setdefault("connections", []).append((f"Firewall{i}", "child", (f"  {net[1]}  ", f"  {net[3]}  ")))
        firewall["connections"] = [(f'switch_cluster{i}', "same", (f"  {net[5]}  ", ""))]
        # connections.setdefault("BorderRouter", []).append((f"Firewall{i}", "child", (f"  {net[1]}  ", f"  {net[3]}  ")))
        # connections[f'Firewall{i}'] = [(f'switch_cluster{i}', "same", (f"  {net[5]}  ", ""))]
        
        # connections[f'switch_cluster{i}'] = [(f'Office{i}', "above",)]
        switch["connections"] = [(f'Office{i}', "above", ("", ""))]
        if not has_user_loc:
            # connections[f'switch_cluster{i}'].append(("UserLocation", "same", ("", f"  {net[20]}  ", "")))
            switch["connections"].append(("UserLocation", "same", ("", f"  {net[20]}  ")))
            has_user_loc = True

        offset = random.randint(40, 100)
        for j in range(1,random.randint(3, 4)):
            ip_address = net[offset+j]
            workstation= get_baseline_dict(item_type= "cluster", name=f'ClusterWorkstation{i+j}', cluster_type='endpoint',
                              nodes= [get_baseline_dict(item_type='device', name=f'Workstation{i+j}', device_type="Workstation", ip=f'{ip_address}', display_name=f'User Workstation {i+j}')])
            config.append(workstation)
            switch["connections"].append(( f'ClusterWorkstation{i+j}', "child", ("","")))
            # connections.setdefault(f'switch_cluster{i}', []).append(( f'ClusterWorkstation{i+j}',))
        
    # return config, connections
    return config

# subnet: [(number of servers, ports open, number of users, ports open, whether theres a firewall), ...]
    
def generate_network(items: list) -> 'Network':
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
    connections = dict()
    for item in items:
        if "connections" in item:
            connections[item["name"]] = item["connections"]

    print("Connections: ", connections)
    map_rep.connect_items_from_config(connections)

    return map_rep
# exampledata = [{ IP: "172.16.0.1", Latency: "0.062", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 443" }, { IP: "172.16.0.2", Latency: "0.051", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 443" }, { IP: "172.16.0.3", Latency: "0.044", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 123 389 443" }, { IP: "172.16.5.5", Latency: "0.004", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 443" }, { IP: "172.16.9.10", Latency: "0.083", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 88 135 139 389 443 445 464" }, { IP: "172.16.31.100", Latency: "0.039", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 139 443 445" }, { IP: "172.16.31.101", Latency: "0.037", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 139 443 445" }, { IP: "172.16.31.102", Latency: "0.29", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 139 443 445 6886" }];
# IP Address
# Type of Computer (Firewall, Domain Controller, Border Router, Switch, UserLocation, User Workstation, etc)
# Location in the network (edges? neighbors? Clusters?)
# [{ IP: "172.16.0.1", Latency: "0.062", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 443" }, { IP: "172.16.0.2", Latency: "0.051", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 443" }, { IP: "172.16.0.3", Latency: "0.044", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 123 389 443" }, { IP: "172.16.5.5", Latency: "0.004", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 443" }, { IP: "172.16.9.10", Latency: "0.083", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 88 135 139 389 443 445 464" }, { IP: "172.16.31.100", Latency: "0.039", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 139 443 445" }, { IP: "172.16.31.101", Latency: "0.037", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 139 443 445" }, { IP: "172.16.31.102", Latency: "0.29", PortsClosed: "", PortsFiltered: "", PortsOpen: "22 53 80 139 443 445 6886" }];

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

def generate_answers(prob_type: str, network: 'Network', cidr_blocks) -> dict:
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
    workstations = network.workstations
    ws_count:int = len(workstations)
    bad_ws = random.randint(1, ws_count)
    shuffled_ws = random.sample(workstations, ws_count)
    left_answer = []
    right_answer = []
    for ws in shuffled_ws[:bad_ws]:
        ws.properties["PortsOpen"] += " 6884"
        left_answer.append(ws.ip)
        right_answer.append(ws.display_name.split(" ")[2])
    

    answers["leftAnswer"] = left_answer
    answers["rightAnswer"] = right_answer

    return answers

def generate_example_data(prob_type: str, network: "Network") -> list[dict[str, str]]:
    example_data = []

    for item in network.items.values():
        if item.type == "device":
            if item.ip:
                example_data.append({
                    "IP": item.ip,
                    "Latency": item.properties["Latency"],
                    "PortsClosed": item.properties["PortsClosed"],
                    "PortsFiltered": item.properties["PortsFiltered"],
                    "PortsOpen": item.properties["PortsOpen"]
                })

            for neighbor, (hier, ips) in item.connections.items():
                
                if len(ips) > 0 and ips[0] != "":
                    example_data.append({
                        'IP': ips[0],
                        "Latency": item.properties["Latency"],
                        "PortsClosed": item.properties["PortsClosed"],
                        "PortsFiltered": item.properties["PortsFiltered"],
                        "PortsOpen": item.properties["PortsOpen"]
                    })

                if len(ips) > 1 and ips[1] != "":
                    example_data.append({
                        'IP': ips[1],
                        "Latency": neighbor.properties["Latency"],
                        "PortsClosed": neighbor.properties["PortsClosed"],
                        "PortsFiltered": neighbor.properties["PortsFiltered"],
                        "PortsOpen": neighbor.properties["PortsOpen"]
                    }) 

    return example_data

def get_problem_defaults(prob_type: str) -> dict:
    i = 5
    if prob_type == "Bad Ports":
        defaults = {
            'probType': "Bad Ports",
            'fixLeft': False,
            'oneColumn': False,
            'probtxt': "We have received a DMCA complaint that someone is sharing copyrighted material from our corporate network via bittorrent. Conduct a scan with nmap to find out which workstation is responsible.   ( Bittorrent is known to use TCP ports in the range 6881 - 6889 )",
            'title': f"Tutor: NMAP problem {i}",
            'opQuestion': 'Based on the output, which workstation is responsible?',
            'leftTitle': 'IP Address',
            'rightTitle': 'Workstation Number'
        }
    return defaults
def gen_problem_dict(prob_type: str, file_name: str, answers: dict, example_data: list) -> dict:
    content = get_problem_defaults(prob_type)
    content["imgAddress"] = "Assets/" + file_name
    content.update(answers)
    content["exampledata"] = example_data
    return content

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
        f.write("\n")
        # Write globals
        for key, value in data_dict.items():
            nools_value = dict_to_nools_value(value)
            f.write(f'global {key} = {nools_value};\n')
            if key == "imgAddress" or key == "ipAnswer" or key == "rightAnswer":
                f.write("\n")




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

    # config, connections = generate_network_config("Bad Ports", cidr_blocks)
    config = generate_network_config("Bad Ports", cidr_blocks)
    print("Configuration: ", config)
    # print("Connecions: ", connections)

    print("Generating Network")
    network = generate_network(config)

    print("Generating network map")
    nmap = network.generate_map('Problem5')
    # 'imgAdress': "Assets/nmap.png",

    # Generate Answers
    answers = generate_answers("Bad Ports", network, cidr_blocks)
    print(answers)

    print("Generating Example Data")
    example_data = generate_example_data(prob_type, network)
    print(example_data)

    # Generate problem file
    print("Generating Problem Dictionary")
    problem = gen_problem_dict("Bad Ports", nmap, answers, example_data)
    print(problem)
    generate_nools_file(problem, "problem5.nools")

