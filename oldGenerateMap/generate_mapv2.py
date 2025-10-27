from graphviz import Digraph

# Create the graph with better formatting
dot = Digraph(format='png', graph_attr={
    'rankdir': 'TB',
    'splines': 'ortho',
    'nodesep': '1.0',
    'ranksep': '1.5',
    'bgcolor': 'white'
})

# Method 1: Use subgraphs with clusters to put icons inside bubbles
def create_node_with_icon_cluster(cluster_name, icon_path, main_label, sub_label, fillcolor='lightblue'):
    with dot.subgraph(name=f'cluster_{cluster_name}') as cluster:
        cluster.attr(style='filled,rounded', fillcolor=fillcolor, label='')
        
        # Icon node inside cluster
        cluster.node(f'{cluster_name}_icon', 
                    image=icon_path,
                    shape='none',
                    width='0.6',
                    height='0.4',
                    fixedsize='true',
                    label='')
        
        # Text node inside cluster  
        if sub_label:
            label_text = f'{main_label}\\n{sub_label}'
        else:
            label_text = main_label
            
        cluster.node(f'{cluster_name}_text',
                    label=label_text,
                    shape='plaintext',
                    fontsize='12')
        
        # Connect icon to text invisibly to maintain layout
        cluster.edge(f'{cluster_name}_icon', f'{cluster_name}_text', style='invis')
    
    return f'{cluster_name}_text'

# Method 2: Alternative using HTML with better icon positioning
def create_node_with_icon_html(node_id, icon_path, main_label, sub_label, shape='box', fillcolor='lightblue', node_width='1.8'):
    if sub_label:
        label_content = f'''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="8">
            <TR><TD COLSPAN="2"><IMG SRC="{icon_path}"/></TD></TR>
            <TR><TD COLSPAN="2">{main_label}</TD></TR>
            <TR><TD COLSPAN="2"><FONT POINT-SIZE="10">{sub_label}</FONT></TD></TR>
        </TABLE>
        >'''
    else:
        label_content = f'''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="8">
            <TR><TD><IMG SRC="{icon_path}"/></TD></TR>
            <TR><TD>{main_label}</TD></TR>
        </TABLE>
        >'''
    
    dot.node(node_id,
             label=label_content,
             shape=shape,
             style='filled,rounded',
             fillcolor=fillcolor,
             width=node_width)
    return node_id

# Method 3: Simple approach - icons as node backgrounds with overlay text
def create_node_with_background_icon(node_id, icon_path, main_label, sub_label, shape='box', fillcolor='lightblue', node_width='1.8'):
    # Create main node with icon as background
    dot.node(f'{node_id}_bg',
             image=icon_path,
             shape='none',
             width='0.8',
             height='0.6',
             fixedsize='true',
             label='')
    
    # Create text overlay
    if sub_label:
        label_text = f'{main_label}\\n{sub_label}'
    else:
        label_text = main_label
        
    dot.node(f'{node_id}_container',
             label=label_text,
             shape=shape,
             style='filled,rounded',
             fillcolor=fillcolor,
             width=node_width,
             margin='0.2')
    
    return f'{node_id}_container'

# Let's try Method 2 (HTML approach) - should work best
print("Creating network diagram with icons inside bubbles...")

# Internet/Cloud
internet = create_node_with_icon_html('Internet', 'icons/cloud.png', 'Internet', '', 
                                     shape='ellipse', fillcolor='lightblue', node_width='1.5')

# Border Router  
border_router = create_node_with_icon_html('BorderRouter', 'icons/router.png', 'Border Router', '172.16.0.1',
                                          fillcolor='dodgerblue')

# Firewall
firewall = create_node_with_icon_html('Firewall', 'icons/firewall.jpg', 'Firewall', '172.16.0.2 - 172.16.0.3',
                                     fillcolor='lightgray', node_width='2.2')

# Switch
switch = create_node_with_icon_html('Switch', 'icons/switch.png', 'Switch', '172.16.5.5',
                                   fillcolor='dodgerblue')

# Domain Controller
domain_controller = create_node_with_icon_html('DomainController', 'icons/server.png', 'Domain Controller', '172.16.9.10',
                                              fillcolor='dodgerblue', node_width='2.0')

# Office
office = create_node_with_icon_html('Office', 'icons/cloud.png', 'Office', '172.16.0.0/12',
                                   fillcolor='lightblue', node_width='2.0')

# Workstations
workstations = []
for i in range(1, 4):
    ws = create_node_with_icon_html(f'Workstation{i}', 'icons/workstation.jpg', 
                                   f'User Workstation {i}', f'172.16.31.{100+i}',
                                   fillcolor='lightblue', node_width='2.0')
    workstations.append(ws)

# You Are Connected Here (no icon)
dot.node('UserLocation', 
         label='You Are\\nConnected Here', 
         shape='ellipse', 
         style='filled', 
         fillcolor='plum',
         width='1.5')

# Create connections
dot.edge(internet, border_router, xlabel='128.237.3.102')
dot.edge(border_router, firewall, xlabel='172.16.0.1')
dot.edge(firewall, switch, xlabel='172.16.0.3')
dot.edge(switch, domain_controller)
dot.edge(domain_controller, office)
for ws in workstations:
    dot.edge(switch, ws)
dot.edge(switch, 'UserLocation', xlabel='172.16.5.5')

# Render the graph
dot.render('network_diagram_icons_inside', cleanup=True)
print("Network diagram with icons inside bubbles created!")