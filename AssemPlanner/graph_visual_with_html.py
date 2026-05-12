import os
import random
import networkx as nx
from pyvis.network import Network

def generate_graph_html():
    # Load graph
    G = nx.read_graphml("./dickens_valve/graph_chunk_entity_relation.graphml")

    # Create visualization network
    net = Network(height="600px", width="100%", notebook=False)
    net.from_nx(G)

    # Add colors and titles
    for node in net.nodes:
        node["color"] = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        if "description" in node:
            node["title"] = node["description"]

    for edge in net.edges:
        if "description" in edge:
            edge["title"] = edge["description"]

    # Ensure templates directory exists
    os.makedirs("templates", exist_ok=True)

    # Write HTML file
    html_path = "templates/index.html"
    net.write_html(html_path)

    # Read and return HTML content
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()