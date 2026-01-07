import json
import random

class MockClient:
    """
    A mock LLM client for testing purposes without consuming API credits.
    Returns valid JSON responses mimicking the expected output structure.
    """
    
    def __init__(self, api_key=None):
        pass

    def complete(self, messages) -> str:
        """
        Returns a mock JSON response.
        Attempts to infer context or just returns a generic valid structure.
        """
        # We can pretend to decide something.
        # Since we don't know the exact node IDs present in the prompt easily,
        # we'll return strings that likely exist if nodes are 0-indexed integers cast to strings
        # or just randoms.
        
        src = str(random.randint(0, 5))
        dst = str(random.randint(0, 5))
        
        response = {
            # Spread keys (DecisionParser)
            "source_node_id": src,
            "target_node_id": dst,
            "strategy": random.choice(["exploit", "brute_force", "phishing"]),
            "reasoning": f"[MOCK] Picking {src} -> {dst} randomly to test UI flow.",
            
            # Mutation keys (MutationParser)
            # The tool uses different prompts, but the parser looks for specific keys.
            # Providing all might be safer if the mock is dumb.
            "analysis": "Mock analysis of viral performance.",
            "decision": random.choice(["stat_boost", "adaptation", "idle"]),
            "stat": random.choice(["attack_power", "stealth", "spread_rate"]),
            "increment": 0.5,
            "new_target_type": "legacy_server"
        }
        
        return json.dumps(response)
