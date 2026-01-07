from simulation.deterministic_policy import DeterministicPolicy
from models.virus import VirusCharacteristics

class MutationTrigger:

    @staticmethod
    def should_mutate(virus) -> bool:
        roll = DeterministicPolicy.get().randint(1, 20)
        # Fix: mutation_rate (1-10) is used as the threshold directly for a d20 roll.
        # Rate 1 => 1/20 (5%), Rate 10 => 10/20 (50%).
        threshold = virus.characteristics.mutation_rate
        return roll <= threshold


class MutationContextBuilder:

    @staticmethod
    def build(virus, metrics_summary, recent_attempts):
        return {
            "virus": {
                "name": virus.name,
                "attack_power": virus.characteristics.attack_power,
                "spread_rate": virus.characteristics.spread_rate,
                "stealth": virus.characteristics.stealth,
                "mutation_rate": virus.characteristics.mutation_rate
            },
            "metrics": metrics_summary,
            "recent_failures": [
                a for a in recent_attempts if not a["success"]
            ]
        }

class MutationStrategy:
    def mutate(self, virus, context) -> VirusCharacteristics:
        raise NotImplementedError

class SimpleMutationStrategy(MutationStrategy):

    def mutate(self, virus, context):
        new_chars = virus.characteristics.clone()

        # Exemplo: falha por segurança alta → stealth++
        new_chars.stealth = min(1.0, new_chars.stealth + 0.05)

        return new_chars


