import ipaddress
from itertools import combinations, product

def generate_all_nmap_options(cidr_blocks):
    """Generate ALL possible nmap input combinations"""
    networks = [ipaddress.IPv4Network(cidr, strict=False) for cidr in cidr_blocks]
    
    # Step 1: Generate all possible representations for individual networks
    individual_reps = {}
    for i, network in enumerate(networks):
        individual_reps[i] = generate_single_network_options(network, cidr_blocks[i])
    
    # Step 2: Generate all possible group combinations
    all_options = set()
    
    # For each possible grouping of the networks
    for group_size in range(1, len(networks) + 1):
        for group_indices in combinations(range(len(networks)), group_size):
            remaining_indices = [i for i in range(len(networks)) if i not in group_indices]
            
            # Generate group representations
            group_networks = [networks[i] for i in group_indices]
            group_reps = generate_group_options(group_networks, group_indices, cidr_blocks)
            
            # Generate individual representations for remaining networks
            remaining_reps = []
            for idx in remaining_indices:
                remaining_reps.append(individual_reps[idx])
            
            # Combine group with remaining individuals
            if remaining_reps:
                for group_rep in group_reps:
                    for combo in product(*remaining_reps):
                        parts = [group_rep] + list(combo)
                        all_options.add(' '.join(parts))
            else:
                # Just the group
                all_options.update(group_reps)
    
    # Step 3: Add the "all individual" combinations
    for combo in product(*individual_reps.values()):
        all_options.add(' '.join(combo))
    
    return sorted(list(all_options))

def generate_single_network_options(network, original_cidr):
    """Generate all possible ways to represent a single network"""
    options = []
    
    # 1. Original CIDR
    options.append(original_cidr)
    
    # 2. Full IP range
    network_ip = network.network_address
    broadcast_ip = network.broadcast_address
    options.append(f"{network_ip}-{broadcast_ip}")
    
    # 3. Short range (network_ip-last_octet)
    last_octet = int(str(broadcast_ip).split('.')[-1])
    options.append(f"{network_ip}-{last_octet}")
    
    # 4. Wildcard notation based on prefix
    # wildcard = generate_wildcard_for_prefix(network)
    # if wildcard:
    #     options.append(wildcard)
    
    return options

def generate_wildcard_for_prefix(network):
    """Generate wildcard notation for networks with even prefixes"""
    octets = str(network.network_address).split('.')
    
    if network.prefixlen == 8:      # /8: a.*.*.*
        return f"{octets[0]}.*.*.*"
    elif network.prefixlen == 12:   # /12: a.b.*.*  (but only if b is on 16-boundary)
        # Check if second octet is on a /12 boundary (multiples of 16)
        if int(octets[1]) % 16 == 0:
            return f"{octets[0]}.{octets[1]}.*.*"
    elif network.prefixlen == 16:   # /16: a.b.*.*
        return f"{octets[0]}.{octets[1]}.*.*"
    elif network.prefixlen == 24:   # /24: a.b.c.*
        return f"{octets[0]}.{octets[1]}.{octets[2]}.*"
    
    return None

def generate_group_options(group_networks, group_indices, original_cidrs):
    """Generate all possible ways to represent a group of networks"""
    if len(group_networks) == 1:
        return generate_single_network_options(group_networks[0], original_cidrs[group_indices[0]])
    
    options = []
    group_cidrs = [original_cidrs[i] for i in group_indices]
    
    # 1. Space-separated individual formats
    individual_combos = []
    for net, orig_cidr in zip(group_networks, group_cidrs):
        individual_combos.append(generate_single_network_options(net, orig_cidr))
    
    for combo in product(*individual_combos):
        options.append(' '.join(combo))
    
    # 2. Comma-separated CIDR
    options.append(','.join(group_cidrs))
    
    # 3. Octet range (if consecutive and same prefix)
    if are_networks_consecutive(group_networks):
        octet_range = generate_octet_range_for_networks(group_networks)
        if octet_range:
            options.append(octet_range)
    
    # 4. Summarized CIDR (if possible)
    if len(group_networks) > 1:
        try:
            summarized = list(ipaddress.summarize_address_range(
                group_networks[0].network_address,
                group_networks[-1].broadcast_address
            ))
            if len(summarized) == 1:
                options.append(str(summarized[0]))
        except:
            pass
    
    return list(set(options))

def are_networks_consecutive(networks):
    """Check if networks are consecutive"""
    if len(networks) < 2:
        return False
    
    # Must all have same prefix length
    if not all(net.prefixlen == networks[0].prefixlen for net in networks):
        return False
    
    # Sort by network address
    sorted_nets = sorted(networks, key=lambda x: x.network_address)
    
    # Check if consecutive
    for i in range(1, len(sorted_nets)):
        if not are_consecutive_subnets(sorted_nets[i-1], sorted_nets[i]):
            return False
    
    return True

def are_consecutive_subnets(net1, net2):
    """Check if two networks with same prefix are consecutive"""
    if net1.prefixlen != net2.prefixlen:
        return False
    
    # The next network should start where the previous one ends + 1
    expected_next = net1.broadcast_address + 1
    return net2.network_address == expected_next

def generate_octet_range_for_networks(networks):
    """Generate octet range for consecutive networks with even prefixes"""
    if not networks:
        return None
    
    # Must all have same prefix
    if not all(net.prefixlen == networks[0].prefixlen for net in networks):
        return None
    
    prefix_len = networks[0].prefixlen
    sorted_nets = sorted(networks, key=lambda x: x.network_address)
    first_addr = str(sorted_nets[0].network_address).split('.')
    last_addr = str(sorted_nets[-1].network_address).split('.')
    
    if prefix_len == 8:    # /8: vary first octet
        first_octet = int(first_addr[0])
        last_octet = int(last_addr[0])
        return f"{first_octet}-{last_octet}.0.0.0-255.255.255"
    
    elif prefix_len == 12:  # /12: vary second octet in chunks of 16
        first_second = int(first_addr[1])
        last_second = int(last_addr[1])
        return f"{first_addr[0]}.{first_second}-{last_second}.0.0-255.255"
    
    elif prefix_len == 16:  # /16: vary second octet
        first_second = int(first_addr[1])
        last_second = int(last_addr[1])
        return f"{first_addr[0]}.{first_second}-{last_second}.0.0-255.255"
    
    elif prefix_len == 24:  # /24: vary third octet
        first_third = int(first_addr[2])
        last_third = int(last_addr[2])
        return f"{first_addr[0]}.{first_addr[1]}.{first_third}-{last_third}.0-255"
    
    return None

if __name__ == "__main__":
    # Example usage
    cidrs = ['10.2.3.0/24', '10.2.4.0/24', '10.2.7.0/24']
    all_options = generate_all_nmap_options(cidrs)

    print(f"Generated {len(all_options)} total options:")
    for i, option in enumerate(all_options, 1):
        print(f"{i:2d}. nmap {option}")