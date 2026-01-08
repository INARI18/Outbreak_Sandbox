from enum import Enum

class AttackStrategy(str, Enum):
    """
    Standardized names for attack strategies chosen by the LLM.
    Acts as the source of truth for string contracts.
    """
    BRUTE_FORCE = "brute_force"
    PHISHING = "phishing"
    EXPLOIT = "exploit"
    
class NodeStatus(str, Enum):
    """
    Standardized node states.
    """
    HEALTHY = "healthy"
    INFECTED = "infected"
    QUARANTINED = "quarantined"
