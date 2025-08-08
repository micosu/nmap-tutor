from typing import Optional, List, Dict, Any
from network import Network
from netaddr import IPNetwork, IPAddress
import random

class ProblemError(Exception):
    pass

class Problem():
    def __init__(self):
        pass

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
    
    def gen_config(self, cidr_blocks) -> list[dict[str, Any]]:
        return []
    
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
    
    def generate_answers(self, network: 'Network', cidr_blocks) -> dict:
        return self.get_answer_defaults()
    
    def generate_example_data(self, network: "Network") -> list[dict[str, str]]:
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
    
    def get_problem_defaults(self, prob_number: int) -> dict:
        return {}

    def gen_problem_dict(self, file_name: str, answers: dict, example_data: list, prob_number: int) -> dict:
        content = self.get_problem_defaults(prob_number)
        content["imgAddress"] = "Assets/" + file_name
        content.update(answers)
        content["exampledata"] = example_data
        return content
        



class BadPorts(Problem):
    def gen_config(self, cidr_blocks):
        config, router = super().start_config()
        has_user_loc = False
        workstation_count = 1
        get_baseline = super().get_baseline_dict
        
        for i in range(len(cidr_blocks)):
            net = cidr_blocks[i]
            firewall = get_baseline(item_type="device", device_type="Firewall", name=f'Firewall_{i}')
            router.setdefault("connections", []).append((f"Firewall_{i}", "child", (f"  {net[1]}  ", f"  {net[3]}  ")))

            # if i % 2 == 0:
            switch = get_baseline(item_type = "cluster", name=f'switch_cluster_{i}', cluster_type='intermediate', 
                            nodes= [get_baseline(item_type="device", name=f'Switch_{i}', device_type= 'Switch')])
            office = get_baseline(item_type = "cluster", name=f'Office_{i}', cluster_type='intermediate', ip= str(net),
                                nodes= [get_baseline(item_type="device", name= f'DomainController_{i}', device_type="Controller", ip= f'{net[10]}', display_name= 'Domain Controller')])
            config = config + [
                firewall,
                switch,
                office
            ]
            firewall["connections"] = [(f'switch_cluster_{i}', "same", (f"  {net[5]}  ", ""))]
            switch["connections"] = [(f'Office_{i}', "above", ("", ""))]
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
    
    def generate_answers(self, network: 'Network', cidr_blocks) -> dict:
        answers = super().generate_answers(network, cidr_blocks)
        
        answers["portsAnswer"] = ['-p 6881-6889']
        # Scan the relevant cidr blocks, or in this case, all of them
        answers["ipAnswer"] =  " ".join([str(block) for block in cidr_blocks])
        # answers["ipAnswer"] =  generate_all_nmap_options(cidr_blocks)
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
    
    def get_problem_defaults(self, prob_number: int) -> dict:
        defaults = {
                'probType': "Bad Ports",
                'fixLeft': False,
                'oneColumn': False,
                'probtxt': "We have received a DMCA complaint that someone is sharing copyrighted material from our corporate network via bittorrent. Conduct a scan with nmap to find out which workstation is responsible.   ( Bittorrent is known to use TCP ports in the range 6881 - 6889 )",
                'title': f"Tutor: NMAP problem {prob_number}",
                'opQuestion': 'Based on the output, which workstation is responsible?',
                'leftTitle': 'IP Address',
                'rightTitle': 'Workstation Number'
            }
        return defaults

class WorkstationProblem(Problem):
    def gen_config(self, cidr_blocks):
        config, router = super().start_config()
        has_user_loc = False
        workstation_count = 1
        server_count = 0
        get_baseline = super().get_baseline_dict
        
        for i in range(len(cidr_blocks)):
            net = cidr_blocks[i]
            firewall = get_baseline(item_type="device", device_type="Firewall", name=f'Firewall_{i}')
            router.setdefault("connections", []).append((f"Firewall_{i}", "child", (f"  {net[1]}  ", f"  {net[3]}  ")))

            dmz = get_baseline(item_type = "cluster", name=f'DMZ_{i}', cluster_type='intermediate', ip= str(net),
                                nodes= [get_baseline(item_type="device", name= f'Server_{server_count + j}', device_type="Server", ip= f'{net[10 + j]}', display_name= f'Server {server_count + j}') for j in range(1,4)])
            server_count += 3
            config = config + [
                firewall,
                dmz
                ]
            firewall["connections"] = [(f'DMZ_{i}', "same", (f"  {net[5]}  ", ""))]
            
            if not has_user_loc:
                dmz["connections"] = [("UserLocation", "above", ("", f"  {net[20]}  "))]
                has_user_loc = True
            else:
                dmz["connections"] = []

            offset = random.randint(40, 100)
            services = ["Kiosk Computer", "Digital Signage", "Vending Machine"]
            for j in range(1,random.randint(3, 4)):
                ip_address = net[offset+j]
                workstation= get_baseline(item_type= "cluster", name=f'ClusterWorkstation_{workstation_count}', cluster_type='endpoint',
                                nodes= [get_baseline(item_type='device', name=f'Workstation_{workstation_count}', device_type="Workstation", ip=f'{ip_address}', display_name=f'{services[j-1]}')])
                config.append(workstation)
                dmz["connections"].append(( f'ClusterWorkstation_{workstation_count}', "child", ("","")))
                workstation_count += 1
            
        return config
    
class IdentifyServices(WorkstationProblem):
    
    def generate_answers(self, network: 'Network', cidr_blocks) -> dict:
        answers = super().generate_answers(network, cidr_blocks)
        answers["portsAnswer"] = ['-p 80,443,25,465,587,2525,53']
        answers["ipAnswer"] =  " ".join([str(block) for block in cidr_blocks])
        servers = network.servers
        portsOpen = {
            "Web Server": "22 53 80 443",
            "Mail Server": "25 465 587 2525",
            "DNS Server": "53"
        }
        # Random ordering of servers so that the first one isn't always the Web Server
        left_answer = list(portsOpen.keys())
        right_answer = []
        for server, portOpen in zip(random.sample(servers, len(servers)), portsOpen.values()):
            server.properties["PortsOpen"] = portOpen
            right_answer.append(server.ip)
        
        answers["leftAnswer"] = left_answer
        answers["rightAnswer"] = right_answer

        return answers
    
    def get_problem_defaults(self, prob_number: int) -> dict:
        defaults = {
                'probType': "Identify Services",
                'fixLeft': True,
                'oneColumn': False,
                'probtxt': "The services section of our DMZ network should contain a web server hosting both secure and insecure web connections (HTTP on TCP port 80 and HTTPS on TCP port 443), a mail server (providing SMTP over TCP ports 25, 465, 587 and 2525), and a DNS server (providing DNS lookup over TCP port 53). All other services are prohibited on this network segment. Using nmap, identify which server is configured at which IP address. Scan only the services portion of the DMZ network.FOR THE LAST QUESTION, PLEASE PRESS ENTER EVEN IF THE FIELD IS PREFILLED. THANK YOU.",
                'title': f"Tutor: NMAP problem {prob_number}",
                'opQuestion': 'Based on the output, which workstation is responsible?',
                'leftTitle': 'Server',
                'rightTitle': 'IP Address'
            }
        return defaults
        

class RogueWorkstations(WorkstationProblem):
    def generate_answers(self, network: 'Network', cidr_blocks) -> dict:
        answers = super().generate_answers(network, cidr_blocks)
        answers["portsAnswer"] = ['']
        answers["ipAnswer"] =  " ".join([str(block) for block in cidr_blocks])
        servers = network.servers

        rogue_num = random.randint(1, 4)
        # Workstation needs to be in example data, but not on the map.
        # Example data is generated from the network
        # Could add items directly to the network, and since map is already generated, that won't change things
            # Somehow I need to access cidr blocks to get ips that make sense but are not in use
        left_answer = []
        right_answer = []
        new_items_config = []
        get_baseline = super().get_baseline_dict
        real_ws = network.workstations
        used = network.used_ips
        for i in range(rogue_num):
            block = random.sample(cidr_blocks, 1)[0]
            while True:
                rand_int = random.randint(block.first + 1, block.last -1)
                ip = str(IPAddress(rand_int))
                print(ip)
                break
            raise KeyError
            ip_address = net[offset+j]
            workstation= get_baseline(item_type= "cluster", name=f'RogueWorkstationCluster_{i}', cluster_type='endpoint',
                            nodes= [get_baseline(item_type='device', name=f'RogueWorkstation_{i}', device_type="Workstation", ip=f'{ip_address}')])
            new_items_config.append(workstation)

        network.add_items_from_config(new_items_config)
        answers["leftAnswer"] = left_answer
        answers["rightAnswer"] = right_answer

        return answers
    
    def get_problem_defaults(self, prob_number: int) -> dict:
        defaults = {
                'probType': "Rogue Workstations",
                'fixLeft': False,
                'oneColumn': True,
                'probtxt': "Scan both the office network and the entire DMZ with one nmap command. Identify any unaccounted for machines on our corporate networks. The firewalls are configured to allow ICMP echo requests through.",
                'title': f"Tutor: NMAP problem {prob_number}",
                'opQuestion': 'Based on the output, list any rogue workstation IPs below:',
                'leftTitle': 'IP Address',
                'rightTitle': ''
            }
        return defaults

class UnresponsiveWorkstations(WorkstationProblem):
    def get_problem_defaults(self, prob_number: int) -> dict:
        defaults = {
                'probType': "Unresponsive Workstations",
                'fixLeft': False,
                'oneColumn': False,
                'probtxt': "Due to a bad update from a vendor, some of our systems are stuck in a boot loop and have become unresponsive. Scan the corporate network using a single nmap command and identify any systems that are affected so that technicans can be dispatched to roll back the update manually. The firewalls are configured to allow ICMP echo requests through.",
                'title': f"Tutor: NMAP problem {prob_number}",
                'opQuestion': 'Based on the output, list any unresponsive workstation IPs below:',
                'leftTitle': 'IP Address',
                'rightTitle': 'Workstation Name'
            }
        return defaults  