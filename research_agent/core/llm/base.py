from abc import ABC, abstractmethod
from typing import Generator, Optional

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, history: list[dict] = [], system_prompt: Optional[str] = None) -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def stream(self, prompt: str, history: list[dict] = [], system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Stream a response from the LLM."""
        pass
