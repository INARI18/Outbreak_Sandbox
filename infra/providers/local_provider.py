from .base import BaseLLMProvider
import os
import json

# FIX: ensure that the local provider is working properly
class LocalProvider(BaseLLMProvider):
    def __init__(self, model_path="microsoft/Phi-3-mini-4k-instruct"):
        self.model_path = model_path
        self._pipeline = None
        self._load_model()

    def _load_model(self):
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
            
            print(f"Loading local model: {self.model_path}...")
            self._pipeline = pipeline(
                "text-generation",
                model=self.model_path,
                device_map="cpu",
                torch_dtype="auto", 
                trust_remote_code=True,
                model_kwargs={"attn_implementation": "eager"}
            )
            print("Local model loaded successfully (CPU Mode).")
            
        except ImportError:
            print("Transformers/Torch not installed. Local mode unavailable.")
        except Exception as e:
            print(f"Error loading model: {e}")
            self._pipeline = None

    def complete(self, messages: list[dict], model: str | None = None) -> str:
        if not self._pipeline:
            return '{"error": "Local model engine not initialized missing dependencies"}'

        prompt = self._pipeline.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        outputs = self._pipeline(
            prompt, 
            max_new_tokens=500, 
            do_sample=True, 
            temperature=0.1, # Low temperature for more deterministic/logical JSON
            return_full_text=False,
            use_cache=False
        )
        
        generated_text = outputs[0]["generated_text"]
        return generated_text

