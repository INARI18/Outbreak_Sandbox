from dataclasses import dataclass

@dataclass
class InfectionDecision:
    source_node_id: str
    target_node_id: str
    reasoning: str | None = None
