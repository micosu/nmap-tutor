from graphviz import Digraph

# Create the graph with better formatting
dot = Digraph(format='png', graph_attr={
    'rankdir': 'TB',
    'splines': 'ortho', 
    'nodesep': '1.0',
    'ranksep': '1.5',
    'bgcolor': 'white',
    'fontname': 'Arial'
})

# Set default node attributes
dot.attr('node', fontname='Arial', fontsize='11')

# Option 1: Use Unicode symbols with HTML formatting for bigger symbols
dot.node('Internet', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><FONT POINT-SIZE="30">☁</FONT></TD></TR>
                     <TR><TD>Internet</TD></TR>
                   </TABLE>>''',
         shape='ellipse', 
         style='filled', 
         fillcolor='lightblue',
         width='1.5')

dot.node('BorderRouter', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><FONT POINT-SIZE="30">📡</FONT></TD></TR>
                     <TR><TD>Border Router</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">172.16.0.1</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='dodgerblue',
         fontcolor='white',
         width='1.8')

dot.node('Firewall', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><FONT POINT-SIZE="30">🛡</FONT></TD></TR>
                     <TR><TD>Firewall</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">172.16.0.2 - 172.16.0.3</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='lightgray',
         width='2.2')

dot.node('Switch', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><FONT POINT-SIZE="30">🔀</FONT></TD></TR>
                     <TR><TD>Switch</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">172.16.5.5</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='dodgerblue',
         fontcolor='white',
         width='1.8')

dot.node('DomainController', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                     <TR><TD>Domain Controller</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">172.16.9.10</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='dodgerblue',
         fontcolor='white',
         width='2.0')

dot.node('Office', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><FONT POINT-SIZE="30">🏢</FONT></TD></TR>
                     <TR><TD>Office</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">172.16.0.0/12</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='lightblue',
         width='2.0')

# Workstations
for i in range(1, 4):
    dot.node(f'Workstation{i}', 
             label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                         <TR><TD><FONT POINT-SIZE="30">💻</FONT></TD></TR>
                         <TR><TD>User Workstation {i}</TD></TR>
                         <TR><TD><FONT POINT-SIZE="10">172.16.31.{100+i}</FONT></TD></TR>
                       </TABLE>>''',
             shape='box', 
             style='filled,rounded', 
             fillcolor='lightblue',
             width='2.0')

# You Are Connected Here
dot.node('UserLocation', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><FONT POINT-SIZE="30">📍</FONT></TD></TR>
                     <TR><TD>You Are</TD></TR>
                     <TR><TD>Connected Here</TD></TR>
                   </TABLE>>''',
         shape='ellipse', 
         style='filled', 
         fillcolor='plum',
         width='1.8')

# Create connections
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
dot.render('network_diagram_simple', cleanup=True)
print("Simple, reliable network diagram created!")

# ============================================
# BONUS: Alternative with shape-based icons
# ============================================

dot2 = Digraph('alternative', format='png', graph_attr={
    'rankdir': 'TB',
    'splines': 'ortho',
    'nodesep': '1.0', 
    'ranksep': '1.5',
    'bgcolor': 'white'
})

# Use different shapes to represent different device types
dot2.node('Internet', 
          label='Internet', 
          shape='ellipse', 
          style='filled', 
          fillcolor='lightblue',
          width='1.5')

dot2.node('BorderRouter', 
          label='Border Router\n172.16.0.1', 
          shape='cylinder',  # Router = cylinder
          style='filled', 
          fillcolor='dodgerblue',
          fontcolor='white',
          width='1.5',
          height='1.0')

dot2.node('Firewall', 
          label='Firewall\n172.16.0.2 - 172.16.0.3', 
          shape='diamond',  # Firewall = diamond
          style='filled', 
          fillcolor='orange',
          width='2.5',
          height='1.5')

dot2.node('Switch', 
          label='Switch\n172.16.5.5', 
          shape='box', 
          style='filled,rounded', 
          fillcolor='dodgerblue',
          fontcolor='white',
          width='1.8')

dot2.node('DomainController', 
          label='Domain Controller\n172.16.9.10', 
          shape='box3d',  # Server = 3D box
          style='filled', 
          fillcolor='green',
          fontcolor='white',
          width='2.0')

dot2.node('Office', 
          label='Office\n172.16.0.0/12', 
          shape='folder',  # Network = folder
          style='filled', 
          fillcolor='lightblue',
          width='2.0')

for i in range(1, 4):
    dot2.node(f'Workstation{i}', 
              label=f'Workstation {i}\n172.16.31.{100+i}', 
              shape='note',  # Workstation = note shape
              style='filled', 
              fillcolor='lightblue',
              width='1.8')

dot2.node('UserLocation', 
          label='You Are\nConnected Here', 
          shape='ellipse', 
          style='filled', 
          fillcolor='plum',
          width='1.8')

# Same connections
dot2.edge('Internet', 'BorderRouter', xlabel='128.237.3.102')
dot2.edge('BorderRouter', 'Firewall', xlabel='172.16.0.1')
dot2.edge('Firewall', 'Switch', xlabel='172.16.0.3')
dot2.edge('Switch', 'DomainController')
dot2.edge('DomainController', 'Office')
dot2.edge('Switch', 'Workstation1')
dot2.edge('Switch', 'Workstation2') 
dot2.edge('Switch', 'Workstation3')
dot2.edge('Switch', 'UserLocation', xlabel='172.16.5.5')

dot2.render('network_diagram_shapes', cleanup=True)
print("Shape-based network diagram created!")
print("\nBoth approaches created! Check out:")
print("1. network_diagram_simple.png (Unicode symbols)")
print("2. network_diagram_shapes.png (Different shapes)")