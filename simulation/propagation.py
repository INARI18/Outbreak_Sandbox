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
        
        Strategies:
        - "brute_force": Boosts Attack, disregards Stealth. High Noise (Detection Risk).
        - "phishing": Boosts Stealth. Good vs Humans, bad vs Automated Systems. Low Noise.
        - "exploit": Balanced approach using standard stats.
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
            infection_chance = effective_attack - defense
            detection_chance = 0.6
            
        elif strategy == AttackStrategy.PHISHING:
            human_nodes = ["home_pc", "corp_workstation"]
            
            if target_node.type in human_nodes:
                effective_attack = stl * 1.4  # Bonus vs Humans
            else:
                effective_attack = stl * 0.5  # Penalty vs IoT/Server
                
            infection_chance = effective_attack - defense
            detection_chance = 0.1  # Very low noise
        
        else: # exploit strategy (default)
            infection_chance = (atk - defense) + rng.uniform(-0.1, 0.1)
            detection_chance = 0.3
            
        # 4. Final Calculation
        success = False
        is_detected = False
        
        roll = rng.random()
        
        if infection_chance > 0 and roll < infection_chance:
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