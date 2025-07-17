from graphviz import Digraph

# Create the main graph with left-to-right layout
dot = Digraph(format='png', graph_attr={
    'rankdir': 'TB',  # Back to Top-Bottom for better control
    'compound': 'true',
    'splines': 'ortho', 
    'nodesep': '1.0',
    'ranksep': '1.5',
    'bgcolor': 'white',
    'fontname': 'Arial'
})

# Set default node attributes
dot.attr('node', fontname='Arial', fontsize='11')

# Core infrastructure nodes (center column)
dot.node('Internet', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><FONT POINT-SIZE="30">☁</FONT></TD></TR>
                     <TR><TD>Internet</TD></TR>
                   </TABLE>>''',
         shape='ellipse', 
         style='filled', 
         fillcolor='lightblue',
         width='1.5')
# DMZ Firewall (connects to left side)
dot.node('Firewall1', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><FONT POINT-SIZE="30">🛡</FONT></TD></TR>
                     <TR><TD>Firewall</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">10.2.3.5</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='orange')

dot.node('BorderRouter', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><FONT POINT-SIZE="30">📡</FONT></TD></TR>
                     <TR><TD>Border Router</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">10.2.4.2</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='dodgerblue',
         fontcolor='white')

dot.node('UserLocation', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><FONT POINT-SIZE="30">📍</FONT></TD></TR>
                     <TR><TD>You Are</TD></TR>
                     <TR><TD>Connected Here</TD></TR>
                   </TABLE>>''',
         shape='ellipse', 
         style='filled', 
         fillcolor='plum')



# Office Firewall (connects to right side)
dot.node('Firewall2', 
         label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                     <TR><TD><FONT POINT-SIZE="30">🛡</FONT></TD></TR>
                     <TR><TD>Firewall</TD></TR>
                     <TR><TD><FONT POINT-SIZE="10">10.2.4.6</FONT></TD></TR>
                   </TABLE>>''',
         shape='box', 
         style='filled,rounded', 
         fillcolor='orange')

# Create subgraph for DMZ (left side)
with dot.subgraph(name='cluster_dmz') as dmz:
    dmz.attr(label='DMZ - 10.2.3.0/24', style='filled,rounded', fillcolor='lightgray', fontsize='12')
    
    # DMZ Services
    dmz.node('Server1', 
             label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                         <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                         <TR><TD>Server 1</TD></TR>
                         <TR><TD><FONT POINT-SIZE="10">10.2.3.20</FONT></TD></TR>
                       </TABLE>>''',
             shape='box', 
             style='filled,rounded', 
             fillcolor='dodgerblue',
             fontcolor='white')
    
    dmz.node('Server2', 
             label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                         <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                         <TR><TD>Server 2</TD></TR>
                         <TR><TD><FONT POINT-SIZE="10">10.2.3.21</FONT></TD></TR>
                       </TABLE>>''',
             shape='box', 
             style='filled,rounded', 
             fillcolor='dodgerblue',
             fontcolor='white')
    
    dmz.node('Server3', 
             label='''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                         <TR><TD><FONT POINT-SIZE="30">🖥</FONT></TD></TR>
                         <TR><TD>Server 3</TD></TR>
                         <TR><TD><FONT POINT-SIZE="10">10.2.3.22</FONT></TD></TR>
                       </TABLE>>''',
             shape='box', 
             style='filled,rounded', 
             fillcolor='dodgerblue',
             fontcolor='white')
    

# Create subgraph for Office (right side)
with dot.subgraph(name='cluster_office') as office:
    office.attr(label='Office - 10.2.4.0/24', style='filled,rounded', fillcolor='lightgray', fontsize='12')
    
    office.node('DomainController', 
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
        office.node(f'Workstation{i}', 
                   label=f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
                               <TR><TD><FONT POINT-SIZE="30">💻</FONT></TD></TR>
                               <TR><TD>User Workstation {i}</TD></TR>
                               <TR><TD><FONT POINT-SIZE="10">10.2.4.{49+i}</FONT></TD></TR>
                             </TABLE>>''',
                   shape='box', 
                   style='filled,rounded', 
                   fillcolor='lightblue')

with dot.subgraph() as s:
    s.attr(rank='same')
    s.node('Internet')
    s.node('UserLocation') 

# Use rank constraints to force horizontal alignment
with dot.subgraph() as s:
    s.attr(rank='same')
    s.node('Firewall1')
    s.node('BorderRouter') 
    s.node('Firewall2')

# Create connections
dot.edge('Internet', 'BorderRouter', xlabel='128.237.3.102', dir='none')

# To DMZ (left side)
dot.edge('Firewall1', 'BorderRouter', dir='none')
# dot.edge('Firewall1', 'cluster_dmz', dir='none')
dot.edge('Firewall1', 'Server2', dir='none', lhead='cluster_dmz') 
# dot.edge('Firewall1', 'Server3', dir='none')

# To Office (right side)
dot.edge('BorderRouter', 'Firewall2', dir='none')
dot.edge('Firewall2', 'DomainController', dir='none')
dot.edge('Firewall2', 'Workstation1', dir='none')
dot.edge('Firewall2', 'Workstation2', dir='none') 
dot.edge('Firewall2', 'Workstation3', dir='none')

# User connection
dot.edge('BorderRouter', 'UserLocation', xlabel='10.2.3.9', dir='none')

# Render the graph
dot.render('network_diagram_layout_controlled', cleanup=True)
print("Layout-controlled network diagram created!")