from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    @abstractmethod
    def complete(self, messages: list[dict], model: str | None = None) -> str:
        """
        Takes a list of messages (role/content) and returns the string response.
        """
        pass
