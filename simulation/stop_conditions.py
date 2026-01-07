from typing import Tuple


def check_stop(engine) -> Tuple[bool, str]:
    """Evaluate common stop conditions for the simulation.

    Returns (should_stop, reason) where reason is a short identifier.
    Conditions checked (in order):
    - max_steps reached
    - no infected nodes (extinction)
    - all nodes infected (saturation)
    - no possible spread (no infected node has a healthy neighbor)
    """
    # Max steps
    if engine.current_step >= engine.max_steps:
        return True, "max_steps_reached"

    # No infected nodes -> nothing to do
    infected = engine.network.infected_nodes()
    if len(infected) == 0:
        return True, "no_infected_nodes"

    # All nodes infected -> finished
    healthy = engine.network.healthy_nodes()
    if len(healthy) == 0:
        return True, "all_infected"

    # Check if any infected node has a healthy neighbor that could be targeted
    for node in infected:
        for neighbor_id in node.connected_nodes:
            neighbor = engine.network.get_node(neighbor_id)
            if neighbor and not neighbor.is_infected:
                # Found at least one possible target
                return False, ""

    # No infected node can reach a healthy node
    return True, "no_possible_spread"
