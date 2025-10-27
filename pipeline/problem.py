from typing import Optional, List, Dict, Any
from network import Network
from netaddr import IPNetwork, IPAddress
import random

class ProblemError(Exception):
    pass

class Problem():
    servers_ports = {
        "Web Server": "80 443",                       
        "Mail Server": "25 465 587 2525",           
        "DNS Server": "53",                            
        "Domain Controller": "88 389 636 3268",     
        "File Server": "445",                          
        "Print Server": "515 9100",                   
        "Application Server": "8080 8443",            
        "Backup Server": "13782 13724",               
        "Monitoring Server": "161 162 5666",          
        "Proxy Server": "3128 8081",                  
        "Update Server": "8530 8531",                 
        "VoIP Server": "5060 5061",                   
    }
    ports_servers = {v: k for k,v in servers_ports.items()}

    servers_blurb = {
        "Web Server": "a web server hosting both secure and insecure web connections (HTTP on TCP port 80 and HTTPS on TCP port 443)",
        "Mail Server": "a mail server providing SMTP over TCP ports 25, 465, 587 and 2525",
        "DNS Server": "a DNS server providing lookup services over TCP port 53",
        "Domain Controller": "a domain controller providing Kerberos and directory services (Kerberos on TCP port 88, LDAP on 389, LDAPS on 636, and Global Catalog on 3268)",
        "File Server": "a file server providing SMB file sharing over TCP port 445",
        "Print Server": "a print server providing printing services (LPD on TCP port 515 and JetDirect on TCP port 9100)",
        "Application Server": "an application server hosting web applications (commonly on TCP ports 8080 and 8443)",
        "Backup Server": "a backup server providing backup services (Veritas NetBackup on TCP ports 13724 and 13782)",
        "Monitoring Server": "a monitoring server providing monitoring and alerting services (SNMP on TCP ports 161 and 162, and NRPE on 5666)",
        "Proxy Server": "a proxy server providing web proxy services (commonly on TCP ports 3128 and 8081)",
        "Update Server": "an update server providing software updates (Microsoft WSUS on TCP ports 8530 and 8531)",
        "VoIP Server": "a VoIP server providing voice-over-IP services (SIP on TCP ports 5060 and 5061)",
    }

    def __init__(self, cidr_blocks, subnets, q_type = "normal", folder = "exampleFiles", images_folder = "images"):
        self.cidr_blocks = cidr_blocks
        self.subnets = subnets
        self.config = self.gen_config()
        self.network = self.gen_network()
        self.answers = None
        self.problem_dict = None
        if q_type not in ["pretest", "posttest", "normal"]:
            raise ProblemError(f"q_type must be either 'pretest', 'posttest', or 'normal', not {q_type}")
        self.q_type = q_type
        self.folder = folder
        self.images_folder = images_folder

    def get_baseline_dict(self, item_type, name, **kwargs) -> dict[str, Any]:
        baseline = {
            "type": item_type,
            'name': name,
        }
        ip = kwargs.get("ip")
        if ip:
            baseline["ip"] = ip
        display_name = kwargs.get('display_name')
        if display_name:
            baseline["display_name"] = display_name
            if display_name == "Domain Controller":
                kwargs.__setitem__("device_type", "Controller")

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
            
            if device_type == "Workstation":
                baseline['properties']["PortsOpen"] = "22 53 80 139 443 445"
            elif device_type == "Firewall":
                baseline['properties']["PortsOpen"] = "22 53 80 123 389 443"
            elif device_type in ["Switch", "DomainController"] or display_name == "Domain Controller":
                baseline['properties']["PortsOpen"] = "22 53 80 88 135 139 389 443 445 464" 
            elif display_name in self.servers_ports:
                baseline['properties']["PortsOpen"] = self.servers_ports[display_name]
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
    
    def start_config(self):
        internet = self.get_baseline_dict(item_type="device", device_type="Internet", name="Internet")
        router = self.get_baseline_dict(item_type="device", device_type="Router", name="BorderRouter")
        user = self.get_baseline_dict(item_type="device", device_type="User", name="UserLocation", display_name="You are connected here")
        config = [
            internet,
            router,
            user
        ]
        internet["connections"] = [("BorderRouter", "child", (' 128.237.3.102 ',""))]

        return config, router
    
    def gen_config(self) -> list[dict[str, Any]]:
        return []
    
    def gen_network(self) -> 'Network':
        """
        Generates a dictionary graph representation of the network, where nodes that are connected by an edge in the map are neighbors

        Args:
            items (list[dict]): A list of items in the network
            connections (dict): Collection of one way connections of devices on the network
        Returns:
            dict: Dictionary representation of network map
        """
        items = self.config
        map_rep = Network("ExampleNetwork", x_spacing= .5, y_spacing= .3333, internal_spacing=.25)
        map_rep.add_items_from_config(items)
        connections = dict()
        for item in items:
            if "connections" in item:
                connections[item["name"]] = item["connections"]

        print("Connections: ", connections)
        map_rep.connect_items_from_config(connections)

        return map_rep
    
    def gen_map(self, img_name: Optional[str] = None) -> None:
        print("A map is being generated")
        if not img_name and self.q_type == "normal":
            img_name = self.__class__.__name__ + "_" + str(self.subnets)
        elif not img_name:
            img_name = self.__class__.__name__ + "_" + self.q_type + '_' + str(self.subnets)

        print(img_name)
        self.img_name = self.network.generate_map(f"{img_name}", folder=self.folder + "/" + self.images_folder)
    
    def get_answer_defaults(self) -> dict:
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

        if self.__class__ in [BadPorts, IdentifyServices]:
            portscan = True
        elif self.__class__ in [RogueWorkstations, UnresponsiveWorkstations]:
            portscan = False
        else:
            raise NameError(f"Problem type '{repr(self.__class__)}' not found")
        return portscan_defaults if portscan else pingscan_defaults
    
    def gen_answers(self) -> dict:
        return self.get_answer_defaults()
    
    def gen_example_data(self) -> list[dict[str, str]]:
        example_data = []

        for item in self.network.items.values():
            if item.type == "device":
                if item.ip:
                    example_data.append({
                        "IP": item.ip.strip(),
                        "Latency": item.properties["Latency"],
                        "PortsClosed": item.properties["PortsClosed"],
                        "PortsFiltered": item.properties["PortsFiltered"],
                        "PortsOpen": item.properties["PortsOpen"]
                    })

                for neighbor, (hier, ips) in item.connections.items():
                    
                    if len(ips) > 0 and ips[0] != "":
                        example_data.append({
                            'IP': ips[0].strip(),
                            "Latency": item.properties["Latency"],
                            "PortsClosed": item.properties["PortsClosed"],
                            "PortsFiltered": item.properties["PortsFiltered"],
                            "PortsOpen": item.properties["PortsOpen"]
                        })

                    if len(ips) > 1 and ips[1] != "":
                        example_data.append({
                            'IP': ips[1].strip(),
                            "Latency": neighbor.properties["Latency"],
                            "PortsClosed": neighbor.properties["PortsClosed"],
                            "PortsFiltered": neighbor.properties["PortsFiltered"],
                            "PortsOpen": neighbor.properties["PortsOpen"]
                        }) 
        example_data.sort(key=lambda x: int(IPAddress(x["IP"].strip())))
        return example_data
    
    def get_problem_defaults(self, prob_number: int) -> dict:
        return {}

    def set_problem_dict(self, prob_number: int = 1) -> dict:
        content = self.get_problem_defaults(prob_number)
        content["imgAddress"] = "Assets/" + self.img_name
        if self.q_type == "pretest":
            content["introtxt"] = "Pre-test: This quiz aims to assess our course content, NOT you personally. There's NO need to worry about getting questions wrong. <strong>If you encounter unfamiliar or challenging questions, please enter 'I don't know' instead of guessing the answer</strong>. Your honest response is invaluable to us as we refine the course.  Click the 'Done' button when you are finished with all of the questions."
        elif self.q_type == "posttest":
            content["introtxt"] = "Post-test: This quiz aims to assess our course content, NOT you personally. There's NO need to worry about getting questions wrong. <strong>If you encounter unfamiliar or challenging questions, please enter 'I don't know' instead of guessing the answer</strong>. Your honest response is invaluable to us as we refine the course.  Click the 'Done' button when you are finished with all of the questions."
        assert(self.answers)
        content.update(self.answers)
        content["exampledata"] = self.gen_example_data()
        self.problem_dict = content
        
        return content
        

    def dict_to_nools_value(self, value):
        """Convert Python values to nools-compatible format"""
        if isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, list):
            items = [self.dict_to_nools_value(item) for item in value]
            return "[" + ", ".join(items) + "]"
        elif isinstance(value, dict):
            items = []
            for k, v in value.items():
                nools_val = self.dict_to_nools_value(v)
                items.append(f"{k}: {nools_val}")  # No quotes around key
            return "{" + ", ".join(items) + "}"
        else:
            return str(value)

    def gen_nools_file(self, output_file = None):           
        if output_file is None:
            
            if self.q_type == "normal":
                output_file = self.folder + "/" + self.__class__.__name__ + '_' + str(self.subnets) + ".nools"
            else:
                output_file = self.folder + "/" + self.__class__.__name__ + '_' + self.q_type + '_' + str(self.subnets) + ".nools"

        if self.q_type == "normal":
            imports = [
                "productionRules-final.nools",
                "SkillDefinitions.nools"
            ]
        else:
            imports = [
                "productionRules-test.nools"
            ]
        
        with open(output_file, 'w') as f:
            # Write imports
            for imp in imports:
                f.write(f'import("{imp}");\n')
            f.write("\n")
            # Write globals
            if self.problem_dict is None:
                raise ProblemError("Make sure to set problem dict before generating the nools file")
            
            for key, value in self.problem_dict.items():
                nools_value = self.dict_to_nools_value(value)
                f.write(f'global {key} = {nools_value};\n')
                if key == "imgAddress" or key == "ipAnswer" or key == "rightAnswer":
                    f.write("\n")



class BadPorts(Problem):
    bad_ports: dict[str, tuple] = { # name -> port_start, port_stop, prob_txt
        "Bittorent": (6881, 6889, "We have received a DMCA complaint that someone is sharing copyrighted material from our corporate network via bittorrent. <strong>Conduct a scan with nmap to find out which workstation is responsible.</strong> ( Bittorrent is known to use TCP ports in the range <strong>6881 - 6889</strong> )"),
        "SQL": (1433, 1440, "IT suspects someone is running an unauthorized SQL Server instance on our internal network. <strong>Scan for hosts listening on TCP ports 1433–1440.</strong>"),
        "VNC": (5900, 5905, "A remote desktop service other than RDP may be in use internally. <strong>Use nmap to check for Virtual Network Computing servers listening on TCP ports 5900–5905.</strong>"),
        "Malware": (31337, 31340, "Unusual connections suggest some workstations may be compromised. <strong>Scan the network for hosts with open TCP ports 31337–31340.</strong>"),
        "Games": (25565, 25570, "We have reason to believe some employees may be running unauthorized game servers on the corporate LAN. <strong> Conduct a scan with nmap to find out which workstations are responsible. </strong> ( Game Server is known to use TCP ports in the range <strong> 25565–25570</strong> )"),
    }
    def __init__(self, cidr_blocks, subnets, q_type = "normal", folder = "exampleFiles", images_folder = "images"):
        super().__init__(cidr_blocks, subnets, q_type, folder, images_folder)
        if q_type == "normal":
            self.bad_type = random.choice(list(self.bad_ports.keys())[:-1])
        else:
            self.bad_type = list(self.bad_ports.keys())[-1] # ensure the pretest/posttest is different than what they practiced with

    def gen_config(self):
        config, router = super().start_config()
        has_user_loc = False
        workstation_count = 1
        get_baseline = super().get_baseline_dict
        
        for i in range(len(self.cidr_blocks)):
            net = self.cidr_blocks[i]
            firewall = get_baseline(item_type="device", device_type="Firewall", name=f'Firewall_{i + 1}', display_name=f'Firewall {i + 1}')
            router.setdefault("connections", []).append((f"Firewall_{i + 1}", "child", (f"  {net[1]}  ", f"  {net[3]}  ")))

            # if i % 2 == 0:
            switch = get_baseline(item_type = "cluster", name=f'switch_cluster_{i}', cluster_type='intermediate', 
                            nodes= [get_baseline(item_type="device", name=f'Switch_{i+1}', device_type= 'Switch', display_name= f'Switch {i+1}')])
            office = get_baseline(item_type = "cluster", name=f'Office_{i + 1}', cluster_type='intermediate', ip= str(net), display_name= f"Office {i+1}",
                                nodes= [get_baseline(item_type="device", name= f'DomainController_{i}', device_type="Controller", ip= f'{net[10]}', display_name= 'Domain Controller')])
            config = config + [
                firewall,
                switch,
                office
            ]
            firewall["connections"] = [(f'switch_cluster_{i}', "same", (f"  {net[5]}  ", ""))]
            switch["connections"] = [(f'Office_{i + 1}', "above", ("", ""))]
            # else:
            #     # switch = get_baseline_dict(item_type = "cluster", name=f'switch_cluster_{i}', cluster_type='intermediate', 
            #     #                 nodes= [get_baseline_dict(item_type="device", name=f'Switch_{i}', device_type= 'Switch')])
            #     switch = get_baseline_dict(item_type = "cluster", name=f'switch_cluster_{i}', cluster_type='intermediate', display_name= f"Office {i}", ip= str(net),
            #                         nodes= [get_baseline_dict(item_type="device", name= f'Switch_{i}', device_type="Switch")])
            #     config = config + [
            #     firewall,
            #     switch,
            #     # office
            #     ]
            #     firewall["connections"] = [(f'switch_cluster_{i}', "same", (f"  {net[5]}  ", ""))]
            #     switch["connections"] = []
                            
            if not has_user_loc:
                switch["connections"].append(("UserLocation", "same", ("", f"  {net[20]}  ")))
                has_user_loc = True

            offset = random.randint(40, 100)
            for j in range(1,random.randint(3, 4)):
                ip_address = net[offset+j]
                workstation= get_baseline(item_type= "cluster", name=f'ClusterWorkstation_{workstation_count}', cluster_type='endpoint',
                                nodes= [get_baseline(item_type='device', name=f'Workstation_{workstation_count}', device_type="Workstation", ip=f'{ip_address}', display_name=f'User Workstation {workstation_count}')])
                config.append(workstation)
                switch["connections"].append(( f'ClusterWorkstation_{workstation_count}', "child", ("","")))
                workstation_count += 1
        return config
    
    def gen_answers(self) -> dict:
        answers = super().gen_answers()
        port_start, port_end, prob_txt = self.bad_ports[self.bad_type]
        answers["portsAnswer"] = [f'-p {port_start}-{port_end}']
        # Scan the relevant cidr blocks, or in this case, all of them
        answers["ipAnswer"] =  [" ".join([str(block) for block in self.cidr_blocks])]
        workstations = self.network.workstations
        ws_count:int = len(workstations)
        
        bad_ws = random.randint(1, min(ws_count, 4))
        print("COUNTS", ws_count, bad_ws)
        shuffled_ws = random.sample(workstations, bad_ws)
        left_answer = []
        right_answer = []
        bad_ports = [str(port_num) for port_num in range(port_start, port_end+1)]
        for ws in shuffled_ws:
            ws.properties["PortsOpen"] += " " + random.choice(bad_ports)
            left_answer.append(ws.ip)
            right_answer.append(ws.display_name.split(" ")[2])
        
        answers["leftAnswer"] = left_answer
        answers["rightAnswer"] = right_answer
        self.answers = answers
        return answers
    
    def get_problem_defaults(self, prob_number: int) -> dict:
        port_start, port_end, prob_txt = self.bad_ports[self.bad_type]
        defaults = {
                'probType': "Bad Ports",
                'fixLeft': False,
                'oneColumn': False,
                'probtxt': prob_txt,
                'title': f"Tutor: NMAP problem {prob_number}",
                'opQuestion': 'Based on the output, which workstations are responsible?',
                'leftTitle': 'IP Address',
                'rightTitle': 'Workstation Number'
            }
        return defaults

class WorkstationProblem(Problem):
    def __init__(self, cidr_blocks, subnets, show_names = True, q_type = "normal", folder = "exampleFiles", images_folder = "images"):
        self.show_names = show_names
        self.services = ""
        super().__init__(cidr_blocks, subnets, q_type, folder=folder, images_folder=images_folder)

    def gen_config(self):
        config, router = super().start_config()
        has_user_loc = False
        
        dmz_names = ['DMZ 1', 'Office 1', "DMZ 2", "Office 2"]
        server_count = 0
        workstation_count = 0
        user_count = 1
        services = ["Kiosk Computer", "Digital Signage", "Vending Machine", "Workstatation 1", "Workstation 2", "Workstation 3",
                    "Security Camera", "Printer", "Access Panel", "Workstation 4", "Workstation 5", "Workstation 6"]
        
        get_baseline = super().get_baseline_dict
        
        for i in range(len(self.cidr_blocks)):
            net = self.cidr_blocks[i]
            firewall = get_baseline(item_type="device", device_type="Firewall", name=f'Firewall_{i + 1}', display_name=f'Firewall {i + 1}')
            router.setdefault("connections", []).append((f"Firewall_{i + 1}", "child", (f"  {net[1]}  ", f"  {net[3]}  ")))

            dmz = get_baseline(item_type = "cluster", name=f'DMZ_{i}', cluster_type='intermediate', ip= str(net), display_name= dmz_names[i],
                                nodes= [get_baseline(item_type="device", name= f'Server_{server_count + j + 1}', device_type="Server", ip= f'{net[20 + j]}', display_name= list(self.servers_ports.keys())[server_count + j]) for j in range(3)])
            print("DMZ LOOKS LIKE: ", dmz)
            if not self.show_names:
                for node in dmz["nodes"]:
                    
                    node['display_name'] = " ".join(node['name'].split("_")) if node['display_name'] != "Domain Controller" else "Domain Controller"
            server_count += 3
            config = config + [
                firewall,
                dmz
                ]
            firewall["connections"] = [(f'DMZ_{i}', "same", (f"  {net[5]}  ", ""))]

            services_net = str(net).split("/")[0] + "/27"
            if len(self.services) > 0:
                self.services = self.services + " " + services_net
            else:
                self.services = services_net
            
            if not has_user_loc:
                # text = get_baseline(item_type="device", name="dmz_text", device_type="Text", display_name="Services portion of the DMZ Assigned to the range " + services_net)
                # config.append(text)
                dmz["connections"] = [("UserLocation", "above", ("", f"  {net[10]}   "))]
                # dmz["connections"].append(("dmz_text", "same", ("", "")))
                has_user_loc = True
            else:
                dmz["connections"] = []
            if not self.show_names:
                text = get_baseline(item_type="device", name=f"dmz_text_{i}", device_type="Text", display_name="Services portion assigned to the range " + services_net)
                config.append(text)
                dmz["connections"].append((f"dmz_text_{i}", "same", ("", "")))

            offset = random.randint(40, 100)
            
            for j in range(random.randint(2, 4)):
                # On even subnets, add services. On odd subnets, add workstations
                ip_address = net[offset+j]
                if i % 2 == 0:
                    workstation= get_baseline(item_type= "cluster", name=f'ClusterWorkstation_{workstation_count}', cluster_type='endpoint',
                                    nodes= [get_baseline(item_type='device', name=f'Workstation_{workstation_count}', device_type="Workstation", ip=f'{ip_address}', display_name=f'{services[i * 3 + j]}')])
                else: 
                    workstation= get_baseline(item_type= "cluster", name=f'ClusterWorkstation_{workstation_count}', cluster_type='endpoint',
                                    nodes= [get_baseline(item_type='device', name=f'Workstation_{workstation_count}', device_type="Workstation", ip=f'{ip_address}', display_name=f'User Workstation {user_count}')])
                    user_count += 1
                config.append(workstation)
                dmz["connections"].append(( f'ClusterWorkstation_{workstation_count}', "child", ("","")))
                workstation_count += 1
            
        return config
    
class IdentifyServices(WorkstationProblem):
    def __init__(self, cidr_blocks, subnets, q_type = "normal", folder = "exampleFiles", images_folder = "images"):
        self.to_identify = []
        super().__init__(cidr_blocks, subnets, show_names= False, q_type=q_type, folder= folder, images_folder=images_folder)
    
    def gen_answers(self) -> dict:
        answers = super().gen_answers()  
        
        servers = self.network.servers
        all_servers = [server.properties["PortsOpen"] for server in servers]
        all_servers_shuffled = random.sample(all_servers, len(all_servers))
        for i, server in enumerate(servers):
            server.name = self.ports_servers[all_servers_shuffled[i]]
            server.properties["PortsOpen"] = all_servers_shuffled[i]
        
        # Select Subset to identify
        self.to_identify = random.sample(servers, random.randint(2,min(len(servers), 4)))
        
        portsAnswer = ",".join([server.properties["PortsOpen"].replace(" ", ",") for server in self.to_identify])
            
        answers["portsAnswer"] = ['-p ' + portsAnswer]
        answers["ipAnswer"] = [self.services] # Only necessary if we have a services section
        # answers["ipAnswer"] = [" ".join([str(block) for block in self.cidr_blocks])]
        
        answers["leftAnswer"] = [server.name for server in self.to_identify]
        answers["rightAnswer"] = [server.ip for server in self.to_identify]
        self.answers = answers
        return answers
    
    def get_problem_defaults(self, prob_number: int) -> dict:
        blurbs = [self.servers_blurb[server.name] for server in self.to_identify]
        blurb_txt = ", ".join(blurbs[:-1]) + ", and " + blurbs[-1]
        probtxt = "The services section of our DMZ network should contain " \
            + blurb_txt \
            + '. All other services are prohibited on this network segment. Using nmap, identify which server is configured at which IP address. <strong>Scan only the services portion of the DMZ network.</strong>'
        defaults = {
                'probType': "Identify Services",
                'fixLeft': True,
                'oneColumn': False,
                'probtxt': probtxt,
                'title': f"Tutor: NMAP problem {prob_number}",
                'opQuestion': 'Based on the output, which server is which service?',
                'leftTitle': 'Server',
                'rightTitle': 'IP Address'
            }
        return defaults
        

class RogueWorkstations(WorkstationProblem):
    def gen_answers(self) -> dict:
        answers = super().gen_answers()
        answers["portsAnswer"] = ['']
        answers["ipAnswer"] =  [" ".join([str(block) for block in self.cidr_blocks])]

        rogue_num = random.randint(2, 4)
        # Workstation needs to be in example data, but not on the map.
        # Example data is generated from the network
        # Could add items directly to the network, and since map is already generated, that won't change things
            # Somehow I need to access cidr blocks to get ips that make sense but are not in use
        left_answer = []
        new_items_config = []
        get_baseline = super().get_baseline_dict
        used_ips = self.network.used_ips
        used_ints = [int(IPAddress(ip)) for ip in used_ips]
        for i in range(rogue_num):
            # block = random.sample(cidr_blocks, 1)[0]
            while True:
                # try one of our used IPs plus an offset
                candidate = random.choice(used_ints) + random.randint(1, 5)
                ip_address = str(IPAddress(candidate))
                if ip_address not in used_ips:
                    break
            workstation= get_baseline(item_type= "cluster", name=f'RogueWorkstationCluster_{i}', cluster_type='endpoint',
                            nodes= [get_baseline(item_type='device', name=f'RogueWorkstation_{i}', device_type="Workstation", ip=f'{ip_address}')])
            if ip_address not in left_answer: # avoid duplicates for now, will look into why duplicates occur later
                left_answer.append(ip_address)
            new_items_config.append(workstation)
        self.network.add_items_from_config(new_items_config)
        answers["leftAnswer"] = left_answer
        answers["rightAnswer"] = []
        self.answers = answers
        return answers
    
    def get_problem_defaults(self, prob_number: int) -> dict:
        defaults = {
                'probType': "Rogue Workstations",
                'fixLeft': False,
                'oneColumn': True,
                'probtxt': "<strong>Scan both the office network and the entire DMZ with one nmap command.</strong> Identify any unaccounted for machines on our corporate networks. The firewalls are configured to allow ICMP echo requests through.",
                'title': f"Tutor: NMAP problem {prob_number}",
                'opQuestion': 'Based on the output, list any rogue workstation IPs below:',
                'leftTitle': 'IP Address',
                'rightTitle': ''
            }
        return defaults

class UnresponsiveWorkstations(WorkstationProblem):

    def gen_answers(self) -> dict:
        answers = super().gen_answers()
        answers["portsAnswer"] = ['']
        answers["ipAnswer"] =  [" ".join([str(block) for block in self.cidr_blocks])]


        systems = self.network.systems

        unresponsive = random.sample(systems, random.randint(2, 4))
        self.network.remove_items(unresponsive)
        left_answer = [item.ip for item in unresponsive]
        right_answer = [item.display_name for item in unresponsive]
        answers["leftAnswer"] = left_answer
        answers["rightAnswer"] = right_answer
        self.answers = answers
        return answers
    
    def get_problem_defaults(self, prob_number: int) -> dict:
        defaults = {
                'probType': "Unresponsive Workstations",
                'fixLeft': False,
                'oneColumn': False,
                'probtxt': "Due to a bad update from a vendor, some of our systems are stuck in a boot loop and have become unresponsive. <strong>Scan the corporate network using a single nmap command and identify any systems that are affected</strong> so that technicans can be dispatched to roll back the update manually. The firewalls are configured to allow ICMP echo requests through.",
                'title': f"Tutor: NMAP problem {prob_number}",
                'opQuestion': 'Based on the output, list any unresponsive workstation IPs below:',
                'leftTitle': 'IP Address',
                'rightTitle': 'Workstation Name'
            }
        return defaults  