from models.virus import Virus
from models.node import Node
from models.enums import AttackStrategy
from simulation.deterministic_policy import DeterministicPolicy

class PropagationSystem:
    @staticmethod
    def attempt_infection(virus: Virus, target_node: Node, strategy: str = AttackStrategy.EXPLOIT) -> dict:
        """
        Calculates infection outcome based on Virus Stats vs Node Defense 
        and the chosen Attack Strategy.
        """
        rng = DeterministicPolicy.get()
        
        # 1. Validation Checks
        if target_node.status != "healthy":
            return {
                "success": False, 
                "reason": "node_not_healthy", 
                "detected": False,
                "infection_score": 0.0
            }

        if not virus.can_infect(target_node.type):
            return {
                "success": False, 
                "reason": "incompatible_host", 
                "detected": True,
                "infection_score": 0.0
            }

        # 2. Normalize Stats (0.0 - 1.0)
        atk = min(max(virus.characteristics.attack_power / 10.0, 0.0), 1.0)
        stl = min(max(virus.characteristics.stealth / 10.0, 0.0), 1.0)
        defense = target_node.security_level

        # 3. Apply Strategy Modifiers
        infection_chance = 0.0
        detection_chance = 0.0
        
        if strategy == AttackStrategy.BRUTE_FORCE:
            effective_attack = atk * 1.5
            infection_chance = 0.1 + (effective_attack - defense)
            detection_chance = 0.6
            
        elif strategy == AttackStrategy.PHISHING:
            human_nodes = ["home_pc", "corp_workstation"]
            
            # HARD BLOCK: Phishing requires a human user
            if target_node.type not in human_nodes:
                return {
                    "success": False,
                    "detected": True,
                    "reason": "phishing_logic_error_no_human",
                    "infection_score": 0.0
                }
            
            # Bonus vs Humans
            effective_attack = stl * 1.4
            
            # Base 20% + diff
            infection_chance = 0.2 + (effective_attack - defense)
            detection_chance = 0.1 
        
        else: # exploit strategy (default)
            # Base 25% + (Atk - Def) + Variance
            infection_chance = 0.25 + (atk - defense) + rng.uniform(-0.05, 0.05)
            detection_chance = 0.3
            
        # 4. Final Calculation
        success = False
        is_detected = False
        
        roll = rng.random()
        
        if infection_chance > 0 and roll < infection_chance:
            target_node.infect()
            status = "infected"
            success = True
        elif roll < 0.05: # Minimal 5% success chance 
            target_node.infect()
            status = "infected"
            success = True
        else:
            det_roll = rng.random()
            if det_roll < detection_chance:
                 is_detected = True
                 
        return {
            "success": success,
            "detected": is_detected,
            "reason": "strategy_failed" if not success else "strategy_success",
            "infection_score": round(infection_chance, 2)
        }