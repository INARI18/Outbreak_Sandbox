from enum import Enum

class AttackStrategy(str, Enum):
    BRUTE_FORCE = "brute_force"
    PHISHING = "phishing"
    EXPLOIT = "exploit"
    
class NodeStatus(str, Enum):
    HEALTHY = "healthy"
    INFECTED = "infected"
    QUARANTINED = "quarantined"
