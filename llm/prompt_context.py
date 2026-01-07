def build_decision_context(step, network, virus, metrics):
    # build adjacency mapping: node_id -> comma-separated neighbor ids
    adjacency = {}
    for n in network.nodes.values():
        adjacency[n.id] = ", ".join(n.connected_nodes)

    return {
        "step": step,

        # network nested structure expected by prompt templates
        "network": {
            "infected_nodes": ", ".join(n.id for n in network.infected_nodes()),
            "healthy_nodes": ", ".join(n.id for n in network.healthy_nodes()),
            "adjacency": adjacency,
            "adjacency_text": "\n" + "\n".join(f"- Node {node}: {nbrs or '(none)'}" for node, nbrs in adjacency.items())
        },

        # virus nested structure expected by prompt templates
        "virus": {
            "name": virus.name,
            "attack": virus.characteristics.attack_power,
            "spread": virus.characteristics.spread_rate,
            "stealth": virus.characteristics.stealth,
            "mutation_rate": virus.characteristics.mutation_rate,
            "behavior": virus.characteristics.behavior,
            "exploit": getattr(virus, "exploit", ""),
            "impact": getattr(virus, "impact", "")
        }
    }


def build_mutation_context(virus, metrics_summary, recent_attempts) -> dict:
    return {
        "virus": {
            "attack": virus.characteristics.attack_power,
            "spread": virus.characteristics.spread_rate,
            "stealth": virus.characteristics.stealth,
            "mutation_rate": virus.characteristics.mutation_rate,
            "behavior": virus.characteristics.behavior,
        },
        "metrics": metrics_summary,
        "recent_attempts": recent_attempts
    }
