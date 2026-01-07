from simulation.mutation import MutationStrategy
from models.virus import VirusCharacteristics

class LLMMutationStrategy(MutationStrategy):
    def __init__(self, llm_interface):
        self.llm = llm_interface

    def mutate(self, virus, context) -> VirusCharacteristics:
        # Pass metrics summary into context
        # If 'metrics_obj' is in context, use it. Otherwise, use empty/dummy metrics to avoid crash
        metrics_obj = context.get('metrics_obj') 
        
        # Guard clause for Mock/Tests where metrics might be None
        if metrics_obj is None:
             # Create a dummy collector if needed or just return clone
             # Returning clone is safer to avoid AttributeError downstream
             return virus.characteristics.clone()
             
        decision = self.llm.decide_mutation(
            virus=virus,
            metrics=metrics_obj
        )
        
        # If error or no mutation, return clone
        if "error" in decision or not decision.get("mutate", False):
            return virus.characteristics.clone()

        new_chars = virus.characteristics.clone()
        p_type = decision.get("type", "")
        param = decision.get("target_parameter", "")
        val = decision.get("change_value")

        if p_type == "stat_boost" and isinstance(val, (int, float)):
            if param == "attack_power":
                new_chars.attack_power = min(10.0, max(0.0, new_chars.attack_power + val))
            elif param == "stealth":
                new_chars.stealth = min(10.0, max(0.0, new_chars.stealth + val))
            elif param == "spread_rate":
                new_chars.spread_rate = min(10.0, max(0.0, new_chars.spread_rate + val))
                
        elif p_type == "adaptation" and isinstance(val, str):
            if param == "target_hosts":
                 if val not in new_chars.target_hosts:
                     new_chars.target_hosts.append(val)

        return new_chars
