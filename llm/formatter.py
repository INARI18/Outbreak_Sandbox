from llm.prompt_loader import load_prompt

class PromptFormatter:
    @staticmethod
    def decision(context: dict) -> list[dict]:
        system = load_prompt("system.txt")
        user = load_prompt("decision.txt", **context)

        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

    @staticmethod
    def mutation(context: dict) -> list[dict]:
        system = load_prompt("system.txt")
        user = load_prompt("mutation.txt", **context)

        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
