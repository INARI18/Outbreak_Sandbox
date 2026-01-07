from models.virus import Virus
from models.node import Node
from simulation.deterministic_policy import DeterministicPolicy

class PropagationSystem:
    """
    Encapsulates the logic and mathematical rules for virus propagation.
    Determines if an infection attempt is successful based on virus stats 
    vs node security.
    """

    @staticmethod
    def attempt_infection(virus: Virus, target_node: Node, strategy: str = "exploit") -> dict:
        """
        Calculates infection outcome based on Virus Stats vs Node Defense 
        AND the chosen Attack Strategy.
        
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
            # Failed attempt on wrong hardware is highly suspicious
            return {
                "success": False, 
                "reason": "incompatible_host", 
                "detected": True,
                "infection_score": 0.0 # Added score for metrics
            }

        # 2. Normalize Stats (0.0 - 1.0)
        atk = min(max(virus.characteristics.attack_power / 10.0, 0.0), 1.0)
        stl = min(max(virus.characteristics.stealth / 10.0, 0.0), 1.0)
        defense = target_node.security_level

        # 3. Apply Strategy Modifiers
        infection_chance = 0.0
        detection_chance = 0.0
        
        if strategy == "brute_force":
            # Aggressive: +50% effective Attack, but Stealth is ignored.
            # High profile: 60% base chance of detection.
            effective_attack = atk * 1.5
            infection_chance = effective_attack - defense
            detection_chance = 0.6
            
        elif strategy == "phishing":
            # Social Engineering: Uses Stealth mostly.
            # Bonus against human-operated nodes, penalty against servers.
            human_nodes = ["home_pc", "corp_workstation"]
            
            if target_node.type in human_nodes:
                effective_attack = stl * 1.4  # Bonus vs Humans
            else:
                effective_attack = stl * 0.5  # Penalty vs IoT/Server (no human to click link)
                
            infection_chance = effective_attack - defense
            detection_chance = 0.1  # Very low noise
        
        else: # strategy == "exploit" (or default)
            infection_chance = (atk - defense) + rng.uniform(-0.1, 0.1)
            detection_chance = 0.3
            
        # 4. Final Calculation
        success = False
        is_detected = False
        
        # Roll for Infection
        # Chance must be > 0. A random roll helps verify probability
        roll = rng.random()
        
        # If chance is 0.4, we need roll < 0.4 to succeed
        if infection_chance > 0 and roll < infection_chance:
            target_node.infect()
            status = "infected"
            success = True
        else:
            # Failed attempt. Check if detected.
            # Detection happens if roll < detection_chance? Or maybe independent roll?
            # Let's say detection is an independent roll.
            det_roll = rng.random()
            if det_roll < detection_chance:
                 is_detected = True
                 
        return {
            "success": success,
            "detected": is_detected,
            "reason": "strategy_failed" if not success else "strategy_success",
            "infection_score": round(infection_chance, 2)
        }

        if success:
            target_node.infect()

        return {
            "success": success,
            "detected": detected,
            "strategy": strategy,
            "infection_chance": round(infection_chance, 2),
            "node_id": target_node.id,
            "node_type": target_node.type,
            "security_before": defense
        }
