import os
from .base import BaseLLMProvider
from groq import Groq
from dotenv import load_dotenv

class GroqProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None):
        load_dotenv()
        self.api_key = api_key or os.getenv("API_KEY")
        self.client = None
        if self.api_key:
            self.client = Groq(
                api_key=self.api_key,
                max_retries=0
            )

    def complete(self, messages: list[dict], model: str | None = None) -> str:
        if not self.client:
            raise ValueError("Groq API Key not configured")
            
        target_model = model or "llama-3.3-70b-versatile"
        # Map generic 'llama-3.3-70b-versatile' implies a capable model.
        # But let's just stick to what is passed or default.
        
        response = self.client.chat.completions.create(
            model=target_model,
            messages=messages
        )
        return response.choices[0].message.content
