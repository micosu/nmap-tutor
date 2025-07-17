from typing import Optional, List, Dict, Any
import pygraphviz as pgv

class NetworkError(Exception):
    pass

class NetworkItem:
    def __init__(self, name, ip):
        self.connections: List[tuple['NetworkItem', dict]] = []
        self.name = name
        self.ip = ip
        self.positioned = False

    def connect_to(self, other_device: 'NetworkItem', labels: tuple[str, str] = ("", ""), direction: str = "auto"):
        """Simple connection with direction hint"""
        self.connections.append((other_device, {"labels": labels, "direction": direction}))

    def get_neighbors(self) -> List['NetworkItem']:
        return [conn[0] for conn in self.connections]
    
    def add_to_map(self, network: 'Network', graph: 'pgv.AGraph', pos: tuple):
        pass

    def connector_node(self):
        return self

class NetworkDevice(NetworkItem):
    """Simplified network device with smart positioning"""

    DEVICE_DEFAULTS = {
        "Internet": {"symbol": "☁", "fillcolor": "lightblue", "fontcolor": "black", "shape": "ellipse", "style":"filled"},
        "Router": {"symbol": "📡", "fillcolor": "lightblue", "fontcolor": "black", "shape": "cylinder", "style":"filled"},
        "Switch": {"symbol": "🔀", "fillcolor": "lightblue", "fontcolor": "black", "shape": "box", "style":"filled"},
        "Controller": {"symbol": "🖥", "fillcolor": "lightgreen", "fontcolor": "black", "shape": "box", "style":"filled"},
        "Firewall": {"symbol": "🛡", "fillcolor": "lightgrey", "fontcolor": "black","shape": "square", "style":"filled"},
        "Server": {"symbol": "🗄️", "fillcolor": "green", "fontcolor": "white", "shape": "box", "style":"filled"},
        "Workstation": {"symbol": "💻", "fillcolor": "lightblue", "fontcolor": "black", "shape": "box", "style":"filled"},
        "User": {"symbol": "📍", "fillcolor": '#CCA4D3', "shape": "ellipse", "style": "filled", "fontcolor": "black"}
    }
    
    def __init__(self, name: str, device_type: str, ip: Optional[str] = None, display_name: Optional[str] = None, **kwargs):
        super().__init__(name, ip)
        self.device_type = device_type
        self.display_name = display_name or name
        
        defaults = self.DEVICE_DEFAULTS.get(device_type, {})

        self.symbol = kwargs.get('symbol', defaults.get('symbol', '🔘'))
        self.fillcolor = kwargs.get('fillcolor', defaults.get('fillcolor', 'lightgray'))
        self.fontcolor = kwargs.get('fontcolor', defaults.get('fontcolor', 'black'))
        self.shape = kwargs.get('shape', defaults.get('shape', 'box'))
        self.width = kwargs.get('width', '1.5')
        self.style= kwargs.get('style', defaults.get('style', 'filled'))
    
    def to_graphviz_label(self) -> str:
        """Generate GraphViz label"""
        if self.ip:
            return f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                         <TR><TD><FONT POINT-SIZE="30">{self.symbol}</FONT></TD></TR>
                         <TR><TD>{self.display_name}</TD></TR>
                         <TR><TD><FONT POINT-SIZE="10">{self.ip}</FONT></TD></TR>
                       </TABLE>>'''
        else:
            return f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                         <TR><TD><FONT POINT-SIZE="30">{self.symbol}</FONT></TD></TR>
                         <TR><TD>{self.display_name}</TD></TR>
                       </TABLE>>'''
    
    def add_to_map(self, network: 'Network', graph: 'pgv.AGraph', pos: tuple):
        """Add this device and its children to the map"""
        if self.positioned:
            return
            
        # Find a free position near the requested one
        final_pos = network.find_free_position(pos)
        
        print(f"Adding {self.name} at position {final_pos}")
        
        # Add this node
        graph.add_node(self.name,
                label=self.to_graphviz_label(),
                shape=self.shape,
                style=self.style,
                fillcolor=self.fillcolor,
                fontcolor=self.fontcolor,
                width=self.width,
                pos=f'{final_pos[0]},{final_pos[1]}!'
            )
        
        self.positioned = True
        network.positions[final_pos] = self
        
        # Position children using smart layout
        if self.connections:
            child_positions = self._calculate_child_positions(final_pos, network)
            
            for i, (connection, conn_data) in enumerate(self.connections):
                child_pos = child_positions[i]
                connection.add_to_map(network, graph, child_pos)
                
                # Add edge
                labels = conn_data["labels"]
                graph.add_edge(self.name, connection.connector_node().name, 
                              taillabel=labels[0], headlabel=labels[1])
    
    def _calculate_child_positions(self, parent_pos: tuple, network: 'Network') -> List[tuple]:
        """Smart positioning based on device type and number of children"""
        num_children = len(self.connections)
        x, y = parent_pos
        spacing_x = network.x_spacing
        spacing_y = network.y_spacing
        
        # Get direction hints
        directions = [conn[1]["direction"] for conn in self.connections]
        
        positions = []
        
        # Handle explicit directions first
        auto_count = 0
        for i, direction in enumerate(directions):
            if direction == "right":
                positions.append((x + spacing_x, y))
            elif direction == "left":
                positions.append((x - spacing_x, y))
            elif direction == "up":
                positions.append((x, y + spacing_y))
            elif direction == "down":
                positions.append((x, y - spacing_y))
            else:  # auto
                positions.append(None)  # Will fill in later
                auto_count += 1
        
        # Fill in auto positions based on device type and remaining space
        if auto_count > 0:
            auto_positions = self._get_auto_positions(parent_pos, auto_count, network)
            auto_index = 0
            for i, pos in enumerate(positions):
                if pos is None:
                    positions[i] = auto_positions[auto_index]
                    auto_index += 1
        
        return positions
    
    def _get_auto_positions(self, parent_pos: tuple, count: int, network: 'Network') -> List[tuple]:
        """Get automatic positions based on device type - using REAL network layout rules"""
        x, y = parent_pos
        spacing_x = network.x_spacing
        spacing_y = network.y_spacing
        
        # REAL positioning rules based on network topology
        if self.device_type == "Internet":
            # Internet always puts BorderRouter directly below at (0,0)
            return [(0, 0)]
                
        elif self.device_type == "Router" and self.name == "BorderRouter":
            # BorderRouter spreads firewalls horizontally on same level
            if count == 1:
                return [(x - spacing_x, y)]  # Single firewall goes left
            elif count == 2:
                return [(x - spacing_x, y), (x + spacing_x, y)]  # Left and right
            elif count == 3:
                # Three firewalls: left, right, and one below to avoid collision
                return [(x - spacing_x, y), (x + spacing_x, y), (x, y - spacing_y)]
            else:  # 4+ firewalls - spread in a wider arc
                positions = []
                # Use wider spacing to avoid collisions
                wide_spacing = spacing_x * 1.5
                start_offset = -(count-1) * wide_spacing / 2
                for i in range(count):
                    positions.append((x + start_offset + i * wide_spacing, y))
                return positions
                
        elif self.device_type == "Firewall":
            # Firewalls put their clusters/subnets below them
            positions = []
            for i in range(count):
                positions.append((x, y - spacing_y))
            return positions
            
        elif self.device_type in ["Switch", "Server"]:
            # Switches/Servers spread children below in a row
            if count == 1:
                return [(x, y - spacing_y)]
            else:
                positions = []
                # Center the row below the parent
                start_x = x - (count-1) * network.internal_spacing / 2
                for i in range(count):
                    positions.append((start_x + i * network.internal_spacing, y - spacing_y))
                return positions
            
        else:  # Default: single child below
            return [(x, y - spacing_y)]

class Cluster(NetworkItem):
    """Cluster of devices"""
    
    def __init__(self, nodes: list['NetworkDevice'], cluster_type: str, name: str, ip: Optional[str] = None, **kwargs):
        super().__init__(name, ip)
        self.nodes = nodes
        self.type = cluster_type
        self.style = kwargs.get('style', 'filled,rounded')
        self.fillcolor = kwargs.get('fillcolor', 'lightblue')
        self.fontsize = kwargs.get('fontsize', '12')
        self.fontcolor = kwargs.get('fontcolor', 'black')

    def get_nodes(self):
        return self.nodes
    
    def add_to_map(self, network: 'Network', graph: 'pgv.AGraph', pos: tuple):
        if self.positioned:
            return
            
        print(f"Adding cluster {self.name} at position {pos}")
        
        # Create subgraph for cluster
        subgraph = graph.add_subgraph(name=f'cluster_{self.name}')
        subgraph.graph_attr.update({
            'style': self.style,
            'fillcolor': self.fillcolor,
            'fontsize': self.fontsize,
            'label': self.name
        })
        
        # Position nodes within cluster
        for i, node in enumerate(self.nodes):
            node_pos = (pos[0] + i * network.internal_spacing, pos[1])
            node.add_to_map(network, subgraph, node_pos)
        
        self.positioned = True
        
        # Handle cluster connections
        if self.connections:
            child_positions = self._calculate_child_positions(pos, network)
            for i, (connection, conn_data) in enumerate(self.connections):
                child_pos = child_positions[i]
                connection.add_to_map(network, graph, child_pos)
                
                labels = conn_data["labels"]
                graph.add_edge(self.connector_node().name, connection.connector_node().name,
                              taillabel=labels[0], headlabel=labels[1])
    
    def _calculate_child_positions(self, parent_pos: tuple, network: 'Network') -> List[tuple]:
        """Simple positioning for cluster children"""
        x, y = parent_pos
        positions = []
        for i in range(len(self.connections)):
            if i == 0:
                positions.append((x + network.x_spacing, y))
            else:
                positions.append((x + network.x_spacing, y - i * network.y_spacing/2))
        return positions

    def connector_node(self):
        return self.nodes[0]

class Network:
    """Network container with smart positioning"""

    def __init__(self, name: str = "Network", x_spacing: float = 2.0, y_spacing: float = 1.5, internal_spacing: float = 0.5):
        self.name = name
        self.items: Dict[str, NetworkItem] = {}
        self.x_spacing = x_spacing
        self.y_spacing = y_spacing
        self.internal_spacing = internal_spacing
        self.positions: Dict[tuple, NetworkItem] = {}

    def add_item(self, item: NetworkItem) -> NetworkItem:
        """Add a device to the network"""
        if item.name in self.items:
            raise ValueError(f"Item '{item.name}' already exists")
        
        self.items[item.name] = item
        return item
    
    def get_item(self, name: str):
        return self.items[name]
    
    def find_free_position(self, preferred_pos: tuple) -> tuple:
        """Find the nearest free position to the preferred one"""
        if preferred_pos not in self.positions:
            return preferred_pos
        
        # Search in expanding squares around the preferred position
        for radius in range(1, 10):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) == radius or abs(dy) == radius:  # Only check perimeter
                        test_pos = (preferred_pos[0] + dx * 0.1, preferred_pos[1] + dy * 0.1)
                        if test_pos not in self.positions:
                            return test_pos
        
        # Fallback
        return (preferred_pos[0] + 0.5, preferred_pos[1] + 0.5)
    
    def generate_map(self, output_name: str = "network") -> str:
        """Generate the network map using proper network topology rules"""
        # Reset positioning
        for item in self.items.values():
            item.positioned = False
        self.positions.clear()
        
        # Create graph
        graph = pgv.AGraph(directed=False, strict=False)
        graph.graph_attr.update({
            'compound': 'true',
            'splines': 'polyline',
            'bgcolor': 'white',
            'fontname': 'Arial',
            'overlap': 'false'
        })
        graph.node_attr.update({
            'fontname': 'Arial',
            'fontsize': '14'
        })
        
        # FIXED positioning: Internet at top, then build down
        if "Internet" in self.items:
            internet = self.get_item("Internet")
            # Internet goes at top center
            internet.add_to_map(self, graph, (0, self.y_spacing))
        
        # Handle any unconnected items
        for item_name, item in self.items.items():
            if not item.positioned:
                # Find a good position for orphaned items
                item.add_to_map(self, graph, (3, 0))
        
        # Layout and save
        graph.layout(prog='neato')
        graph.draw(f"{output_name}.png", format='png')
        print(f"Network diagram saved as {output_name}.png")
        return f"{output_name}.png"

# Example with two firewalls like your beautiful diagram
if __name__ == "__main__":
    # Create devices
    internet = NetworkDevice(name="Internet", device_type="Internet")
    br = NetworkDevice(name="BorderRouter", device_type="Router", ip="172.16.0.1")
    ul = NetworkDevice(name="UserLocation", device_type="User", display_name="You are connected here")
    fw1 = NetworkDevice(name="Firewall1", device_type="Firewall", ip="172.16.0.2")
    fw2 = NetworkDevice(name="Firewall2", device_type="Firewall", ip="172.16.0.3")
    
    # DMZ Servers
    server1 = NetworkDevice(name="Server1", device_type="Server", ip="10.2.3.21")
    server2 = NetworkDevice(name="Server2", device_type="Server", ip="10.2.3.22") 
    server3 = NetworkDevice(name="Server3", device_type="Server", ip="10.2.3.23")
    
    # DMZ Services
    kiosk = NetworkDevice(name="Kiosk", device_type="Workstation", ip="10.2.3.50")
    signage = NetworkDevice(name="DigitalSignage", device_type="Workstation", ip="10.2.3.51")
    
    # Office devices
    dc = NetworkDevice(name="DomainController", device_type="Controller", ip="10.2.4.20")
    ws1 = NetworkDevice(name="Workstation1", device_type="Workstation", ip="10.2.4.50")
    ws2 = NetworkDevice(name="Workstation2", device_type="Workstation", ip="10.2.4.51")
    ws3 = NetworkDevice(name="Workstation3", device_type="Workstation", ip="10.2.4.52")
    
    # Create clusters
    dmz_cluster = Cluster([server1, server2, server3], "intermediate", "DMZ")
    office_cluster = Cluster([dc], "intermediate", "Office")
    
    # Create network
    network = Network("Enterprise Network", x_spacing=0.75, y_spacing=0.5, internal_spacing=0.25)
    
    # Add items
    for item in [internet, br, ul, fw1, fw2, dmz_cluster, office_cluster, 
                 kiosk, signage, ws1, ws2, ws3]:
        network.add_item(item)
    
    # Create connections following your diagram topology
    internet.connect_to(br, labels=('128.237.3.102', ""))
    
    # BorderRouter connects to BOTH firewalls (this will position them left/right)
    br.connect_to(fw1, labels=("10.2.3.5", "10.2.3.2"))
    br.connect_to(fw2, labels=("10.2.4.2", "10.2.4.4"))
    
    # Firewalls connect to their respective subnets
    fw1.connect_to(dmz_cluster, labels=("10.2.3.7", ""))
    fw2.connect_to(office_cluster, labels=("10.2.4.6", ""))
    
    # DMZ connections
    dmz_cluster.connect_to(ul, labels=("10.2.3.9", ""), direction="up")  # User location up and left
    server2.connect_to(kiosk, direction="down")
    server2.connect_to(signage, direction="down")
    
    # Office connections  
    dc.connect_to(ws1, direction="down")
    dc.connect_to(ws2, direction="down")
    dc.connect_to(ws3, direction="down")
    
    # Generate map
    network.generate_map("enterprise_network")