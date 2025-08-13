import pygraphviz as pgv
# pyright: reportAttributeAccessIssue=false

nmap = pgv.AGraph(directed=False, strict=False)

# Set graph attributes for neato
nmap.graph_attr.update({
    'compound': 'true',
    'splines': 'polyline',
    'bgcolor': 'white',
    'fontname': 'Arial',
    'overlap': 'false'  # Prevents node overlap with neato
})

nmap.node_attr.update({
    'fontname': 'Arial',
    'fontsize': '14'
})
x_spacing = .75
y_spacing = .5
internal_spacing = .25
# Top row - Internet
nmap.add_node('Internet', 
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">☁</FONT></TD></TR>
                        <TR><TD>Internet</TD></TR>
                      </TABLE>>''',
           shape='ellipse',
           style='filled',
           fillcolor='lightblue',
           width='1.5',
           pos=f'0,{y_spacing}!')  # Top center

# Middle row - all on same horizontal level
nmap.add_node('Firewall1', 
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">🛡</FONT></TD></TR>
                        <TR><TD>Firewall</TD></TR>
                      </TABLE>>''',
           shape='square',
           style='filled',
           fillcolor='lightgrey',
           width='1.5',
           pos=f'-{x_spacing},0!')  # Middle left

nmap.add_node('BorderRouter', 
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">📡</FONT></TD></TR>
                        <TR><TD>Border Router</TD></TR>
                      </TABLE>>''',
           shape='cylinder',
           style='filled',
           fillcolor='lightblue',
           width='1.5',
           pos='0,0!')  # Middle center

nmap.add_node('Firewall2', 
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">🛡</FONT></TD></TR>
                        <TR><TD>Firewall</TD></TR>
                      </TABLE>>''',
           shape='square',
           style='filled',
           fillcolor='lightgrey',
           width='1.5',
           pos=f'{x_spacing},0!')  # Middle right

# Create DMZ cluster
dmz = nmap.add_subgraph(name="cluster_dmz")
dmz.graph_attr.update({
    # 'label': 'DMZ - 102.3.0/24',
    'style': 'filled,rounded',
    'fillcolor': '#218dbb',
    'fontsize': '12',
})

# DMZ Servers - positioned horizontally below Firewall1
for i in range(1, 4):
    # x * 1 + y = -5
    # x * 2 + y = -4
    # x * 3 + y = -3

    print("Positions: ", i*internal_spacing-x_spacing*3)
    dmz.add_node(f'Server{i}',
                   label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                                <TR><TD>Server {i}</TD></TR>
                                <TR><TD><FONT POINT-SIZE="30">🗄️</FONT></TD></TR>
                                <TR><TD><FONT POINT-SIZE="20">10.2.3.{20+i}</FONT></TD></TR>
                              </TABLE>>''',
                   shape='none',
                   width=".5",
                   fontcolor='white',
                   pos=f'{i*internal_spacing-x_spacing*3},0!')  # Bottom row, spaced horizontally
print("Server2 Position: ", )
dmz_label_x = nmap.get_node('Server2').attr['pos'].split(",")[0]
nmap.add_node('DMZ_Label',
              label='DMZ - 10.2.3.0/24',
              shape='rectangle',  # Invisible node, just text
              style='filled,rounded',
              color='lightblue',
              fontsize='12',
              pos=f'{dmz_label_x},.2!') 

nmap.add_node('UserLocation', 
              label='You Are Conneted Here',
              shape='ellipse',
              color='#CCA4D3',
              style='filled',
              fontsize='12',
              pos=f'-{3*x_spacing/2},{y_spacing/1.5}!')

for i in range(1, 4):
    names = ["Kiosk Computer", "Digital Signage", "Vending Machine"]
    # Create individual cluster for each workstation
    service_cluster = nmap.add_subgraph(name=f"cluster_service{i}")
    service_cluster.graph_attr.update({
        'style': 'filled,rounded',
        'fillcolor': 'lightblue',  # Lighter blue like in your image
        'fontsize': '10',
    })
    
    service_cluster.add_node(f'DMZ_Service{i}',
                       label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                                    <TR><TD>{names[i-1]}</TD></TR>
                                    <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                                    <TR><TD><FONT POINT-SIZE="15">10.2.3.{49+i}</FONT></TD></TR>
                                  </TABLE>>''',
                       shape='none',
                       width=".5",
                       fontcolor='black',  # Black text for light blue background
                       pos=f'{i*internal_spacing-x_spacing*3},-{y_spacing}!')


office = nmap.add_subgraph(name="cluster_office")
office.graph_attr.update({
    # 'label': 'DMZ - 102.3.0/24',
    'style': 'filled,rounded',
    'fillcolor': '#218dbb',
    'fontsize': '12',
})


office.add_node(f'DomainController',
                label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                            <TR><TD>Domain Controller</TD></TR>
                            <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                            <TR><TD><FONT POINT-SIZE="20">10.2.4.20</FONT></TD></TR>
                            </TABLE>>''',
                shape='none',
                fontcolor='white',
                width=".5",
                pos=f'{x_spacing*2},0!')  # Bottom row, spaced horizontally

print("DC Position: ", )
office_label_x = nmap.get_node('DomainController').attr['pos'].split(",")[0]
nmap.add_node('Office_Label',
              label='Office - 10.2.4.20/24',
              shape='rectangle',  # Invisible node, just text
              style='filled,rounded',
              color='lightblue',
              fontsize='12',
              pos=f'{office_label_x},.2!') 

for i in range(1, 4):
    # Create individual cluster for each workstation
    workstation_cluster = nmap.add_subgraph(name=f"cluster_workstation{i}")
    workstation_cluster.graph_attr.update({
        'style': 'filled,rounded',
        'fillcolor': 'lightblue',  # Lighter blue like in your image
        'fontsize': '10',
    })
    print(f"Workstation Postions: {i*internal_spacing+x_spacing*(4/3)},-1!")
    # 2 * .25 + .75 * x = 1.5
    
    workstation_cluster.add_node(f'Workstation{i}',
                       label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                                    <TR><TD>User Workstation {i}</TD></TR>
                                    <TR><TD><FONT POINT-SIZE="30">💻</FONT></TD></TR>
                                    <TR><TD><FONT POINT-SIZE="15">10.2.4.{49+i}</FONT></TD></TR>
                                  </TABLE>>''',
                       shape='none',
                       width=".5",
                       fontcolor='black',  # Black text for light blue background
                       pos=f'{i*internal_spacing+x_spacing*(4/3)},-{y_spacing}!')

# Add all your edges to the MAIN graph (nmap), not subgraphs
nmap.add_edge('Internet', 'BorderRouter', taillabel=' 128.237.3.102 ')
nmap.add_edge('BorderRouter', 'Firewall1', headlabel='  10.2.3.2  ', taillabel='  10.2.3.5  ')
nmap.add_edge('BorderRouter', 'Firewall2', headlabel='  10.2.4.4  ', taillabel='  10.2.4.2  ')

# Connect DMZ to Firewall1
nmap.add_edge('Server3', 'Firewall1', headlabel='  10.2.3.7  ', taillabel="")
nmap.add_edge('Server3', 'UserLocation', headlabel='  10.2.3.9  ')
# Connect DMZ to Services
for i in range(1, 4):
    nmap.add_edge('Server2', f'DMZ_Service{i}')

# Connect Office to Firewall2
nmap.add_edge('Firewall2', 'DomainController', taillabel='  10.2.4.6  ')

for i in range(1, 4):
    nmap.add_edge('DomainController', f'Workstation{i}')

# Use neato layout with absolute positioning
nmap.layout(prog='neato')
nmap.draw('Michael_diagram_pygraphviz.png', format='png')
print("PyGraphviz network diagram created with neato!")

print("\n=== Positioning Info ===")
location = nmap.get_node("UserLocation").attr["pos"]
print(location)