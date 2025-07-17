import pygraphviz as pgv

# Create the main graph with attributes
G = pgv.AGraph(directed=True, strict=False)

# Set graph attributes
G.graph_attr.update({
    'rankdir': 'TB',
    'compound': 'true',
    'splines': 'ortho',
    'nodesep': '1.0',
    'ranksep': '1.5',
    'bgcolor': 'white',
    'fontname': 'Arial'
})

# Set default node attributes
G.node_attr.update({
    'fontname': 'Arial',
    'fontsize': '11'
})

# Core infrastructure nodes
G.add_node('Internet', 
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">☁</FONT></TD></TR>
                        <TR><TD>Internet</TD></TR>
                      </TABLE>>''',
           shape='ellipse',
           style='filled',
           fillcolor='lightblue',
           width='1.5')

G.add_node('BorderRouter',
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">📡</FONT></TD></TR>
                        <TR><TD>Border Router</TD></TR>
                        <TR><TD><FONT POINT-SIZE="10">10.2.4.2</FONT></TD></TR>
                      </TABLE>>''',
           shape='box',
           style='filled,rounded',
           fillcolor='dodgerblue',
           fontcolor='white')

# DMZ Firewall
G.add_node('Firewall1',
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">🛡</FONT></TD></TR>
                        <TR><TD>Firewall</TD></TR>
                        <TR><TD><FONT POINT-SIZE="10">10.2.3.5</FONT></TD></TR>
                      </TABLE>>''',
           shape='box',
           style='filled,rounded',
           fillcolor='orange')


# Office Firewall
G.add_node('Firewall2',
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">🛡</FONT></TD></TR>
                        <TR><TD>Firewall</TD></TR>
                        <TR><TD><FONT POINT-SIZE="10">10.2.4.6</FONT></TD></TR>
                      </TABLE>>''',
           shape='box',
           style='filled,rounded',
           fillcolor='orange')

G.add_node('UserLocation',
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">📍</FONT></TD></TR>
                        <TR><TD>You Are</TD></TR>
                        <TR><TD>Connected Here</TD></TR>
                      </TABLE>>''',
           shape='ellipse',
           style='filled',
           fillcolor='plum')



# Create DMZ subgraph
dmz = G.add_subgraph(name='cluster_dmz')
dmz.graph_attr.update({
    'label': 'DMZ - 10.2.3.0/24',
    'style': 'filled,rounded',
    'fillcolor': 'lightgray',
    'fontsize': '12'
})

# DMZ Servers
dmz.add_node('Server1',
             label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                          <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                          <TR><TD>Server 1</TD></TR>
                          <TR><TD><FONT POINT-SIZE="10">10.2.3.20</FONT></TD></TR>
                        </TABLE>>''',
             shape='box',
             style='filled,rounded',
             fillcolor='dodgerblue',
             fontcolor='white')

dmz.add_node('Server2',
             label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                          <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                          <TR><TD>Server 2</TD></TR>
                          <TR><TD><FONT POINT-SIZE="10">10.2.3.21</FONT></TD></TR>
                        </TABLE>>''',
             shape='box',
             style='filled,rounded',
             fillcolor='dodgerblue',
             fontcolor='white')

dmz.add_node('Server3',
             label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                          <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                          <TR><TD>Server 3</TD></TR>
                          <TR><TD><FONT POINT-SIZE="10">10.2.3.22</FONT></TD></TR>
                        </TABLE>>''',
             shape='box',
             style='filled,rounded',
             fillcolor='dodgerblue',
             fontcolor='white')

# Create Office subgraph
office = G.add_subgraph(name='cluster_office')
office.graph_attr.update({
    'label': 'Office - 10.2.4.0/24',
    'style': 'filled,rounded',
    'fillcolor': 'lightgray',
    'fontsize': '12'
})

office.add_node('DomainController',
                label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                             <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                             <TR><TD>Domain Controller</TD></TR>
                             <TR><TD><FONT POINT-SIZE="10">10.2.4.20</FONT></TD></TR>
                           </TABLE>>''',
                shape='box',
                style='filled,rounded',
                fillcolor='red',
                fontcolor='white')

# Office Workstations
for i in range(1, 4):
    office.add_node(f'Workstation{i}',
                   label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                                <TR><TD><FONT POINT-SIZE="30">💻</FONT></TD></TR>
                                <TR><TD>User Workstation {i}</TD></TR>
                                <TR><TD><FONT POINT-SIZE="10">10.2.4.{49+i}</FONT></TD></TR>
                              </TABLE>>''',
                   shape='box',
                   style='filled,rounded',
                   fillcolor='lightblue')

# Set rank constraints using node attributes instead of subgraphs
# This approach works better with PyGraphviz
G.get_node('Internet').attr['rank'] = '1'
G.get_node('UserLocation').attr['rank'] = '1'

G.get_node('Firewall1').attr['rank'] = '3'  
G.get_node('BorderRouter').attr['rank'] = '2'
G.get_node('Firewall2').attr['rank'] = '3'

# Create connections
G.add_edge('Internet', 'BorderRouter', xlabel='128.237.3.102', dir='none')

# To DMZ (left side)
G.add_edge('BorderRouter', 'Firewall1', dir='none')
G.add_edge('Firewall1', 'BorderRouter', dir='none')
G.add_edge('Firewall1', 'Server2', dir='none', lhead='cluster_dmz')

# To Office (right side)
G.add_edge('BorderRouter', 'Firewall2', dir='none')
G.add_edge('Firewall2', 'DomainController', dir='none')
G.add_edge('Firewall2', 'Workstation1', dir='none')
G.add_edge('Firewall2', 'Workstation2', dir='none')
G.add_edge('Firewall2', 'Workstation3', dir='none')

# User connection
G.add_edge('BorderRouter', 'UserLocation', xlabel='10.2.3.9', dir='none')

# Render the graph
G.layout(prog='dot')  # Use dot layout algorithm
G.draw('network_diagram_pygraphviz.png', format='png')
print("PyGraphviz network diagram created!")

# Optional: You can also save as other formats
# G.draw('network_diagram_pygraphviz.svg', format='svg')
# G.draw('network_diagram_pygraphviz.pdf', format='pdf')

# Example of PyGraphviz's node manipulation capabilities:
print("\n=== PyGraphviz Node Manipulation Examples ===")

# Access and modify individual nodes
internet_node = G.get_node('Internet')
print(f"Internet node attributes: {internet_node.attr}")

# You can modify node attributes after creation
user_node = G.get_node('UserLocation')
print(f"UserLocation fillcolor before: {user_node.attr['fillcolor']}")
# user_node.attr['fillcolor'] = 'lightgreen'  # Uncomment to change color

# Get node position after layout (requires layout to be called first)
G.layout(prog='dot')
print(f"BorderRouter position: {G.get_node('BorderRouter').attr['pos']}")

# You can iterate through all nodes
print("All nodes in graph:")
for node in G.nodes():
    print(f"  {node}")

# You can access subgraph nodes
print("Nodes in DMZ subgraph:")
dmz_subgraph = G.get_subgraph('cluster_dmz')
for node in dmz_subgraph.nodes():
    print(f"  {node}")

# You can modify edges
edge = G.get_edge('Internet', 'BorderRouter')
print(f"Internet->BorderRouter edge attributes: {edge.attr}")

print("\nThis level of control is what makes PyGraphviz powerful!")