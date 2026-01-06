"""
GroqClient
A lightweight wrapper around the Groq SDK providing a simple interface for chat completions.

This class:
- Loads environment variables from a .env file (via python-dotenv) when instantiated.
- Creates a Groq client using either a provided api_key or the API_KEY environment variable.
- Provides a convenience method to request a chat completion and return the text content of the first choice.

Usage
-----
- api_key (optional): pass an explicit API key to the constructor to avoid reading from the environment.
- If api_key is not provided, the constructor will attempt to read the API key from the environment variable "API_KEY" after calling load_dotenv().

Methods
-------
complete(messages) -> str
    Send a chat completion request to Groq and return the content string from the first returned choice.
    - messages: The messages payload expected by the Groq Chat Completions API (typically a sequence of dicts
      with "role" and "content" keys, e.g. [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]).
    - Returns: The textual content of the first choice returned by the Groq SDK.
"""
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
