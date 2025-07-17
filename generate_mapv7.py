import pygraphviz as pgv

# Create the main graph with attributes
G = pgv.AGraph(directed=True, strict=False)

# Set graph attributes - MUST use neato for absolute positioning
G.graph_attr.update({
    'layout': 'neato',  # Required for pos attribute
    'compound': 'true',
    'splines': 'ortho',
    'bgcolor': 'white',
    'fontname': 'Arial',
    'overlap': 'false'  # Prevents node overlap
})

# Set default node attributes
G.node_attr.update({
    'fontname': 'Arial',
    'fontsize': '11'
})

# Core infrastructure nodes with absolute positions
G.add_node('Internet', 
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">☁</FONT></TD></TR>
                        <TR><TD>Internet</TD></TR>
                      </TABLE>>''',
           shape='ellipse',
           style='filled',
           fillcolor='lightblue',
           width='1.5',
           pos='2,4!')  # Top center

G.add_node('UserLocation',
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">📍</FONT></TD></TR>
                        <TR><TD>You Are</TD></TR>
                        <TR><TD>Connected Here</TD></TR>
                      </TABLE>>''',
           shape='ellipse',
           style='filled',
           fillcolor='plum',
           pos='6,4!')  # Top right

# Middle row - same Y coordinate for horizontal alignment
G.add_node('Firewall1',
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">🛡</FONT></TD></TR>
                        <TR><TD>Firewall</TD></TR>
                        <TR><TD><FONT POINT-SIZE="10">10.2.3.5</FONT></TD></TR>
                      </TABLE>>''',
           shape='box',
           style='filled,rounded',
           fillcolor='orange',
           pos='0,2!')  # Left side

G.add_node('BorderRouter',
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">📡</FONT></TD></TR>
                        <TR><TD>Border Router</TD></TR>
                        <TR><TD><FONT POINT-SIZE="10">10.2.4.2</FONT></TD></TR>
                      </TABLE>>''',
           shape='box',
           style='filled,rounded',
           fillcolor='dodgerblue',
           fontcolor='white',
           pos='3,2!')  # Center

G.add_node('Firewall2',
           label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                        <TR><TD><FONT POINT-SIZE="30">🛡</FONT></TD></TR>
                        <TR><TD>Firewall</TD></TR>
                        <TR><TD><FONT POINT-SIZE="10">10.2.4.6</FONT></TD></TR>
                      </TABLE>>''',
           shape='box',
           style='filled,rounded',
           fillcolor='orange',
           pos='6,2!')  # Right side

# Create DMZ subgraph
dmz = G.add_subgraph(name='cluster_dmz')
dmz.graph_attr.update({
    'label': 'DMZ - 10.2.3.0/24',
    'style': 'filled,rounded',
    'fillcolor': 'lightgray',
    'fontsize': '12'
})

# DMZ Servers - positioned horizontally below Firewall1
dmz.add_node('Server1',
             label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                          <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                          <TR><TD>Server 1</TD></TR>
                          <TR><TD><FONT POINT-SIZE="10">10.2.3.20</FONT></TD></TR>
                        </TABLE>>''',
             shape='box',
             style='filled,rounded',
             fillcolor='dodgerblue',
             fontcolor='white',
             pos='-1.5,0!')  # Bottom left

dmz.add_node('Server2',
             label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                          <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                          <TR><TD>Server 2</TD></TR>
                          <TR><TD><FONT POINT-SIZE="10">10.2.3.21</FONT></TD></TR>
                        </TABLE>>''',
             shape='box',
             style='filled,rounded',
             fillcolor='dodgerblue',
             fontcolor='white',
             pos='0,0!')  # Bottom center-left

dmz.add_node('Server3',
             label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                          <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                          <TR><TD>Server 3</TD></TR>
                          <TR><TD><FONT POINT-SIZE="10">10.2.3.22</FONT></TD></TR>
                        </TABLE>>''',
             shape='box',
             style='filled,rounded',
             fillcolor='dodgerblue',
             fontcolor='white',
             pos='1.5,0!')  # Bottom center-right

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
                fontcolor='white',
                pos='6,0!')  # Bottom right

# Office Workstations - positioned horizontally
office.add_node('Workstation1',
               label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                            <TR><TD><FONT POINT-SIZE="30">💻</FONT></TD></TR>
                            <TR><TD>User Workstation 1</TD></TR>
                            <TR><TD><FONT POINT-SIZE="10">10.2.4.50</FONT></TD></TR>
                          </TABLE>>''',
               shape='box',
               style='filled,rounded',
               fillcolor='lightblue',
               pos='7.5,0!')

office.add_node('Workstation2',
               label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                            <TR><TD><FONT POINT-SIZE="30">💻</FONT></TD></TR>
                            <TR><TD>User Workstation 2</TD></TR>
                            <TR><TD><FONT POINT-SIZE="10">10.2.4.51</FONT></TD></TR>
                          </TABLE>>''',
               shape='box',
               style='filled,rounded',
               fillcolor='lightblue',
               pos='9,0!')

office.add_node('Workstation3',
               label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                            <TR><TD><FONT POINT-SIZE="30">💻</FONT></TD></TR>
                            <TR><TD>User Workstation 3</TD></TR>
                            <TR><TD><FONT POINT-SIZE="10">10.2.4.52</FONT></TD></TR>
                          </TABLE>>''',
               shape='box',
               style='filled,rounded',
               fillcolor='lightblue',
               pos='10.5,0!')

# Create connections
G.add_edge('Internet', 'BorderRouter', xlabel='128.237.3.102', dir='none')

# To DMZ (left side)
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
# User Workstation - 💻
# Render the graph - no need to call layout() separately when using neato
G.layout(prog="neato")
G.draw('network_diagram_positioned.png', format='png')
print("Positioned network diagram created!")

# Optional: You can also save as other formats
# G.draw('network_diagram_positioned.svg', format='svg')
# G.draw('network_diagram_positioned.pdf', format='pdf')

print("\n=== Position Information ===")
print("Layout: Y=4 (top), Y=2 (middle), Y=0 (bottom)")
print("DMZ servers are horizontally spaced at Y=0")
print("Office devices are horizontally spaced at Y=0")
print("All positioning is absolute and controlled by pos='x,y!' attributes")