from pyvis.network import Network
import networkx as nx
import os

# ======================
# CONFIGURATION
# ======================

PLACEHOLDER = "icons/placeholder.png"

# Character connections (normalized)
raw_connections = {
    "Colorzip": ["Mycil","Siouxwu","Anglais","Sandy","Johnny","Mazy","Mika","Harley","Jacks","Maybell"],
    "Mycil": ["Colorzip","Siouxwu","Smear","Anglais","Duskstep","Hex","Honeydew"],
    "Siouxwu": ["Mycil","Colorzip"],
    "Duskstep": ["Mycil","Mintie","Smear"],
    "Smear": ["Mycil","Duskstep","Mintie"],
    "Mintie": ["Smear","Duskstep"],
    "Hex": ["Mycil","Honeydew"],
    "Honeydew": ["Mycil","Hex"],
    "Lightning": [],
    "Ecosia": ["Evosia"],
    "Evosia": ["Ecosia"],
    "Anglais": ["Colorzip","Mycil"],
    "Celise": ["Damore"],
    "Damore": ["Celise"],
    "Calie": ["Esme","Miyoni"],
    "Esme": ["Calie","Miyoni"],
    "Qiztote": [],
    "Whispersong": ["Mika","Johnny","Hazelmist","Embertail"],
    "Hazelmist": ["Embertail","Whispersong"],
    "Embertail": ["Hazelmist","Whispersong"],
    "Johnny": ["Mazy","Colorzip","Mika","Harley","Whispersong","Maybell"],
    "Mazy": ["Johnny","Colorzip","Mika","Harley","Jacks"],
    "Jacks": ["Mazy","Harley","Mika","Mittens","Colorzip"],
    "Mika": ["Colorzip","Harley","Mazy","Johnny","Jacks","Whispersong","Mittens","Maybell"],
    "Harley": ["Colorzip","Mika","Mazy","Johnny","Jacks","Mittens"],
    "Sandy": ["Colorzip"],
    "Mittens": ["Jacks","Mika","Harley"],
    "Miyoni": ["Calie","Esme"],
    "Maybell": ["Colorzip","Johnny","Mika"]
}

# Normalize names and build bidirectional connections
def normalize(name):
    return name.strip().title()

connections = {}
for char, links in raw_connections.items():
    char = normalize(char)
    connections.setdefault(char, [])
    for link in links:
        link = normalize(link)
        connections[char].append(link)
        connections.setdefault(link, [])
        if char not in connections[link]:
            connections[link].append(char)

# ======================
# BUILD GRAPH
# ======================

G = nx.Graph()


for char in connections.keys():
    icon_path = f"icons/{char.lower()}.png"
    if not os.path.exists(icon_path):
        icon_path = PLACEHOLDER
    G.add_node(
        char,
        label=char,
        shape="image",
        image=icon_path,
        size=45  # <-- starting size of the icons (make larger)
    )

for char, links in connections.items():
    for link in links:
        G.add_edge(char, link, color="#c057e6")  # red line
    
        

# ======================
# CREATE NETWORK
# ======================

net = Network(
    height="900px",
    width="100%",
    bgcolor="#222222",
    font_color="white"
)

net.from_nx(G)
for e in net.edges:
        e['color'] = "#dc92f7"  # bright green
        e['width'] = 3  # thicker lines
# Increase node size multiplier for initial display
for node in net.nodes:
    node['size'] = 45  # big icons

# Physics layout options
net.set_options("""
{
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -2000,
      "centralGravity": 0.3,
      "springLength": 180,
      "springConstant": 0.05,
      "damping": 0.3
    },
    "minVelocity": 0.75,
    "stabilization": {"iterations": 300}
  },
  "nodes": {
    "physics": true
  }
}
""")

# ======================
# CLICK-TO-FOCUS + RESET BUTTON
# ======================

# We use a template string to inject the button and the click handler
# The button is added to the document body via JS to ensure it appears over the map.
focus_script = """
<script>
window.addEventListener('load', function() {
    // 1. Add "Show Full Map" button to the UI
    let btnDiv = document.createElement("div");
    btnDiv.style = "position:absolute; top:20px; left:20px; z-index:1000;";
    btnDiv.innerHTML = `
        <button id="resetBtn" style="padding:12px 24px; font-size:16px; font-weight:bold; 
        background-color:#007ACC; color:white; border:none; border-radius:8px; 
        cursor:pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            Show Full Map
        </button>`;
    document.body.appendChild(btnDiv);

    // 2. Define the reset functionality
    document.getElementById("resetBtn").onclick = function() {
        let allNodes = network.body.data.nodes.get();
        let allEdges = network.body.data.edges.get();
        
        network.body.data.nodes.update(allNodes.map(n => ({id: n.id, hidden: false})));
        network.body.data.edges.update(allEdges.map(e => ({id: e.id, hidden: false})));
    };

    // 3. Define the click-to-hide functionality
    network.on("click", function(params) {
        if (params.nodes.length > 0) {
            let selectedNode = params.nodes[0];
            let neighbors = network.getConnectedNodes(selectedNode);
            let neighborhood = [selectedNode, ...neighbors];

            // Update nodes: hide if not in neighborhood
            let nodeUpdates = network.body.data.nodes.get().map(n => ({
                id: n.id,
                hidden: !neighborhood.includes(n.id)
            }));
            network.body.data.nodes.update(nodeUpdates);

            // Update edges: hide if not connected to selected node
            let edgeUpdates = network.body.data.edges.get().map(e => ({
                id: e.id,
                hidden: !(e.from === selectedNode || e.to === selectedNode)
            }));
            network.body.data.edges.update(edgeUpdates);
        }
    });
});
</script>
"""
net.html += focus_script

# ======================
# SAVE HTML
# ======================

net.save_graph("character_map.html")
print("Map created: character_map.html")