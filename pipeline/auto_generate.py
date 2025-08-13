from netaddr import IPNetwork, IPAddress
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

def dict_to_nools_value(value):
    """Convert Python values to nools-compatible format"""
    if isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, list):
        items = [dict_to_nools_value(item) for item in value]
        return "[" + ", ".join(items) + "]"
    elif isinstance(value, dict):
        items = []
        for k, v in value.items():
            nools_val = dict_to_nools_value(v)
            items.append(f"{k}: {nools_val}")  # No quotes around key
        return "{" + ", ".join(items) + "}"
    else:
        return str(value)

def generate_nools_file(data_dict, output_file, imports=None):
    if imports is None:
        imports = [
            "productionRules-initialHint.nools",
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

def pipeline(prob_type: str, **kwargs):
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
    
    subnets: int = kwargs.get("subnets", 1)
    neighbors = kwargs.get('neighbors', True)
    cidr_blocks = generate_random_cidrs(subnets, neighbors)
    print("Cidr Blocks:", cidr_blocks)

    config = problem.gen_config(cidr_blocks)
    print(config)
    print("Generating Network")
    network = generate_network(config)
    print("Generating network map")
    nmap = network.generate_map(''.join(prob_type.split()) + '_' + str(subnets))
    # network.all_positions()
    answers = problem.generate_answers(network, cidr_blocks)
    # # answers = generate_answers(prob_type, network, cidr_blocks)
    print("Answers: ", answers)
    # # example_data = generate_example_data(prob_type, network)
    example_data = problem.generate_example_data(network)
    print("Example Data: ", example_data)

    # print("Generating Problem Dictionary")
    problem_dict = problem.gen_problem_dict( nmap, answers, example_data, 7)
    print(problem_dict)

    generate_nools_file(problem_dict, f"{''.join(prob_type.split()) + '_' + str(subnets)}.nools")


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

    # Still need to:
        # DONE Add blob about DMZ services limited to range
        # DONE Make ip addresses larger in image
        # Abstract everything to problem class
        # Abstract gen config function for even more generalizability
        # Variable distances for different
        # DONE Make sure number of answers is <= number of answer blanks available
        # Make sure server and ports match
        # DONE Services vs Workstations 
        # DONE Upload Example File to CTAT
