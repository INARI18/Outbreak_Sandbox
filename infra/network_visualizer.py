"""
NetworkVisualizer

Adapter that translates a models.network.Network instance into a networkx.Graph
and provides basic visualization utilities.

This module-level adapter encapsulates a networkx.Graph and a reference to the
source Network object. It is responsible for converting the domain model
(nodes and their connections) into a graph representation that can be used
with NetworkX algorithms and plotting tools.

Class: NetworkVisualizer
- Purpose:
    Construct and maintain a networkx.Graph that mirrors the nodes and edges
    defined in a models.network.Network instance, and offer a simple draw
    helper to produce a PNG snapshot of the graph.

- Attributes:
    graph (networkx.Graph): The constructed NetworkX graph instance.
    network (models.network.Network): The source network model used to
        populate the graph. Expected to provide a .nodes mapping where each
        node has attributes: id, status, security_level, type, and
        connected_nodes (an iterable of neighbor ids).
"""

import networkx as nx
from models.network import Network

class NetworkVisualizer:
    def __init__(self, network: Network):
        self.graph = nx.Graph()
        self.network = network

    def build(self):
        for node in self.network.nodes.values():
            self.graph.add_node(
                node.id,
                status=node.status,
                security=node.security_level,
                type=node.type
            )

        for node in self.network.nodes.values():
            for target in node.connected_nodes:
                self.graph.add_edge(node.id, target)

    def draw(self):
        # Draw the adapter's graph using matplotlib
        import matplotlib.pyplot as plt

        colors = []
        for _, data in self.graph.nodes(data=True):
            if data.get("status") == "infected":
                colors.append("red")
            else:
                colors.append("green")

        nx.draw(self.graph, node_color=colors, with_labels=True)
        # Save to file in headless environments and close the figure
        plt.savefig("network_debug.png")
        plt.close()
