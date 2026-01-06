"""Topology factory utilities using networkx.

Provides a mapping from topology names to functions that create a networkx.Graph
with a requested number of nodes.

Functions accept a node_count (int) and optional kwargs for topology-specific
options. All graphs' nodes are labeled with integers from 0..n-1.
"""

from math import ceil, floor, sqrt
from typing import Callable, Dict
import networkx as nx


def _relabel_to_ints(G: nx.Graph) -> nx.Graph:
    """Relabel nodes to 0..n-1 preserving order."""
    mapping = {old: i for i, old in enumerate(G.nodes())}
    return nx.relabel_nodes(G, mapping)


def topology_random(node_count: int, probability: float | None = None, seed: int | None = None) -> nx.Graph:
    if node_count <= 1:
        return nx.empty_graph(max(0, node_count)) # return a graph without edges, only nodes (handles negative numbers)
    if probability is None:
        probability = min(1.0, 2.0 / max(1, node_count)) # default probability
    G = nx.gnp_random_graph(node_count, probability, seed=seed)
    return _relabel_to_ints(G)


def topology_ring(node_count: int, **_) -> nx.Graph:
    if node_count <= 0:
        return nx.empty_graph(0)
    G = nx.cycle_graph(node_count)
    return _relabel_to_ints(G)


def topology_star(node_count: int, **_) -> nx.Graph:
    if node_count <= 0:
        return nx.empty_graph(0)
    if node_count == 1:
        return nx.empty_graph(1)
    G = nx.star_graph(node_count - 1) # the star graph with n leaves has n+1 nodes because center is 0
    return _relabel_to_ints(G)


def topology_mesh(node_count: int, **_) -> nx.Graph:
    if node_count <= 0:
        return nx.empty_graph(max(0, node_count))
    G = nx.complete_graph(node_count)
    return _relabel_to_ints(G)


def topology_grid(node_count: int, **_) -> nx.Graph:
    if node_count <= 0:
        return nx.empty_graph(max(0, node_count))

    # choose rows and cols to make near-square grid
    rows = int(floor(sqrt(node_count)))
    if rows <= 0:
        rows = 1
    cols = int(ceil(node_count / rows))

    G = nx.grid_2d_graph(rows, cols)

    # Relabel nodes to integers in row-major order and trim extras
    newG = nx.Graph()
    nodes = list(G.nodes())
    for i, coord in enumerate(nodes):
        if i >= node_count:
            break
        newG.add_node(i)

    # add edges only between kept nodes
    coord_to_idx = {coord: i for i, coord in enumerate(nodes) if i < node_count}
    for a, b in G.edges():
        if a in coord_to_idx and b in coord_to_idx:
            newG.add_edge(coord_to_idx[a], coord_to_idx[b])

    return newG


def topology_hub(node_count: int, hubs: int = 1, **_) -> nx.Graph:
    if node_count <= 0:
        return nx.empty_graph(max(0, node_count))
    if node_count == 1:
        return nx.empty_graph(1)

    hubs = max(1, min(hubs, node_count))
    G = nx.Graph()
    for i in range(hubs):
        G.add_node(i)

    # interconnect hubs
    for i in range(hubs):
        for j in range(i + 1, hubs):
            G.add_edge(i, j)

    # remaining nodes are spokes
    spoke_start = hubs
    for s in range(spoke_start, node_count):
        # assign to a hub in round-robin
        hub = (s - spoke_start) % hubs
        G.add_node(s)
        G.add_edge(hub, s)

    return G


TOPOLOGY_MAP: Dict[str, Callable[..., nx.Graph]] = {
    "random": topology_random,
    "ring": topology_ring,
    "star": topology_star,
    "mesh": topology_mesh,
    "grid": topology_grid,
    "hub": topology_hub,
}


def create_topology(name: str, node_count: int, **kwargs) -> nx.Graph:
    name = name.lower()
    if name not in TOPOLOGY_MAP:
        raise KeyError(f"Unknown topology: {name}. Available: {list(TOPOLOGY_MAP.keys())}")
    return TOPOLOGY_MAP[name](node_count, **kwargs)
