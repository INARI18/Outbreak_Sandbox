from .base import BaseLLMProvider
import random

class MockProvider(BaseLLMProvider):
    def complete(self, messages: list[dict], model: str | None = None) -> str:
        # Simple mock response logic just to keep things running
        # We can inspect the last message content to be slightly more context aware if needed
        return '{"source_node_id": "0", "target_node_id": "1", "reasoning": "Mock reasoning"}'
