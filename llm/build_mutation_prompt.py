def build_mutation_prompt(context):
    virus = context["virus"]

    return f"""
The virus may mutate based on recent performance.

Current virus characteristics:
- attack_power: {virus['attack_power']}
- spread_rate: {virus['spread_rate']}
- stealth: {virus['stealth']}

Recent performance summary:
{context['metrics_summary']}

Recent attempts:
{context['recent_attempts']}

Decide whether the virus should mutate.
If yes, propose new characteristics.
"""
