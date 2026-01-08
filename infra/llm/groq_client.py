
import os
from groq import Groq
from dotenv import load_dotenv


class GroqClient:
    def __init__(self, api_key: str | None = None):
        load_dotenv()
        self.client = Groq(
            api_key=api_key or os.getenv("API_KEY"),
            max_retries=0
        )

    def complete(self, messages) -> str:
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        return response.choices[0].message.content 
