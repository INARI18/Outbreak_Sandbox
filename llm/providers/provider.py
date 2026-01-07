from llm.interface import DecisionProvider
from llm.types import InfectionDecision
from infra.llm.groq_client import GroqClient
from llm.prompts import build_prompt
from llm.parsers import parse_decision

class LLMDecisionProvider(DecisionProvider):
    def __init__(self, model="llama-3.3-70b-versatile"):
        self.client = GroqClient()
        self.model = model

    def decide(self, step, network, virus, metrics):
        messages = build_prompt(step, network, virus, metrics)
        raw = self.client.complete(messages, self.model)
        return parse_decision(raw)
