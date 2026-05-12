import json
import os
import networkx as nx
from pyvis.network import Network
import webbrowser


def generate_interactive_map(json_path: str, html_output: str = "templates/graph_temp.html"):
    """Generate interactive visualization of scene graph"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()

    for node in data["nodes"]:
        G.add_node(node["id"], label=node["name"], type=node["type"])

    for edge in data["edges"]:
        G.add_edge(edge["source"], edge["target"], label=edge["relation"])

    net = Network(height="850px", width="100%", directed=True, notebook=False,
                  bgcolor="#ffffff", font_color="#222222")

    net.force_atlas_2based(gravity=-100, central_gravity=0.02,
                           spring_length=80, spring_strength=0.08,
                           damping=0.4, overlap=0.6)

    net.from_nx(G)

    type_colors = {
        "Room": "#f4a261",
        "shelves": "#2a9d8f",
        "Tool": "#e76f51",
        "Part": "#264653"
    }

    for node in net.nodes:
        node_type = G.nodes[node["id"]]["type"]
        node["color"] = type_colors.get(node_type, "#cccccc")
        node["title"] = f"<b>Type:</b> {node_type}<br><b>Name:</b> {node['label']}"
        node["size"] = 25
        node["font"] = {"size": 20}

    for edge in net.edges:
        source, target = edge["from"], edge["to"]
        edge_data = G.get_edge_data(source, target)
        if "label" in edge_data:
            edge["title"] = f"Relation: {edge_data['label']}"
        edge["width"] = 2
        edge["arrows"] = "to"

    os.makedirs(os.path.dirname(html_output), exist_ok=True)
    net.write_html(html_output)
    print(f"✅ Graph generated: {html_output}")

    abs_path = os.path.abspath(html_output)
    webbrowser.open(f"file://{abs_path}")


if __name__ == "__main__":
    generate_interactive_map("React/scene_graph.json")