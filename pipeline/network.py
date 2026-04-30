from typing import Optional, List, Dict, Any
import pygraphviz as pgv
from pathlib import Path

class NetworkError(Exception):
    pass


class NetworkItem:
    # If it is a central node (e.g. Internet), neighbors should be placed below it
    directions: dict[str, dict[int, List[tuple[float, float, str]]]] = {
        "north" : {
            0: [],
            1: [(0, 1, "north")],
            2: [(-.5, 1, "west"), (.5, 1, "east")],
            3: [(-.5, 1, "east"), (0, 1, "east"), (.5, 1, "east")],
        },
        "northeast" : {
            0: [],
            1: [(1, 1, "northeast")],
            2: [(1, -.5, "northeast"), (1, .5, "northeast")],
            3: [(1, -.5, "northeast"), (1.5, 0, "northeast"), (1, .5, "northeast")],
        },
        "east" : {
            0: [],
            1: [(1, 0, "east")],
            2: [(1, -.5, "east"), (1, .5, "east")],
            3: [(1, -.5, "east"), (1.5, 0, "east"), (1, .5, "east")],
        },
        "southeast" : {
            0: [],
            1: [(1, -1, "east")],
            2: [(1, -.5, "east"), (1, .5, "east")],
            3: [(1, -.5, "east"), (1.5, 0, "east"), (1, .5, "east")],
        },
        "south" : {
            0: [],
            1: [(.5, -1.5, "south")],
            2: [(-.5, -1, "west"), (.5, -1, "east")],
            3: [(1, -.5, "east"), (1.5, 0, "east"), (1, .5, "east")],
        },
        "southwest" : {
            0: [],
            1: [(-1, -1, "west")],
            2: [(-.5, -1, "west"), (.5, -1, "east")],
            3: [(1, -.5, "east"), (1.5, 0, "east"), (1, .5, "east")],
        },
        "west" : {
            0: [],
            1: [(-1.1, 0, "west")],
            2: [(-1, -.5, "west"), (-1, .5, "west")],
            3: [(-1, -.5, "west"), (-1.5, 0, "west"), (-1, .5, "west")],
        },
        "northwest" : {
            0: [],
            1: [(-1.25, 1, "northwest")],
            2: [(-1, -.5, "west"), (-1, .5, "west")],
            3: [(-1, -.5, "west"), (-1.5, 0, "west"), (-1, .5, "west")],
        },
        
    }
    offset = {
        0: [],
        1: [(0, -1, "south")], 
        2: [(-.5, -1, "southwest"), (.5, -1, "southeast")],
        3: [(-.5, -1, "southwest"), (0, -1, "south"), (.5, -1, "southeast")],
        4: [(-1, -1, "southwest"), (-.5, -1, "south"), (.5, -1, "south"), (1, -1, "southeast")],
    }


    def __init__(self, name, ip, type_, display_name: Optional[str] = None, properties = {}):
        self.connections: dict['NetworkItem', tuple[str, tuple[str, str]]] = {}
        self.name = name
        self.ip = ip
        self.type = type_
        self.properties = properties
        self.connector_node = None
        self.display_name = display_name or name

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
    
    def add_to_map(self, network: 'Network', graph: 'pgv.AGraph', pos: tuple, dir: str ="east"):
        offset = self.offset[len(self.children)]
        dir_offset = self.directions[dir][len(self.same)]
        # print(f"Node {self.name} at position {pos} with connections: {self.connections}")
        if not self.connector_node:
                self.set_connector_node(dir)

        for i, connection in enumerate(self.above):
            (hier, labels) = self.connections[connection]

            # Kind of hard coding cases where user location is above a dmz
            if connection.name != "UserLocation":
                connection.add_to_map(network, graph, (pos[0] + 0 * network.x_spacing, pos[1] + 1 * network.y_spacing), "north")
            else: 
                # print(f"For user location, direction is {dir}, sp x os pffset by {self.directions[dir][1][0][0]}, so instead of {pos[0]}, its {pos[0] - self.directions[dir][1][0][0] * .4 * network.x_spacing}")
                connection.add_to_map(network, graph, (pos[0] - self.directions[dir][1][0][0] * .4 * network.x_spacing, pos[1] + 1 * network.y_spacing), "north")
            

        for i, connection in enumerate(self.same):
            (hier, labels) = self.connections[connection]
            # print(f"Current Item: {self.name}, Going to {connection.name}, in direction {dir}, but offset is {dir_offset[i][2]}")
            # print(f"Current postion: {pos}")
            if "text" not in connection.name:
                connection.add_to_map(network, graph, (pos[0] + dir_offset[i][0] * network.x_spacing * .9, pos[1] + dir_offset[i][1] * network.y_spacing), dir_offset[i][2])
            else:          
                print("OUTSIDE NAME IS ", self.outside_connector_node.name)
                new_pos = graph.get_node(self.outside_connector_node.name).attr['pos'].strip("!").split(",")
                new_pos = float(new_pos[0]), float(new_pos[1])
                connection.add_to_map(network, graph, (new_pos[0] + dir_offset[i][0] * network.x_spacing * .3, new_pos[1] + dir_offset[i][1] * network.y_spacing), dir_offset[i][2])
            

        for i, connection in enumerate(self.children):
            (hier, labels) = self.connections[connection]
            new_pos = graph.get_node(self.child_connector_node.name).attr['pos'].strip("!").split(",")
            new_pos = float(new_pos[0]), float(new_pos[1])
            connection.add_to_map(network, graph, (new_pos[0] + offset[i][0] * network.internal_spacing, new_pos[1] + offset[i][1] * network.y_spacing*1.2), offset[i][2])
    
    def add_edges(self, network: 'Network', graph: 'pgv.AGraph'):
        for connection in self.neighbors:
            (hier, labels) = self.connections[connection]
            if self.name not in ["Internet"]:
                # print(f"adding edge between {self.name} and {connection.name}")
                if hier == "same":
                    if not connection.name.startswith("dmz_text"):
                        graph.add_edge(self.inside_connector_node.name, connection.set_connector_node().name, taillabel = labels[0], headlabel=labels[1])
                elif hier == "above":
                    graph.add_edge(self.above_connector_node.name, connection.set_connector_node().name, taillabel = labels[0], headlabel=labels[1])
                else:
                    graph.add_edge(self.child_connector_node.name, connection.set_connector_node().name, taillabel = labels[0], headlabel=labels[1])

            connection.add_edges(network, graph)


    def set_connector_node(self, dir = "south") -> "NetworkItem":
        if self.connector_node is None:
            self.connector_node: Optional["NetworkItem"] = self
        return self.connector_node

    @property
    def inside_connector_node(self):
        return self.connector_node
    
    @property
    def outside_connector_node(self):
        return self.connector_node
    
    @property
    def above_connector_node(self):
        return self.connector_node
    
    @property
    def child_connector_node(self):
        return self.connector_node

class NetworkDevice(NetworkItem):
    """Representation for individual nodes on our network and how they connect to each other"""
    offsets = {
        'Internet' : {
            0: [],
            1: [(0, -1, "south")], 
            2: [(-1, 0, "west"), (1, 0, "east")],
            3: [(-1, 0, "west"), (0, -1, "south"), (1, 0, "east")],
            4: [(-1, 0, "west"), (-1, -1, "west"), (1, 0, "east"), (1, -1, "east")]
        },
        'Router': {
            0: [],
            1: [(1.75, 0, "east")], 
            2: [(-1.75, 0, "west"), (1.75, 0, "east")],
            3: [(-1.75, 0, "west"), (0, -1, "south"), (1.75, 0, "east")],
            4: [(-1.25, 1, "west"), (1.25, 1, "east"), (-1.25, -1, "southwest"), (1.25, -1, "southeast")]
        },
        # "east" : {
        #     0: [],
        #     1: [(1, 0, "east")],
        #     2: [(1, -.5, "east"), (1, .5, "east")],
        #     3: [(1, -.5, "east"), (1.5, 0, "east"), (1, .5, "east")],
        # },
        # "west" : {
        #     0: [],
        #     1: [(-1, 0, "west")],
        #     2: [(-1, -.5, "west"), (-1, .5, "west")],
        #     3: [(-1, -.5, "west"), (-1.5, 0, "west"), (-1, .5, "west")],
        # },
        'Normal' :{
            0: [],
            1: [(0, -1, "south")],
            2: [(-.5, -1, "south"), (.5, -1, "south")],
            3: [(-.5, -1, "south"), (0, -1, "south"), (.5, -1, "south")],
        },
        # 'parent' : {
        #     0: [],
        #     1: [(0, 1, "north")],
        #     2: [(-.5, 1, "north"), (.5, 1, "north")],
        #     3: [(-.5, 1, "north"), (0, 1, "north"), (.5, 1, "north")],
        # }
    }

    

    DEVICE_DEFAULTS = {
        "Internet": {"symbol": "☁", "fillcolor": "lightblue", "fontcolor": "black", "shape": "ellipse", "style":"filled", "offset": offsets['Internet']},
        "Router": {"symbol": "📡", "fillcolor": "lightblue", "fontcolor": "black", "shape": "cylinder", "offset": offsets["Router"]},
        "Switch": {"symbol": "🔀", "fillcolor": "none", "fontcolor": "white", "shape": 'none'},
        "Controller": {"symbol": "🖥", "fillcolor": "none", "fontcolor": "white", "shape": 'none'},
        "Firewall": {"symbol": "🛡", "fillcolor": "lightgrey", "fontcolor": "black","shape": "square", "style":"filled"},
        "Server": {"symbol": "🗄️", "fillcolor": "none", "fontcolor": "black", "shape": 'none'},
        "Workstation": {"symbol": "💻", "fillcolor": "lightblue", "fontcolor": "black"},
        "Printer": {"symbol": "🖨️", "fillcolor": "lightblue", "fontcolor": "black"},
        "Camera": {"symbol": "📷", "fillcolor": "lightblue", "fontcolor": "black"},
        "Thermostat": {"symbol": "🌡️", "fillcolor": "lightblue", "fontcolor": "black"},
        "User": {"symbol": "📍", "fillcolor": '#CCA4D3', "shape": "ellipse", "style": "filled"},
        "Text": {"symbol": "🗒️","shape": "rectangle", "fillcolor": "none", "fontcolor": 'black', "fontsize": 12}
    }
    
    def __init__(self, name: str, device_type: str, ip: Optional[str] = None, display_name: Optional[str] = None, **kwargs):
        properties = kwargs.get('properties', {})
        super().__init__(name, ip, type_ = "device", display_name= display_name, properties=properties)
        self.device_type = device_type
        
        defaults = self.DEVICE_DEFAULTS.get(device_type, {})

        self.symbol = kwargs.get('symbol', defaults.get('symbol', '🔘'))
        self.fillcolor = kwargs.get('fillcolor', defaults.get('fillcolor', 'lightgray'))
        self.fontcolor = kwargs.get('fontcolor', defaults.get('fontcolor', 'black'))
        self.shape = kwargs.get('shape', defaults.get('shape', 'box'))
        self.width = kwargs.get('width', defaults.get('width', '1'))
        self.style= kwargs.get('style', defaults.get('style', 'filled,rounded'))
        self.fontsize= kwargs.get('fontsize', defaults.get('fontsize', 14))
        self.offset: dict[int, List[tuple[float, float, str]]] = kwargs.get('offset', defaults.get('offset', NetworkDevice.offsets["Normal"]))
        
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
        def wrap_text_by_words(text, max_width=15):
            words = text.split()
            lines = []
            current_line = ""

            for word in words:
                # If adding the next word exceeds max_width, start a new line
                if len(current_line) + len(word) + (1 if current_line else 0) > max_width:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Add space if line not empty
                    current_line += (" " if current_line else "") + word

            # Append last line
            if current_line:
                lines.append(current_line)

            # Join lines with <BR/>
            return "<BR/>".join(lines)
        display= wrap_text_by_words(self.display_name)
        if self.ip:
            return f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="{self.fontsize}">{self.display_name}</FONT></TD></TR>
                         <TR><TD><FONT POINT-SIZE="30">{self.symbol}</FONT></TD></TR>
                         <TR><TD><FONT POINT-SIZE="14">{self.ip}</FONT></TD></TR>
                       </TABLE>>'''
        else:
            return f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="{self.fontsize}">{display}</FONT></TD></TR>
                        <TR><TD><FONT POINT-SIZE="30">{self.symbol}</FONT></TD></TR>  
                       </TABLE>>'''
        
    
    def add_to_map(self, network: 'Network', graph: 'pgv.AGraph', pos: tuple, dir: str ="east"):
        if pos in network.positions:
            print(f"Adding {self.name} to already occupied position {pos}")
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
        1: [(0, -1, "south")], 
        2: [(-.5, -1, "southwest"), (.5, -1, "southeast")],
        3: [(-.5, -1, "southwest"), (0, -1, "south"), (.5, -1, "southeast")],
        4: [(-1, -1, "southwest"), (-.5, -1, "south"), (.5, -1, "south"), (1, -1, "southeast")],
    }

    CLUSTER_DEFAULTS = {
        "intermediate": {'style': 'filled,rounded', 'fillcolor': '#218dbb', 'fontsize': '12', 'offset': offset},
        "endpoint": {'style': 'filled,rounded', 'fillcolor': 'lightblue', 'fontsize': '10','offset': offset},
    }

    def __init__(self, nodes: list['NetworkDevice'], cluster_type: str, name: str, ip: Optional[str] = None, display_name: Optional[str] = None, **kwargs):
        super().__init__(name, ip, type_="cluster", display_name= display_name)
        self.nodes = nodes
        self.cluster_type = cluster_type
        defaults = self.CLUSTER_DEFAULTS.get(cluster_type, {})

        self.style= kwargs.get('style', defaults.get('style', 'filled,rounded'))
        self.fillcolor = kwargs.get('fillcolor', defaults.get('fillcolor', 'lightblue'))
        self.fontsize = kwargs.get('fontsize', defaults.get('fontsize', '12'))
        self.fontcolor = kwargs.get('fontcolor', defaults.get('fontcolor', 'black'))
        self.offset = kwargs.get('offset', defaults.get('offset', Cluster.offset))
        self.label = kwargs.get('label', None)

        self.properties = kwargs.get('properties', {})
        self.connector_node = None

    def get_nodes(self):
        return self.nodes
    
    def get_neighbors(self) -> List['NetworkItem']:
        """Get all devices that share an edge"""
        return [neighbor for neighbor in self.connections]
    
    @property
    def graphviz_label(self) -> Optional[str]:
        """DRY - single place that defines how labels look"""
        if self.ip:
            return f'{self.display_name} - {self.ip}'
        else:
            return None
        
    def add_to_map(self, network: 'Network', graph: 'pgv.AGraph', pos: tuple, dir: str ="south"):
        subgraph = graph.add_subgraph(name=f'cluster_{self.name}')
        subgraph.graph_attr.update({
            'style': self.style,
            'fillcolor': self.fillcolor,
            'fontsize': self.fontsize
        })
        # if direction is west, add nodes going to the left, starting with the last node
        nodes = self.get_nodes() if dir != "west" else self.get_nodes()[::-1]
        position = pos
        for i, node in enumerate(nodes):
            if dir != "west":
                position = (pos[0] + i * network.internal_spacing, pos[1])
            else:
                position = (pos[0] + i * network.internal_spacing - i * network.x_spacing, pos[1])
            node.add_to_map(network, subgraph, position)
        # print(f"Original position to put {self.name}'s nodes: {pos};  Final position of node: {position}")
        super().add_to_map(network, graph, pos, dir)

        if self.graphviz_label:
            center:tuple[float, float] = self.get_center(subgraph)
            graph.add_node(self.name+"_label",
                        label=self.graphviz_label,
                        shape='rectangle',  # Invisible node, just text
                        style='filled,rounded',
                        color='lightblue',
                        fontsize='14',
                        pos=f'{center[0]},{center[1] + network.internal_spacing/1.5}!') 
            
    def __str__(self):
        return f"Cluster {self.name}"
    
    def __repr__(self):
        return f"Cluster {self.name}"
    
    def get_center(self, graph):
        # if it's odd, return position of center node
        # if it's even, average positions of center nodes
        # print("Self nodes length: ", len(self.nodes))
        if len(self.nodes) % 2 != 0:
            center = graph.get_node(self.nodes[len(self.nodes) // 2].name).attr['pos'].strip("!").split(",")
            return float(center[0]), float(center[1])
        else:
            left = graph.get_node(self.nodes[len(self.nodes) // 2 - 1].name).attr['pos'].strip("!").split(",")
            right = graph.get_node(self.nodes[len(self.nodes) // 2].name).attr['pos'].strip("!").split(",")
            return (float(left[0]) + float(right[0])) / 2, (float(left[1]) + float(right[1])) / 2
   
    def set_connector_node(self, dir="south") -> "NetworkDevice":
        if self.connector_node:
            return self.connector_node
        # middle node
        if dir == "south":
            self.connector_node = self.nodes[len(self.nodes) // 2]
        elif dir =="west":
            self.connector_node = self.nodes[-1]
        elif dir =="east":
            self.connector_node = self.nodes[0]
        else:
            self.connector_node = self.nodes[0]

        return self.connector_node
    
    @property
    def child_connector_node(self):
        return self.nodes[len(self.nodes) // 2]
    
    @property
    def outside_connector_node(self):
        if self.connector_node:
            inside_ind = self.nodes.index(self.connector_node)
            if inside_ind == len(self.nodes) - 1:
                return self.nodes[0]
            elif inside_ind == 0:
                return self.nodes[-1]
            else:
                return self.connector_node
            
        raise NetworkError(f"Node {self.name} does not have a connector node yet")


class Network:
    """Container for the entire network - keeps everything organized"""
    def __init__(self, name: str = "Network", x_spacing: float = .5, y_spacing: float =1/3, internal_spacing: float= .25):
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

    
    def remove_items(self, items: list['NetworkItem']):
        for item in items:
            if item.name not in self.items:
                raise ValueError(f"Item '{item.name}' does not exist")
            self.items.pop(item.name)
    
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
    def used_ips(self):
        network_ips: set[str] = set()
        for item in self.items.values():
            if item.type == "device" and item.ip:
                network_ips.add(item.ip)

        return network_ips
    
    @property
    def systems(self):
        all_systems: list['NetworkItem'] = list()
        for item in self.items.values():
            if item.type == "device" and item.ip and item.device_type == "Workstation" and "User" not in item.display_name :
                all_systems.append(item)

        return all_systems

    def generate_map(self, output_name: str = "network", folder: str ="") -> str:
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

        self.map.layout(prog='neato')
        self.map.add_edge('Internet', 'BorderRouter', taillabel=' 128.237.3.102 ')
        # # # Add second edge
        internet.add_edges(self, self.map)

        filepath = f"{folder}/{output_name}.png" if folder else f"{output_name}.png"
        if folder:
            Path(folder).mkdir(parents=True, exist_ok=True)
        self.map.draw(filepath, format='png')

        # Add all connections
        return f"{output_name}.png"
    
    @property
    def workstations(self) -> list['NetworkDevice']:
        ws = list()
        for item in self.items.values():
            if isinstance(item, NetworkDevice):

                if item.device_type == "Workstation":
                    ws.append(item)
        return ws
    
    @property
    def servers(self) -> list['NetworkDevice']:
        server_list = list()
        for item in self.items.values():
            if isinstance(item, NetworkDevice):
                if item.device_type == "Server":
                    server_list.append(item)
        return server_list
    
    def all_positions(self):
        for item in self.items.values():
            if item.type != "cluster":
                print(f"item {item.name} is at position {self.map.get_node(item.name).attr['pos'].strip('!').split(',')}")


if __name__ == "__main__":
    # Generate example network (1 subnet)
    network = Network("TrialNetwork")
    base_ip = '192.168.0.0'
    prefix_length = '/24'

    base_parts = base_ip.split('.')
    base_prefix = '.'.join(base_parts[:-1])
    base_last = int(base_parts[-1])

    def ip_offset(offset):
        return f"{base_prefix}.{base_last + offset}"

    # Change IP addresses of individual devices here
    devices = network.add_items_from_config([
        {'type': 'device', 'name': 'Internet', 'device_type': 'Internet'},
        {'type': 'device', 'name': 'BorderRouter', 'device_type': 'Router'},
        {'type': 'device', 'name': 'UserLocation', 'device_type': 'User', 'display_name': 'You are connected here'},
        {'type': 'device', 'name': 'Firewall1', 'device_type': 'Firewall'},
        {'type': 'cluster', 'name': 'switch', 'cluster_type': 'intermediate', 'nodes': [{'type': 'device', 'name': 'Switch', 'device_type': 'Switch'}]},
        {'type': 'cluster', 'name': 'Office', 'cluster_type': 'intermediate', 'nodes': [{'type': 'device', 'name': 'DomainController', 'device_type': 'Controller', 'ip': ip_offset(20), 'display_name': 'Domain Controller'}], 'ip': base_ip + prefix_length},
        {'type': 'cluster', 'name': 'ClusterWorkstation1', 'cluster_type': 'endpoint', 'nodes': [{'type': 'device', 'name': 'Workstation1', 'device_type': 'Server', 'ip': ip_offset(100), 'display_name': 'Server'}]},
        {'type': 'cluster', 'name': 'ClusterWorkstation2', 'cluster_type': 'endpoint', 'nodes': [{'type': 'device', 'name': 'Workstation2', 'device_type': 'Printer', 'ip': ip_offset(101), 'display_name': 'User Workstation'}]},
        {'type': 'cluster', 'name': 'ClusterWorkstation3', 'cluster_type': 'endpoint', 'nodes': [{'type': 'device', 'name': 'Workstation3', 'device_type': 'Camera', 'ip': ip_offset(102), 'display_name': 'Camera'}]},
    ])

    # Change IP addresses of individual edges here
    network.connect_items_from_config({
        "Internet": [("BorderRouter", "child", (' 128.237.3.102 ',""))],
        "BorderRouter": [("Firewall1", "child", (f"  {ip_offset(1)}  ", f"  {ip_offset(2)}  "))],
        "Firewall1": [("switch", "same", (f"  {ip_offset(3)}  ", ""))],
        "switch": [("UserLocation", "same", ("", f"  {ip_offset(5)}  ")), ("Office", "above"), ("ClusterWorkstation1",), ("ClusterWorkstation2",), ("ClusterWorkstation3",)]
    })

    # Change file name here
    network.generate_map("network_map")