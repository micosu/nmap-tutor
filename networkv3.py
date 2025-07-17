import pygraphviz as pgv
import math
from typing import Dict, List, Tuple, Optional

class NetworkDiagramGenerator:
    def __init__(self):
        self.x_spacing = 0.75
        self.y_spacing = 0.5
        self.internal_spacing = 0.25
        self.cluster_padding = 0.3
        
    def create_network_diagram(self, network_config: Dict) -> pgv.AGraph:
        """
        Create a network diagram based on configuration
        
        network_config format:
        {
            'internet': {'label': 'Internet', 'ip': '128.237.3.102'},
            'border_routers': [{'label': 'Border Router', 'ip': '10.2.3.1'}],
            'firewalls': [
                {'label': 'Firewall 1', 'ip': '10.2.3.2'},
                {'label': 'Firewall 2', 'ip': '10.2.4.4'}
            ],
            'networks': [
                {
                    'name': 'DMZ',
                    'subnet': '10.2.3.0/24',
                    'servers': [
                        {'label': 'Server 1', 'ip': '10.2.3.21'},
                        {'label': 'Server 2', 'ip': '10.2.3.22'}
                    ],
                    'clients': [
                        {'label': 'Kiosk Computer', 'ip': '10.2.3.50'},
                        {'label': 'Digital Signage', 'ip': '10.2.3.51'}
                    ]
                },
                {
                    'name': 'Office',
                    'subnet': '10.2.4.0/24',
                    'servers': [
                        {'label': 'Domain Controller', 'ip': '10.2.4.20'}
                    ],
                    'clients': [
                        {'label': 'User Workstation 1', 'ip': '10.2.4.50'},
                        {'label': 'User Workstation 2', 'ip': '10.2.4.51'}
                    ]
                }
            ],
            'connections': [
                {'from': 'internet', 'to': 'border_router_0', 'label': '128.237.3.102'},
                {'from': 'border_router_0', 'to': 'firewall_0', 'head_label': '10.2.3.2', 'tail_label': '10.2.3.5'},
                # ... more connections
            ]
        }
        """
        
        nmap = pgv.AGraph(directed=False, strict=False)
        
        # Set graph attributes
        nmap.graph_attr.update({
            'compound': 'true',
            'splines': 'polyline',
            'bgcolor': 'white',
            'fontname': 'Arial',
            'overlap': 'false'
        })
        
        nmap.node_attr.update({
            'fontname': 'Arial',
            'fontsize': '14'
        })
        
        # Calculate layout positions
        positions = self._calculate_positions(network_config)
        
        # Create nodes
        self._create_nodes(nmap, network_config, positions)
        
        # Create connections
        self._create_connections(nmap, network_config)
        
        # Use neato layout with absolute positioning
        nmap.layout(prog='neato')
        
        return nmap
    
    def _calculate_positions(self, config: Dict) -> Dict[str, Tuple[float, float]]:
        """Calculate positions for all nodes to avoid collisions and maintain balance"""
        positions = {}
        
        # Internet at top center
        positions['internet'] = (0, self.y_spacing)
        
        # Border routers in middle row, centered
        border_routers = config.get('border_routers', [])
        if border_routers:
            for i, router in enumerate(border_routers):
                x = (i - len(border_routers)/2 + 0.5) * self.x_spacing
                positions[f'border_router_{i}'] = (x, 0)
        
        # Firewalls distributed horizontally in middle row
        firewalls = config.get('firewalls', [])
        if firewalls:
            # Calculate balanced distribution
            total_width = (len(firewalls) - 1) * self.x_spacing
            start_x = -total_width / 2
            
            for i, firewall in enumerate(firewalls):
                x = start_x + i * self.x_spacing
                positions[f'firewall_{i}'] = (x, 0)
        
        # Networks positioned below firewalls
        networks = config.get('networks', [])
        if networks:
            # Distribute networks under firewalls
            for net_idx, network in enumerate(networks):
                # Calculate network center position
                if len(firewalls) > net_idx:
                    base_x = positions[f'firewall_{net_idx}'][0]
                else:
                    # If more networks than firewalls, distribute evenly
                    base_x = (net_idx - len(networks)/2 + 0.5) * self.x_spacing * 2
                
                # Position servers
                servers = network.get('servers', [])
                if servers:
                    server_start_x = base_x - (len(servers) - 1) * self.internal_spacing / 2
                    for i, server in enumerate(servers):
                        x = server_start_x + i * self.internal_spacing
                        positions[f'network_{net_idx}_server_{i}'] = (x, 0)
                
                # Position clients below servers
                clients = network.get('clients', [])
                if clients:
                    client_start_x = base_x - (len(clients) - 1) * self.internal_spacing / 2
                    for i, client in enumerate(clients):
                        x = client_start_x + i * self.internal_spacing
                        positions[f'network_{net_idx}_client_{i}'] = (x, -self.y_spacing)
                
                # Position network label
                positions[f'network_{net_idx}_label'] = (base_x, 0.2)
        
        return positions
    
    def _create_nodes(self, nmap: pgv.AGraph, config: Dict, positions: Dict):
        """Create all nodes with calculated positions"""
        
        # Internet node
        if 'internet' in config:
            internet = config['internet']
            pos = positions['internet']
            nmap.add_node('internet',
                         label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                                    <TR><TD><FONT POINT-SIZE="30">☁</FONT></TD></TR>
                                    <TR><TD>{internet['label']}</TD></TR>
                                  </TABLE>>''',
                         shape='ellipse',
                         style='filled',
                         fillcolor='lightblue',
                         width='1.5',
                         pos=f'{pos[0]},{pos[1]}!')
        
        # Border routers
        border_routers = config.get('border_routers', [])
        for i, router in enumerate(border_routers):
            pos = positions[f'border_router_{i}']
            nmap.add_node(f'border_router_{i}',
                         label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                                    <TR><TD><FONT POINT-SIZE="30">📡</FONT></TD></TR>
                                    <TR><TD>{router['label']}</TD></TR>
                                  </TABLE>>''',
                         shape='cylinder',
                         style='filled',
                         fillcolor='lightblue',
                         width='1.5',
                         pos=f'{pos[0]},{pos[1]}!')
        
        # Firewalls
        firewalls = config.get('firewalls', [])
        for i, firewall in enumerate(firewalls):
            pos = positions[f'firewall_{i}']
            nmap.add_node(f'firewall_{i}',
                         label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                                    <TR><TD><FONT POINT-SIZE="30">🛡</FONT></TD></TR>
                                    <TR><TD>{firewall['label']}</TD></TR>
                                  </TABLE>>''',
                         shape='square',
                         style='filled',
                         fillcolor='lightgrey',
                         width='1.5',
                         pos=f'{pos[0]},{pos[1]}!')
        
        # Networks (servers and clients)
        networks = config.get('networks', [])
        for net_idx, network in enumerate(networks):
            # Create network cluster for servers
            if network.get('servers'):
                server_cluster = nmap.add_subgraph(name=f"cluster_network_{net_idx}_servers")
                server_cluster.graph_attr.update({
                    'style': 'filled,rounded',
                    'fillcolor': '#218dbb',
                    'fontsize': '12',
                })
                
                # Add servers to cluster
                for i, server in enumerate(network['servers']):
                    pos = positions[f'network_{net_idx}_server_{i}']
                    server_cluster.add_node(f'network_{net_idx}_server_{i}',
                                          label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                                                      <TR><TD>{server['label']}</TD></TR>
                                                      <TR><TD><FONT POINT-SIZE="30">🗄️</FONT></TD></TR>
                                                      <TR><TD><FONT POINT-SIZE="20">{server['ip']}</FONT></TD></TR>
                                                    </TABLE>>''',
                                          shape='none',
                                          width="0.5",
                                          fontcolor='white',
                                          pos=f'{pos[0]},{pos[1]}!')
                
                # Add network label
                label_pos = positions[f'network_{net_idx}_label']
                nmap.add_node(f'network_{net_idx}_label',
                             label=f'{network["name"]} - {network["subnet"]}',
                             shape='rectangle',
                             style='filled,rounded',
                             color='lightblue',
                             fontsize='12',
                             pos=f'{label_pos[0]},{label_pos[1]}!')
            
            # Create client nodes
            for i, client in enumerate(network.get('clients', [])):
                client_cluster = nmap.add_subgraph(name=f"cluster_network_{net_idx}_client_{i}")
                client_cluster.graph_attr.update({
                    'style': 'filled,rounded',
                    'fillcolor': 'lightblue',
                    'fontsize': '10',
                })
                
                pos = positions[f'network_{net_idx}_client_{i}']
                icon = '🖥' if 'workstation' in client['label'].lower() else '💻'
                
                client_cluster.add_node(f'network_{net_idx}_client_{i}',
                                      label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                                                  <TR><TD>{client['label']}</TD></TR>
                                                  <TR><TD><FONT POINT-SIZE="30">{icon}</FONT></TD></TR>
                                                  <TR><TD><FONT POINT-SIZE="15">{client['ip']}</FONT></TD></TR>
                                                </TABLE>>''',
                                      shape='none',
                                      width="0.5",
                                      fontcolor='black',
                                      pos=f'{pos[0]},{pos[1]}!')
    
    def _create_connections(self, nmap: pgv.AGraph, config: Dict):
        """Create connections between nodes"""
        connections = config.get('connections', [])
        
        for conn in connections:
            from_node = conn['from']
            to_node = conn['to']
            
            # Add edge with optional labels
            edge_attrs = {}
            if 'label' in conn:
                edge_attrs['label'] = conn['label']
            if 'head_label' in conn:
                edge_attrs['headlabel'] = f"  {conn['head_label']}  "
            if 'tail_label' in conn:
                edge_attrs['taillabel'] = f"  {conn['tail_label']}  "
            
            nmap.add_edge(from_node, to_node, **edge_attrs)


# Example usage
def create_example_network():
    """Create an example network configuration"""
    config = {
        'internet': {'label': 'Internet', 'ip': '128.237.3.102'},
        'border_routers': [{'label': 'Border Router', 'ip': '10.2.3.1'}],
        'firewalls': [
            {'label': 'Firewall 1', 'ip': '10.2.3.2'},
            {'label': 'Firewall 2', 'ip': '10.2.4.4'}
        ],
        'networks': [
            {
                'name': 'DMZ',
                'subnet': '10.2.3.0/24',
                'servers': [
                    {'label': 'Server 1', 'ip': '10.2.3.21'},
                    {'label': 'Server 2', 'ip': '10.2.3.22'},
                    {'label': 'Server 3', 'ip': '10.2.3.23'}
                ],
                'clients': [
                    {'label': 'Kiosk Computer', 'ip': '10.2.3.50'},
                    {'label': 'Digital Signage', 'ip': '10.2.3.51'},
                    {'label': 'Vending Machine', 'ip': '10.2.3.52'}
                ]
            },
            {
                'name': 'Office',
                'subnet': '10.2.4.0/24',
                'servers': [
                    {'label': 'Domain Controller', 'ip': '10.2.4.20'}
                ],
                'clients': [
                    {'label': 'User Workstation 1', 'ip': '10.2.4.50'},
                    {'label': 'User Workstation 2', 'ip': '10.2.4.51'},
                    {'label': 'User Workstation 3', 'ip': '10.2.4.52'}
                ]
            }
        ],
        'connections': [
            {'from': 'internet', 'to': 'border_router_0', 'label': '128.237.3.102'},
            {'from': 'border_router_0', 'to': 'firewall_0', 'head_label': '10.2.3.2', 'tail_label': '10.2.3.5'},
            {'from': 'border_router_0', 'to': 'firewall_1', 'head_label': '10.2.4.4', 'tail_label': '10.2.4.2'},
            {'from': 'firewall_0', 'to': 'network_0_server_2', 'head_label': '10.2.3.7'},
            {'from': 'firewall_1', 'to': 'network_1_server_0', 'tail_label': '10.2.4.6'},
            {'from': 'network_0_server_1', 'to': 'network_0_client_0'},
            {'from': 'network_0_server_1', 'to': 'network_0_client_1'},
            {'from': 'network_0_server_1', 'to': 'network_0_client_2'},
            {'from': 'network_1_server_0', 'to': 'network_1_client_0'},
            {'from': 'network_1_server_0', 'to': 'network_1_client_1'},
            {'from': 'network_1_server_0', 'to': 'network_1_client_2'}
        ]
    }
    
    generator = NetworkDiagramGenerator()
    diagram = generator.create_network_diagram(config)
    diagram.draw('automated_network_diagram.png', format='png')
    print("Automated network diagram created!")
    
    return diagram

# Create example with different topology (4 firewalls)
def create_balanced_network():
    """Create a network with 4 firewalls to demonstrate balancing"""
    config = {
        'internet': {'label': 'Internet', 'ip': '128.237.3.102'},
        'border_routers': [{'label': 'Border Router', 'ip': '10.2.3.1'}],
        'firewalls': [
            {'label': 'Firewall 1', 'ip': '10.2.3.2'},
            {'label': 'Firewall 2', 'ip': '10.2.4.4'},
            {'label': 'Firewall 3', 'ip': '10.2.5.2'},
            {'label': 'Firewall 4', 'ip': '10.2.6.4'}
        ],
        'networks': [
            {
                'name': 'DMZ',
                'subnet': '10.2.3.0/24',
                'servers': [
                    {'label': 'Web Server', 'ip': '10.2.3.21'},
                    {'label': 'DB Server', 'ip': '10.2.3.22'}
                ],
                'clients': [
                    {'label': 'Kiosk', 'ip': '10.2.3.50'}
                ]
            },
            {
                'name': 'Office',
                'subnet': '10.2.4.0/24',
                'servers': [
                    {'label': 'Domain Controller', 'ip': '10.2.4.20'}
                ],
                'clients': [
                    {'label': 'Workstation 1', 'ip': '10.2.4.50'},
                    {'label': 'Workstation 2', 'ip': '10.2.4.51'}
                ]
            },
            {
                'name': 'Dev',
                'subnet': '10.2.5.0/24',
                'servers': [
                    {'label': 'Dev Server', 'ip': '10.2.5.21'}
                ],
                'clients': [
                    {'label': 'Dev Machine', 'ip': '10.2.5.50'}
                ]
            },
            {
                'name': 'Guest',
                'subnet': '10.2.6.0/24',
                'servers': [
                    {'label': 'Guest Portal', 'ip': '10.2.6.21'}
                ],
                'clients': [
                    {'label': 'Guest WiFi', 'ip': '10.2.6.50'}
                ]
            }
        ],
        'connections': [
            {'from': 'internet', 'to': 'border_router_0'},
            {'from': 'border_router_0', 'to': 'firewall_0'},
            {'from': 'border_router_0', 'to': 'firewall_1'},
            {'from': 'border_router_0', 'to': 'firewall_2'},
            {'from': 'border_router_0', 'to': 'firewall_3'},
            {'from': 'firewall_0', 'to': 'network_0_server_0'},
            {'from': 'firewall_1', 'to': 'network_1_server_0'},
            {'from': 'firewall_2', 'to': 'network_2_server_0'},
            {'from': 'firewall_3', 'to': 'network_3_server_0'}
        ]
    }
    
    generator = NetworkDiagramGenerator()
    diagram = generator.create_network_diagram(config)
    diagram.draw('balanced_network_diagram.png', format='png')
    print("Balanced network diagram with 4 firewalls created!")
    
    return diagram

if __name__ == "__main__":
    # Create the original network
    create_example_network()
    
    # Create a balanced network with 4 firewalls
    create_balanced_network()