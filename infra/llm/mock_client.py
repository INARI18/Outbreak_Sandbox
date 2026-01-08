import json
import random

class MockClient:
    def __init__(self, api_key=None):
        pass

    def complete(self, messages) -> str:
        src = str(random.randint(0, 5))
        dst = str(random.randint(0, 5))
        
        response = {
            "source_node_id": src,
            "target_node_id": dst,
            "strategy": random.choice(["exploit", "brute_force", "phishing"]),
            "reasoning": f"[MOCK] Picking {src} -> {dst} randomly to test UI flow.",
            
            # Mutation keys (MutationParser)
            # The tool uses different prompts, but the parser looks for specific keys.
            "analysis": "Mock analysis of viral performance.",
            "decision": random.choice(["stat_boost", "adaptation", "idle"]),
            "stat": random.choice(["attack_power", "stealth", "spread_rate"]),
            "increment": 0.5,
            "new_target_type": "legacy_server"
        }
        
        return json.dumps(response)
