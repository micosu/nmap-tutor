from netaddr import IPNetwork
from typing import Optional, List, Dict, Any
import argparse
import random
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

def pipeline(prob_type: str, **kwargs):
    # subnet: [(number of servers, ports open, number of users, ports open, whether theres a firewall), ...]
    subnets: int = kwargs.get("subnets", 1)
    q_type: str = kwargs.get("q_type", "normal")
    neighbors = kwargs.get('neighbors', True)
    folder: str = kwargs.get("folder", "exampleFiles")
    print("folederrrrr: ", folder)
    images_folder: str = kwargs.get("images_folder", "images")
    cidr_blocks = generate_random_cidrs(subnets, neighbors)
    print("Cidr Blocks:", cidr_blocks)

    prob_types: dict[str, type['Problem']] = {
        "Bad Ports": BadPorts,
        "Identify Services": IdentifyServices,
        "Rogue Workstations": RogueWorkstations,
        "Unresponsive Workstations": UnresponsiveWorkstations
    }

    try:
        problem_class: type['Problem'] = prob_types[prob_type]
    except KeyError:
        print(f"Error: problem type {prob_type} is not currently an accepted type.Available problem types are {prob_types.keys()}")
        return
    problem = problem_class(cidr_blocks, subnets, q_type=q_type, folder=folder, images_folder=images_folder)
    config = problem.config
    print(config)
    print("Generating Network")
    network = problem.network

    print("Generating Map")
    problem.gen_map()

    answers = problem.gen_answers()
    print("Answers: ", answers)


    example_data = problem.gen_example_data()
    print("Example Data: ", example_data)

    # print("Generating Problem Dictionary")
    problem_dict = problem.set_problem_dict(prob_number=2)
    print(problem_dict)

    problem.gen_nools_file()
    print("Problem file Generated Successfully")


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
    parser.add_argument("--q_type", type=str, required=False, default="normal")
    parser.add_argument("--folder", type=str, required=False, default="exampleFiles")
    parser.add_argument("--image_folder", type=str, required=False, default="images")

    args = parser.parse_args()
    print(args)
    pipeline(prob_type=args.prob_type, subnets=args.subnets, q_type= args.q_type, folder=args.folder, image_folder=args.image_folder)
