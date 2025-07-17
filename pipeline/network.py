from typing import Optional, List, Dict, Any
import pygraphviz as pgv

class NetworkError(Exception):
    pass

def debug_before_after_layout(graph, stage=""):
    """Check node visual properties before and after layout"""
    print(f"\n=== {stage} ===")
    
    # Check actual rendered positions and sizes
    try:
        internet = graph.get_node('Internet')
        print(f"Internet - pos: {internet.attr.get('pos')}, width: {internet.attr.get('width')}")
        print(f"Internet - height: {internet.attr.get('height')}, shape: {internet.attr.get('shape')}")
        
        # Check if layout has added any new attributes
        all_attrs = dict(internet.attr)
        layout_attrs = {k:v for k,v in all_attrs.items() if k not in ['label', 'shape', 'style', 'fillcolor', 'fontcolor', 'width']}
        if layout_attrs:
            print(f"Layout-added attributes: {layout_attrs}")
            
    except Exception as e:
        print(f"Error getting node info: {e}")
    
    # Check graph-level attributes that affect rendering
    print(f"Graph bb: {graph.graph_attr.get('bb', 'Not set')}")
    print(f"Graph size: {graph.graph_attr.get('size', 'Not set')}")
    print(f"Graph dpi: {graph.graph_attr.get('dpi', 'Not set')}")

class NetworkItem:
    # If it is a central node (e.g. Internet), neighbors should be placed below it
    directions: dict[str, dict[int, List[tuple[float, float, str]]]] = {
        'right' : {
            0: [],
            1: [(1, 0, 'right')],
            2: [(1, -.5, 'right'), (1, .5, 'right')],
            3: [(1, -.5, 'right'), (1.5, 0, 'right'), (1, .5, 'right')],
        },
        'left' : {
            0: [],
            1: [(-1, 0, 'left')],
            2: [(-1, -.5, 'left'), (-1, .5, 'left')],
            3: [(-1, -.5, 'left'), (-1.5, 0, 'left'), (-1, .5, 'left')],
        },
        'down' : {
            0: [],
            1: [(0, -1, 'down')],
            2: [(-.5, -1, 'left'), (.5, -1, 'right')],
            3: [(1, -.5, 'right'), (1.5, 0, 'right'), (1, .5, 'right')],
        },
        'up' : {
            0: [],
            1: [(0, 1, 'up')],
            2: [(-.5, 1, 'left'), (.5, 1, 'right')],
            3: [(-.5, 1, 'right'), (0, 1, 'right'), (.5, 1, 'right')],
        }
    }
    offset = {
        0: [],
        1: [(0, -1, "down")], 
        2: [(-.5, -1, "left"), (.5, -1, "right")],
        3: [(-.5, -1, "left"), (0, -1, "down"), (.5, -1, "right")],
        4: [(-1, -1, "left"), (-.5, -1, "down"), (.5, -1, "down"), (1, -1, "right")],
    }


    def __init__(self, name, ip, device_type):
        self.connections: dict['NetworkItem', tuple[str, tuple[str, str]]] = {}
        self.name = name
        self.ip = ip
        self.device_type = device_type

    def connect_to(self, other_device: 'NetworkItem' , hierarchy:str = "child", labels: tuple[str, str] = ("", "")):
        """DRY way to create connections"""
        self.connections[other_device] = (hierarchy, labels)

    @property
    def neighbors(self) -> List['NetworkItem']:
        """Get all devices that share an edge"""
        return [neighbor for neighbor in self.connections]
    @property
    def above(self):
        return {neighbor: vals for neighbor,vals in self.connections.items() if self.connections[neighbor][0] == "above" }
    
    @property
    def same(self):
        return [neighbor for neighbor in self.connections if self.connections[neighbor][0] == "same" ]
    
    @property
    def children(self):
        return [neighbor for neighbor in self.connections if self.connections[neighbor][0] == "child" ]
    
    def add_to_map(self, network: 'Network', graph: 'pgv.AGraph', pos: tuple, dir: str ="right"):
        offset = self.offset[len(self.children)]
        dir_offset = self.directions[dir][len(self.same)]
        # print(f"Node {self.name} at position {pos} with connections: {self.connections}")

        for i, connection in enumerate(self.above):
            (hier, labels) = self.connections[connection]
            connection.add_to_map(network, graph, (pos[0] + 0 * network.x_spacing, pos[1] + 1 * network.y_spacing), "up")
            # graph.add_edge(self.connector_node.name, connection.connector_node.name, taillabel = labels[0], headlabel=labels[1])

        for i, connection in enumerate(self.same):
            (hier, labels) = self.connections[connection]
            connection.add_to_map(network, graph, (pos[0] + dir_offset[i][0] * network.x_spacing, pos[1] + dir_offset[i][1] * network.y_spacing), dir_offset[i][2])
            # graph.add_edge(self.connector_node.name, connection.connector_node.name, taillabel = labels[0], headlabel=labels[1])

        for i, connection in enumerate(self.children):
            (hier, labels) = self.connections[connection]
            connection.add_to_map(network, graph, (pos[0] + offset[i][0] * network.internal_spacing, pos[1] + offset[i][1] * network.y_spacing), offset[i][2])
            # graph.add_edge(self.connector_node.name, connection.connector_node.name, taillabel = labels[0], headlabel=labels[1])
    
    def add_edges(self, network: 'Network', graph: 'pgv.AGraph'):
        for connection in self.neighbors:
            (hier, labels) = self.connections[connection]
            if self.name not in ["Internet"]:
                # print(f"adding edge between {self.name} and {connection.name}")
                graph.add_edge(self.connector_node.name, connection.connector_node.name, taillabel = labels[0], headlabel=labels[1])
            connection.add_edges(network, graph)

        

    @property
    def connector_node(self):
        return self
    
    def position(self):
        pass

class NetworkDevice(NetworkItem):
    """Representation for individual nodes on our network and how they connect to each other"""
    offsets = {
        'Internet' : {
            0: [],
            1: [(0, -1, 'down')], 
            2: [(-1, 0, 'left'), (1, 0, 'right')],
            3: [(-1, 0, 'left'), (0, -1, 'down'), (1, 0, 'right')],
            4: [(-1, 0, 'left'), (-1, -1, 'left'), (1, 0, 'right'), (1, -1, 'right')]
        },
        'Router': {
            0: [],
            1: [(2, 0, 'right')], 
            2: [(-1, 0, 'left'), (1, 0, 'right')],
            3: [(-1, 0, 'left'), (0, -1, 'down'), (1, 0, 'right')],
            4: [(-1, .5, 'left'), (-1, -1, 'down'), (1, .5, 'right'), (2, -1, 'down')]
        },
        'right' : {
            0: [],
            1: [(1, 0, 'right')],
            2: [(1, -.5, 'right'), (1, .5, 'right')],
            3: [(1, -.5, 'right'), (1.5, 0, 'right'), (1, .5, 'right')],
        },
        'left' : {
            0: [],
            1: [(-1, 0, 'left')],
            2: [(-1, -.5, 'left'), (-1, .5, 'left')],
            3: [(-1, -.5, 'left'), (-1.5, 0, 'left'), (-1, .5, 'left')],
        },
        'Normal' :{
            0: [],
            1: [(0, -1, 'down')],
            2: [(-.5, -1, 'down'), (.5, -1, 'down')],
            3: [(-.5, -1, 'down'), (0, -1, 'down'), (.5, -1, 'down')],
        },
        'parent' : {
            0: [],
            1: [(0, 1, 'up')],
            2: [(-.5, 1, 'up'), (.5, 1, 'up')],
            3: [(-.5, 1, 'up'), (0, 1, 'up'), (.5, 1, 'up')],
        }
    }

    

    DEVICE_DEFAULTS = {
        "Internet": {"symbol": "☁", "fillcolor": "lightblue", "fontcolor": "black", "shape": "ellipse", "style":"filled", "offset": offsets['Internet']},
        "Router": {"symbol": "📡", "fillcolor": "lightblue", "fontcolor": "black", "shape": "cylinder", "offset": offsets["Router"]},
        "Switch": {"symbol": "🔀", "fillcolor": "none", "fontcolor": "white", "shape": 'none', "offset": offsets["Normal"]},
        "Controller": {"symbol": "🖥", "fillcolor": "none", "fontcolor": "white", "shape": 'none', "offset": offsets["Normal"]},
        "Firewall": {"symbol": "🛡", "fillcolor": "lightgrey", "fontcolor": "black","shape": "square", "style":"filled", "offset": offsets["Normal"]},
        "Server": {"symbol": "🗄️", "fillcolor": "green", "fontcolor": "white", "width": "1", "offset": offsets["Normal"]},
        "Workstation": {"symbol": "💻", "fillcolor": "lightblue", "fontcolor": "black", "offset": offsets["Normal"]},
        "User": {"symbol": "📍", "fillcolor": '#CCA4D3', "shape": "ellipse", "style": "filled", "offset": offsets["Normal"]}
    }
    
    def __init__(self, name: str, device_type: str, ip: Optional[str] = None, display_name: Optional[str] = None, **kwargs):
        super().__init__(name, ip, device_type)
        self.display_name = display_name or name
        
        defaults = self.DEVICE_DEFAULTS.get(device_type, {})

        self.symbol = kwargs.get('symbol', defaults.get('symbol', '🔘'))
        self.fillcolor = kwargs.get('fillcolor', defaults.get('fillcolor', 'lightgray'))
        self.fontcolor = kwargs.get('fontcolor', defaults.get('fontcolor', 'black'))
        self.shape = kwargs.get('shape', defaults.get('shape', 'box'))
        self.width = kwargs.get('width', defaults.get('width', '1'))
        self.style= kwargs.get('style', defaults.get('style', 'filled,rounded'))
        self.offset: dict[int, List[tuple[float, float, str]]] = kwargs.get('offset', defaults.get('offset', NetworkDevice.offsets["Normal"]))
        
        # Extra properties
        self.properties = kwargs.get('properties', {})
        
        # Validate on creation
        self._validate()

    def _validate(self):
        """Built-in validation - no need to remember to call it"""
        if self.device_type in ["workstation", "server", "service"] and not self.ip:
            raise ValueError(f"{self.device_type.title()} devices must have IP addresses")
        
        if self.device_type not in self.DEVICE_DEFAULTS:
            print(f"Warning: Unknown device type '{self.device_type}'. Using defaults.")
        
    
    @property
    def graphviz_label(self) -> str:
        """DRY - single place that defines how labels look"""
        if self.ip:
            return f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD>{self.display_name}</TD></TR>
                         <TR><TD><FONT POINT-SIZE="30">{self.symbol}</FONT></TD></TR>
                         <TR><TD><FONT POINT-SIZE="10">{self.ip}</FONT></TD></TR>
                       </TABLE>>'''
        else:
            return f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD>{self.display_name}</TD></TR>
                        <TR><TD><FONT POINT-SIZE="30">{self.symbol}</FONT></TD></TR>  
                       </TABLE>>'''
        
    
    def add_to_map(self, network: 'Network', graph: 'pgv.AGraph', pos: tuple, dir: str ="right"):
        if pos in network.positions:
            assert(False)
        else:
            network.positions.add(pos)

        graph.add_node(self.name,
                label=self.graphviz_label,
                shape=self.shape,
                style=self.style,
                fillcolor=self.fillcolor,
                fontcolor=self.fontcolor,
                width=self.width,
                pos=f'{pos[0]},{pos[1]}!'
            )
        super().add_to_map(network, graph, pos, dir)
            

class Cluster(NetworkItem):
    # intermediate is for clusters where devices are in the same shape
    # endpoint is for clusters where devices are in different shapes
    offset = {
        0: [],
        1: [(0, -1, "down")], 
        2: [(-.5, -1, "left"), (.5, -1, "right")],
        3: [(-.5, -1, "left"), (0, -1, "down"), (.5, -1, "right")],
        4: [(-1, -1, "left"), (-.5, -1, "down"), (.5, -1, "down"), (1, -1, "right")],
    }

    CLUSTER_DEFAULTS = {
        "intermediate": {'style': 'filled,rounded', 'fillcolor': '#218dbb', 'fontsize': '12', 'offset': offset},
        "endpoint": {'style': 'filled,rounded', 'fillcolor': 'lightblue', 'fontsize': '10','offset': offset},
    }

    def __init__(self, nodes: list['NetworkDevice'], cluster_type: str, name: str, ip: Optional[str] = None, **kwargs):
        super().__init__(name, ip, device_type="cluster")
        self.nodes = nodes
        self.type = cluster_type
        defaults = self.CLUSTER_DEFAULTS.get(cluster_type, {})

        self.style= kwargs.get('style', defaults.get('style', 'filled,rounded'))
        self.fillcolor = kwargs.get('fillcolor', defaults.get('fillcolor', 'lightblue'))
        self.fontsize = kwargs.get('fontsize', defaults.get('fontsize', '12'))
        self.fontcolor = kwargs.get('fontcolor', defaults.get('fontcolor', 'black'))
        self.offset = kwargs.get('offset', defaults.get('offset', Cluster.offset))
        self.label = kwargs.get('label', None)

    def get_nodes(self):
        return self.nodes
    
    def get_neighbors(self) -> List['NetworkItem']:
        """Get all devices that share an edge"""
        return [neighbor for neighbor in self.connections]
    
    @property
    def graphviz_label(self) -> Optional[str]:
        """DRY - single place that defines how labels look"""
        if self.ip:
            return f'{self.name} - {self.ip}'
        else:
            return None
        
    def add_to_map(self, network: 'Network', graph: 'pgv.AGraph', pos: tuple, dir: str ="down"):
        subgraph = graph.add_subgraph(name=f'cluster_{self.name}')
        subgraph.graph_attr.update({
            'style': self.style,
            'fillcolor': self.fillcolor,
            'fontsize': self.fontsize
        })
        
        for i, node in enumerate(self.get_nodes()):
            node.add_to_map(network, subgraph, (pos[0] + i * network.internal_spacing, pos[1]))
        super().add_to_map(network, graph, pos, dir)

        if self.graphviz_label:
            center:tuple[str, str] = graph.get_node(self.connector_node.name).attr['pos'].strip("!").split(",")
            graph.add_node(self.name+"_label",
                        label=self.graphviz_label,
                        shape='rectangle',  # Invisible node, just text
                        style='filled,rounded',
                        color='lightblue',
                        fontsize='12',
                        pos=f'{center[0]},{float(center[1]) + network.internal_spacing/3}!') 
            
    def __str__(self):
        return f"Cluster {self.name}"
    
    def __repr__(self):
        return f"Cluster {self.name}"
   

    @property
    def connector_node(self, dir="down"):
        # middle node
        if dir == "down":
            return self.nodes[len(self.nodes) // 2]
        elif dir =="left":
            return self.nodes[len(self.nodes)-1]
        elif dir =="right":
            return self.nodes[0]
        else:
            return  self.nodes[0]

class Network:
    """Container for the entire network - keeps everything organized"""

    def __init__(self, name: str = "Network", x_spacing: float = 1, y_spacing: float = .666, internal_spacing: float= .5):
        """
        Layout looks best if ratio of x_spacing : y_spacing is 3 : 2 and
        ration of x_spacing : internal_spacing is 2 : 1
        """
        self.name = name
        self.items: Dict[str, NetworkItem] = {}
        self.metadata = {}
        self.x_spacing = x_spacing
        self.y_spacing = y_spacing
        self.internal_spacing = internal_spacing
        self.map = pgv.AGraph(directed=False, strict=False)
        self.positions: set[tuple] = set()

    def _validate_network(self):
        """Makes sure fully formed network has all required components"""
        required_devices = {"Internet", "UserLocation", "BorderRouter"}
        missing_devices = required_devices - set(self.items)
        if missing_devices:
            raise NetworkError(f"Missing required devices: {', '.join(missing_devices)}")

    def add_item(self, item: NetworkItem) -> NetworkItem:
        """Add a device to the network"""
        if item.name in self.items:
            raise ValueError(f"Item '{item.name}' already exists")
        
        self.items[item.name] = item
        return item
    
    def add_items(self, items: List[NetworkItem]) -> None:
        new_items: Dict[str, NetworkItem] = {}
        for item in items:
            if item.name in self.items:
                raise ValueError(f"Item '{item.name}' already exists")
            
            new_items[item.name] = item
        
        self.items = new_items

    def add_items_from_config(self, item_configs: list[dict]) -> dict[str, 'NetworkItem']:
        """
        Add multiple items to the network from configuration dictionaries.
        
        Each config dict should have:
        - 'type': 'device' or 'cluster'
        - 'name': string name
        - Other parameters specific to NetworkDevice or Cluster constructors
        
        Returns a dict mapping names to created objects for easy reference.
        """
        created_items = {}
    
        for config in item_configs:
            config = config.copy()  # Don't modify original
            item_type = config.pop('type')
            name = config['name']
            if name in self.items:
                raise ValueError(f"Item '{name}' already exists")
            
            if item_type == 'device':
                item = NetworkDevice(**config)
            elif item_type == 'cluster':
                # Handle nodes reference - replace string names with actual objects
                if 'nodes' not in config:
                    raise NetworkError("Clusters must have a list of nodes")
                
                config['nodes'] = list(self.add_items_from_config(config['nodes']).values())
                item = Cluster(**config)
            else:
                raise ValueError(f"Unknown item type: {item_type}")
            
            created_items[name] = item
            # Assuming your network has an add method or similar
            self.add_item(item)  # Adjust this based on your network class
        return created_items
    
    def connect_items_from_config(self, connections: dict[str, list[tuple]]):
        for node, neighbors in connections.items():
            node = self.get_item(node)
            for neighbor in neighbors:
                # Handle different tuple lengths
                if len(neighbor) == 1:
                    # Just the node
                    node.connect_to(self.get_item(neighbor[0]))
                elif len(neighbor) == 2:
                    # Node and hierarchy
                    node.connect_to(self.get_item(neighbor[0]), neighbor[1])
                elif len(neighbor) == 3:
                    # Node, hierarchy, and labels
                    node.connect_to(self.get_item(neighbor[0]), neighbor[1], neighbor[2])

    
    def get_item(self, name: str):
        return self.items[name]

    def add_connections(self, connections: dict['NetworkItem', set[tuple]]):
        for node, neighbors in connections.items():
            for neighbor in neighbors:
                # Handle different tuple lengths
                if len(neighbor) == 1:
                    # Just the node
                    node.connect_to(neighbor[0])
                elif len(neighbor) == 2:
                    # Node and hierarchy
                    node.connect_to(neighbor[0], neighbor[1])
                elif len(neighbor) == 3:
                    # Node, hierarchy, and labels
                    node.connect_to(neighbor[0], neighbor[1], neighbor[2])
    @property
    def all_ips(self):
        # IP address -> device_type, ip_type
        network_ips: list[dict] = []
        for item in self.items.values():
            if item.ip:
                network_ips.append({
                    'ip_address': item.ip,
                    'device_type': item.device_type, 
                    'ip_type': "device"
                })

            for neighbor, (hier, ips) in item.connections.items():
                if len(ips) > 0 and ips[0] != "":
                    network_ips.append({
                    'ip_address': ips[0],
                    'device_type': item.device_type, 
                    'ip_type': "interface"
                })

                if len(ips) > 1 and ips[1] != "":
                    network_ips.append({
                    'ip_address': ips[1],
                    'device_type': neighbor.device_type, 
                    'ip_type': "interface"
                })

        return network_ips

    def generate_map(self, output_name: str = "network") -> str:
        """Generate Graphviz diagram - single method does it all"""
        self._validate_network()

        self.map = pgv.AGraph(directed=False, strict=False)

        # Set graph attributes for neato
        self.map.graph_attr.update({
            'compound': 'true',
            'splines': 'polyline',
            'bgcolor': 'white',
            'fontname': 'Arial',
            'overlap': 'false', # Prevents node overlap with neato
            'inputscale': '1',      # Don't rescale input coordinates
            'mode': 'major'
        })

        self.map.node_attr.update({
            'fontname': 'Arial',
            'fontsize': '14'
        })
        
        # Add all edges + postions (DFS)
        internet = self.get_item("Internet")
        internet.add_to_map(self, self.map, (0, 0))
        
        # debug_before_after_layout(self.map, "After adding all nodes, before any edges")

        # # Add first edge
        self.map.add_edge('Internet', 'BorderRouter', taillabel='128.237.3.102')
        # debug_before_after_layout(self.map, "After first edge, before layout")

        self.map.layout(prog='neato')
        # debug_before_after_layout(self.map, "After first edge, after layout")

        # # # Add second edge
        internet.add_edges(self, self.map)
        # self.map.add_edge('Firewall1', 'Switch', headlabel='172.16.0.1', taillabel='172.16.0.2')
        # debug_before_after_layout(self.map, "After second edge, before layout")

        self.map.draw( f"{output_name}.png", format='png')
        # print("PyGraphviz network diagram created with neato!")
        # Add all connections
        return f"{output_name}.png"

if __name__ == "__main__":
    # Generate example network
    network = Network("TrialNetwork", y_spacing=.666, x_spacing=1, internal_spacing=.5)
    devices = network.add_items_from_config([
        {'type': 'device', 'name': 'Internet', 'device_type': 'Internet'},
        {'type': 'device', 'name': 'BorderRouter', 'device_type': 'Router'},
        {'type': 'device', 'name': 'UserLocation', 'device_type': 'User', 'display_name': 'You are connected here'},
        {'type': 'device', 'name': 'Firewall1', 'device_type': 'Firewall'},
        {'type': 'cluster', 'name': 'switch', 'cluster_type': 'intermediate', 'nodes': [{'type': 'device', 'name': 'Switch', 'device_type': 'Switch'}]},
        {'type': 'cluster', 'name': 'Office', 'cluster_type': 'intermediate', 'nodes': [{'type': 'device', 'name': 'DomainController', 'device_type': 'Controller', 'ip': '172.16.9.10', 'display_name': 'Domain Controller'}], 'ip': '172.16.0.0/12'},
        {'type': 'cluster', 'name': 'ClusterWorkstation1', 'cluster_type': 'endpoint', 'nodes': [{'type': 'device', 'name': 'Workstation1', 'device_type': 'Workstation', 'ip': '172.16.31.101', 'display_name': 'User Workstation 1'}]},
        {'type': 'cluster', 'name': 'ClusterWorkstation2', 'cluster_type': 'endpoint', 'nodes': [{'type': 'device', 'name': 'Workstation2', 'device_type': 'Workstation', 'ip': '172.16.31.102', 'display_name': 'User Workstation 2'}]},
        {'type': 'cluster', 'name': 'ClusterWorkstation3', 'cluster_type': 'endpoint', 'nodes': [{'type': 'device', 'name': 'Workstation3', 'device_type': 'Workstation', 'ip': '172.16.31.103', 'display_name': 'User Workstation 3'}]},
    ])

    network.connect_items_from_config({
        "Internet": [("BorderRouter", "child", (' 128.237.3.102 ',""))],
        "BorderRouter": [("Firewall1", "child", ("  172.16.0.1  ", "  172.16.0.2  "))],
        "Firewall1": [("switch", "same", ("  172.16.0.3  ", ""))],
        "switch": [("UserLocation", "same", ("", "  172.16.5.5  ")), ("Office", "above"), ("ClusterWorkstation1",), ("ClusterWorkstation2",), ("ClusterWorkstation3",)]
    })

    network.generate_map("one_subnet")

    # Paused:
    # Next steps: add positions into network map, starting from internet
    # Future, add functions for adding a bunch of items to the network, with their connections
    # Even more future, add a "generate random map function"
