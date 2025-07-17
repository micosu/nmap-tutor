from graphviz import Digraph

# Create the graph with better formatting
dot = Digraph(format='png', graph_attr={
    'rankdir': 'TB',  # Top to bottom layout
    'splines': 'ortho',  # Orthogonal edges (straight lines)
    'nodesep': '1.0',  # Space between nodes
    'ranksep': '1.5',  # Space between ranks
    'bgcolor': 'white'
})

# Internet/Cloud - using icon
dot.node('Internet', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><IMG SRC="icons/cloud.png" SCALE="TRUE"/></TD></TR>
                     <TR><TD>Internet</TD></TR>
                   </TABLE>>''',
         shape='ellipse', 
         style='filled', 
         fillcolor='lightblue',
         width='1.5')

# Border Router - using icon
dot.node('BorderRouter', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><IMG SRC="icons/router.png" SCALE="TRUE"/></TD></TR>
                     <TR><TD>Border Router</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">172.16.0.1</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='dodgerblue',
         width='1.8')

# Switch - using icon
dot.node('Switch', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><IMG SRC="icons/switch.png" SCALE="TRUE"/></TD></TR>
                     <TR><TD>Switch</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">172.16.5.5</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='dodgerblue',
         width='1.8')

# Firewall - using icon
dot.node('Firewall', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><IMG SRC="icons/firewall.jpg" SCALE="TRUE"/></TD></TR>
                     <TR><TD>Firewall</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">172.16.0.2 - 172.16.0.3</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='lightgray',
         width='2.2')

# Domain Controller - using icon  
dot.node('DomainController', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><IMG SRC="icons/server.png" SCALE="TRUE"/></TD></TR>
                     <TR><TD>Domain Controller</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">172.16.9.10</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='dodgerblue',
         width='2.0')

# Office Network
dot.node('Office', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><IMG SRC="icons/cloud.png" SCALE="TRUE"/></TD></TR>
                     <TR><TD>Office</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">172.16.0.0/12</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='lightblue',
         width='2.0')

# User Workstations - using icons
for i in range(1, 4):
    dot.node(f'Workstation{i}', 
             label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                         <TR><TD><IMG SRC="icons/workstation.jpg" SCALE="TRUE"/></TD></TR>
                         <TR><TD>User Workstation {i}</TD></TR>
                         <TR><TD><FONT POINT-SIZE="10">172.16.31.{100+i}</FONT></TD></TR>
                       </TABLE>>''',
             shape='box', 
             style='filled,rounded', 
             fillcolor='lightblue',
             width='2.0')

# You Are Connected Here
dot.node('UserLocation', 
         label='You Are\nConnected Here', 
         shape='ellipse', 
         style='filled', 
         fillcolor='plum',
         width='1.5')

# Create connections (using xlabel to avoid orthogonal edge warning)
dot.edge('Internet', 'BorderRouter', xlabel='128.237.3.102')
dot.edge('BorderRouter', 'Firewall', xlabel='172.16.0.1')
dot.edge('Firewall', 'Switch', xlabel='172.16.0.3')
dot.edge('Switch', 'DomainController')
dot.edge('DomainController', 'Office')
dot.edge('Switch', 'Workstation1')
dot.edge('Switch', 'Workstation2') 
dot.edge('Switch', 'Workstation3')
dot.edge('Switch', 'UserLocation', xlabel='172.16.5.5')

# Render the graph
dot.render('network_diagram_with_icons', cleanup=True)
print("Network diagram with icons created as 'network_diagram_with_icons.png'")