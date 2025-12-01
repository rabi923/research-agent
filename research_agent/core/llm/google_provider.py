from typing import Generator, Optional
import google.generativeai as genai
from research_agent.core.llm.base import BaseLLMProvider
from research_agent.config.settings import settings

class GoogleGeminiProvider(BaseLLMProvider):
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate(self, prompt: str, history: list[dict] = [], system_prompt: Optional[str] = None) -> str:
        # Construct chat history for Gemini
        # Gemini expects history as a list of Content objects or a chat session.
        # For simplicity in this stateless wrapper, we'll format it into the prompt or use start_chat if we want to maintain state.
        # Here we will format it as a text block for the "flash" model which handles context well.
        
        context_str = ""
        if history:
            context_str = "Conversation History:\n"
            for msg in history:
                role = msg.get("role")
                content = msg.get("content")
                if role in ["user", "assistant"]:
                    context_str += f"{role.capitalize()}: {content}\n"
            context_str += "\n"

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System Instruction: {system_prompt}\n\n{context_str}User Query: {prompt}"
        else:
            full_prompt = f"{context_str}User Query: {prompt}"
            
        response = self.model.generate_content(full_prompt)
        return response.text

    def stream(self, prompt: str, history: list[dict] = [], system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        context_str = ""
        if history:
            context_str = "Conversation History:\n"
            for msg in history:
                role = msg.get("role")
                content = msg.get("content")
                if role in ["user", "assistant"]:
                    context_str += f"{role.capitalize()}: {content}\n"
            context_str += "\n"

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System Instruction: {system_prompt}\n\n{context_str}User Query: {prompt}"
        else:
            full_prompt = f"{context_str}User Query: {prompt}"

        response = self.model.generate_content(full_prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
