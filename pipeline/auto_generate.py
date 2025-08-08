from netaddr import IPNetwork
from typing import Optional, List, Dict, Any
import argparse
import random
import json
from network import Network
from problem import Problem, BadPorts, IdentifyServices, RogueWorkstations, UnresponsiveWorkstations

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


# def generate_network_config(problem: Problem, cidr_blocks: list['IPNetwork']) -> list:
#     """
#     Generate a list of CIDR blocks in a private range.

#     Args:
#         problem_type (str): What type of problem the network is for (e.g. "Bad Ports")
#         cidr_blocks (list['IPNetwork']): CIDR blocks for each subnet in the network

#     Returns:
#         tuple[list, dict]: list of dictionaries of devices in the network, and dictionary of connections between these devices
#     """
#     internet = problem.get_baseline_dict(item_type="device", device_type="Internet", name="Internet")
#     router = problem.get_baseline_dict(item_type="device", device_type="Router", name="BorderRouter")
#     user = problem.get_baseline_dict(item_type="device", device_type="User", name="UserLocation", display_name="You are connected here")
#     config = [
#         internet,
#         router,
#         user
#     ]
#     internet["connections"] = [("BorderRouter", "child", (' 128.237.3.102 ',""))]

#     config = problem.gen_config()
#     return config


    
def generate_network(items: list) -> 'Network':
    """
    Generates a dictionary graph representation of the network, where nodes that are connected by an edge in the map are neighbors

    Args:
        items (list[dict]): A list of items in the network
        connections (dict): Collection of one way connections of devices on the network
    Returns:
        dict: Dictionary representation of network map
    """
    map_rep = Network("ExampleNetwork", x_spacing= .5, y_spacing= .3333, internal_spacing=.25)
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

# def get_answer_defaults(prob_type: str) -> dict:
#     portscan_defaults = {
#         'sudoAnswer': ['sudo'],
#         'nmapAnswer': ['nmap'],
#         'scanAnswer': ['-sS','-sT',''],
#         'pFlagAnswer': ['-p','-pT'],
#         'outputAnswer': ['-oN',''],
#         'pingAnswer' : ['-Pn',''],
#     }
    
#     pingscan_defaults = {
#         'sudoAnswer': ['sudo'],
#         'nmapAnswer': ['nmap'],
#         'scanAnswer': ['-sn','-PE',''],
#         'portsAnswer': [''],
#         'pRangeAnswer': [''],
#         'pFlagAnswer': [''],
#         'outputAnswer': ['-oN',''],
#         'pingAnswer' : [''],
#     }

#     if prob_type in ["Bad Ports", "Identify Services"]:
#         portscan = True
#     elif prob_type in ["Rogue Workstations", "Unresponsive Workstations"]:
#         portscan = False
#     else:
#         raise NameError("Problem type not found")
#     return portscan_defaults if portscan else pingscan_defaults

# def generate_answers(prob_type: str, network: 'Network', cidr_blocks) -> dict:
#     answers = get_answer_defaults(prob_type)
    
#     if prob_type == "Bad Ports":
#         answers["portsAnswer"] = ['-p 6881-6889']
#         # Scan the relevant cidr blocks, or in this case, all of them
#         answers["ipAnswer"] =  [str(block) for block in cidr_blocks] 
#         # answers["ipAnswer"] =  generate_all_nmap_options(cidr_blocks)
#         workstations = network.workstations
#         ws_count:int = len(workstations)
#         bad_ws = random.randint(1, ws_count)
#         shuffled_ws = random.sample(workstations, ws_count)
#         left_answer = []
#         right_answer = []
#         for ws in shuffled_ws[:bad_ws]:
#             ws.properties["PortsOpen"] += " 6884"
#             left_answer.append(ws.ip)
#             right_answer.append(ws.display_name.split(" ")[2])
#     elif prob_type == "Identify Services":
#         answers["portsAnswer"] = ['-p 80,443,25,465,587,2525,53']
#         answers["ipAnswer"] =  [str(block) for block in cidr_blocks]
#         servers = network.servers
#         portsOpen = {
#             "Web Server": "22 53 80 443",
#             "Mail Server": "25 465 587 2525",
#             "DNS Server": "53"
#         }
#         # Random ordering of servers so that the first one isn't always the Web Server
#         left_answer = list(portsOpen.keys())
#         right_answer = []
#         for server, portOpen in zip(random.sample(servers, len(servers)), portsOpen.values()):
#             server.properties["PortsOpen"] = portOpen
#             right_answer.append(server.ip)
    
#     answers["leftAnswer"] = left_answer
#     answers["rightAnswer"] = right_answer

#     return answers

# def generate_example_data(prob_type: str, network: "Network") -> list[dict[str, str]]:
#     example_data = []

#     for item in network.items.values():
#         if item.type == "device":
#             if item.ip:
#                 example_data.append({
#                     "IP": item.ip,
#                     "Latency": item.properties["Latency"],
#                     "PortsClosed": item.properties["PortsClosed"],
#                     "PortsFiltered": item.properties["PortsFiltered"],
#                     "PortsOpen": item.properties["PortsOpen"]
#                 })

#             for neighbor, (hier, ips) in item.connections.items():
                
#                 if len(ips) > 0 and ips[0] != "":
#                     example_data.append({
#                         'IP': ips[0],
#                         "Latency": item.properties["Latency"],
#                         "PortsClosed": item.properties["PortsClosed"],
#                         "PortsFiltered": item.properties["PortsFiltered"],
#                         "PortsOpen": item.properties["PortsOpen"]
#                     })

#                 if len(ips) > 1 and ips[1] != "":
#                     example_data.append({
#                         'IP': ips[1],
#                         "Latency": neighbor.properties["Latency"],
#                         "PortsClosed": neighbor.properties["PortsClosed"],
#                         "PortsFiltered": neighbor.properties["PortsFiltered"],
#                         "PortsOpen": neighbor.properties["PortsOpen"]
#                     }) 

#     return example_data

# def get_problem_defaults(prob_type: str, prob_number: int) -> dict:
#     if prob_type == "Bad Ports":
#         defaults = {
#             'probType': "Bad Ports",
#             'fixLeft': False,
#             'oneColumn': False,
#             'probtxt': "We have received a DMCA complaint that someone is sharing copyrighted material from our corporate network via bittorrent. Conduct a scan with nmap to find out which workstation is responsible.   ( Bittorrent is known to use TCP ports in the range 6881 - 6889 )",
#             'title': f"Tutor: NMAP problem {prob_number}",
#             'opQuestion': 'Based on the output, which workstation is responsible?',
#             'leftTitle': 'IP Address',
#             'rightTitle': 'Workstation Number'
#         }
#     elif prob_type == "Identify Services":
#         defaults = {
#             'probType': "Identify Services",
#             'fixLeft': True,
#             'oneColumn': False,
#             'probtxt': "The services section of our DMZ network should contain a web server hosting both secure and insecure web connections (HTTP on TCP port 80 and HTTPS on TCP port 443), a mail server (providing SMTP over TCP ports 25, 465, 587 and 2525), and a DNS server (providing DNS lookup over TCP port 53). All other services are prohibited on this network segment. Using nmap, identify which server is configured at which IP address. Scan only the services portion of the DMZ network.FOR THE LAST QUESTION, PLEASE PRESS ENTER EVEN IF THE FIELD IS PREFILLED. THANK YOU.",
#             'title': f"Tutor: NMAP problem {prob_number}",
#             'opQuestion': 'Based on the output, which workstation is responsible?',
#             'leftTitle': 'Server',
#             'rightTitle': 'IP Address'
#         }
#     elif prob_type == "Rogue Workstations":
#         defaults = {
#             'probType': "Rogue Workstations",
#             'fixLeft': False,
#             'oneColumn': True,
#             'probtxt': "Scan both the office network and the entire DMZ with one nmap command. Identify any unaccounted for machines on our corporate networks. The firewalls are configured to allow ICMP echo requests through.",
#             'title': f"Tutor: NMAP problem {prob_number}",
#             'opQuestion': 'Based on the output, list any rogue workstation IPs below:',
#             'leftTitle': 'IP Address',
#             'rightTitle': ''
#         }
#     elif prob_type == "Unresponsive Workstations":
#         defaults = {
#             'probType': "Unresponsive Workstations",
#             'fixLeft': False,
#             'oneColumn': False,
#             'probtxt': "Due to a bad update from a vendor, some of our systems are stuck in a boot loop and have become unresponsive. Scan the corporate network using a single nmap command and identify any systems that are affected so that technicans can be dispatched to roll back the update manually. The firewalls are configured to allow ICMP echo requests through.",
#             'title': f"Tutor: NMAP problem {prob_number}",
#             'opQuestion': 'Based on the output, list any unresponsive workstation IPs below:',
#             'leftTitle': 'IP Address',
#             'rightTitle': 'Workstation Name'
#         }
#     else:
#         raise ValueError(f"Problem Type: {prob_type} is not a currently accepted problem type")
#     return defaults

# def gen_problem_dict(prob_type: str, file_name: str, answers: dict, example_data: list, prob_number: int) -> dict:
#     content = get_problem_defaults(prob_type, prob_number)
#     content["imgAddress"] = "Assets/" + file_name
#     content.update(answers)
#     content["exampledata"] = example_data
#     return content

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

def pipeline(prob_type, **kwargs):
    # subnet: [(number of servers, ports open, number of users, ports open, whether theres a firewall), ...]
    prob_types = {
        "Bad Ports": BadPorts(),
        "Identify Services": IdentifyServices(),
        "Rogue Workstations": RogueWorkstations(),
        "Unresponsive Workstations": UnresponsiveWorkstations()
    }
    try:
        problem: 'Problem' = prob_types[prob_type]
    except KeyError:
        print(f"Error: problem type {prob_type} is not currently an accepted type.Available problem types are {prob_types.keys()}")
        return
    
    subnets = kwargs.get("subnets", 1)
    neighbors = kwargs.get('neighbors', True)
    cidr_blocks = generate_random_cidrs(subnets, neighbors)
    print("Cidr:", cidr_blocks)

    config = problem.gen_config(cidr_blocks)
    print(config)
    print("Generating Network")
    network = generate_network(config)
    print("Generating network map")
    nmap = network.generate_map('Problem6')
    # network.all_positions()
    answers = problem.generate_answers(network, cidr_blocks)
    # # answers = generate_answers(prob_type, network, cidr_blocks)
    print("Answers: ", answers)
    # # example_data = generate_example_data(prob_type, network)
    # example_data = problem.generate_example_data(network)
    # print("Example Data: ", example_data)

    # # print("Generating Problem Dictionary")
    # problem_dict = problem.gen_problem_dict( nmap, answers, example_data, 7)
    # print(problem_dict)

    # generate_nools_file(problem_dict, "problem7.nools")


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--prob_type", type=str, required=True)
    parser.add_argument("--subnets", type=int, required=True)

    args = parser.parse_args()
    pipeline(prob_type=args.prob_type, subnets=args.subnets)
