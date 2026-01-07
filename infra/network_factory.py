from typing import Optional
import networkx as nx
import random
import os

from models.network import Network
from models.node import Node
from infra.repositories.node_type_repository import NodeTypeRepository


def graph_to_network(
    G: nx.Graph,
    network_id: str = "generated-net",
    topology: str = "unknown",
    security_level: Optional[float] = None,
) -> Network:
    """Convert a networkx.Graph into a `Network` containing `Node`s.

    Nodes in the returned Network will have string IDs equal to their integer
    node labels from G (converted to str). Edges are treated as undirected
    connections and will be added bidirectionally to each Node.connected_nodes.
    """
    node_count = G.number_of_nodes()
    
    # Load Node Types
    repo = NodeTypeRepository("node_types.json")
    try:
        available_types = repo.load_all()
    except Exception:
        # Fallback if json not found or error
        available_types = []

    # Determine types per node
    node_configs = []
    final_network_security = 0.0

    if not available_types:
        # Fallback logic: use default values for all nodes
        fallback_sec = security_level if security_level is not None else 0.3
        final_network_security = fallback_sec
        for idx in range(node_count):
            node_configs.append({
                "type": "pc",
                "sec": fallback_sec,
                "name": f"Node-{idx}"
            })
    else:
        if security_level is None:
            # Random selection (uniform probability)
            chosen_types = random.choices(available_types, k=node_count)
        else:
            weights = [1.0 / (abs(nt.security_level - security_level) + 0.1) for nt in available_types]
            chosen_types = random.choices(available_types, weights=weights, k=node_count)
        
        # Calculate resulting network security level
        if node_count > 0:
            final_network_security = sum(t.security_level for t in chosen_types) / node_count
            final_network_security = round(final_network_security, 2)
        
        for idx, t in enumerate(chosen_types):
            node_configs.append({
                "type": t.id,
                "sec": t.security_level,
                "name": f"{t.name}-{idx}"
            })

    network = Network(id=network_id, topology=topology, size=node_count, security_level=final_network_security)

    # Ensure deterministic ordering of nodes (use sorted by current labels)
    nodes = list(G.nodes())
    
    pos = nx.spring_layout(G, scale=1.0, seed=42)

    # Create Node objects
    for idx, n in enumerate(nodes):
        config = node_configs[idx]
        node = Node(
            id=str(idx),
            name=config["name"],
            node_type=config["type"],
            security_level=config["sec"],
        )
        
        # Assign position
        if n in pos:
            node.x = float(pos[n][0])
            node.y = float(pos[n][1])

        network.add_node(node)
        
    original_to_str = {orig: str(i) for i, orig in enumerate(nodes)}

    # Add connections
    for u, v in G.edges():
        su = original_to_str[u]
        sv = original_to_str[v]
        network.get_node(su).connect(sv)
        network.get_node(sv).connect(su)

    return network
