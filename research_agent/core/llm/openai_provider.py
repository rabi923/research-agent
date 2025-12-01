from typing import Generator, Optional
from openai import OpenAI
from research_agent.core.llm.base import BaseLLMProvider
from research_agent.config.settings import settings

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o" # Default to a capable model

    def generate(self, prompt: str, history: list[dict] = [], system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add history
        for msg in history:
            if msg.get("role") in ["user", "assistant"]:
                messages.append({"role": msg.get("role"), "content": msg.get("content")})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

    def stream(self, prompt: str, history: list[dict] = [], system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        # Add history
        for msg in history:
            if msg.get("role") in ["user", "assistant"]:
                messages.append({"role": msg.get("role"), "content": msg.get("content")})

        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
