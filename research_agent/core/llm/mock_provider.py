from typing import Generator, Optional
import time
from research_agent.core.llm.base import BaseLLMProvider

class MockLLMProvider(BaseLLMProvider):
    def generate(self, prompt: str, history: list[dict] = [], system_prompt: Optional[str] = None) -> str:
        return f"Mock response to: {prompt}"

    def stream(self, prompt: str, history: list[dict] = [], system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        response = f"Mock response to: {prompt}"
        for word in response.split():
            yield word + " "
            time.sleep(0.1)
