from typing import Generator, Optional
import google.generativeai as genai
from research_agent.core.llm.base import BaseLLMProvider
from research_agent.config.settings import settings

class GoogleGeminiProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            print("Error: GOOGLE_API_KEY is missing in settings!")
        else:
            print(f"Google API Key loaded: {settings.GOOGLE_API_KEY[:5]}...{settings.GOOGLE_API_KEY[-4:]}")
            
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model_name = 'gemini-2.5-flash'
        print(f"DEBUG: Initializing Google Model: {model_name}")
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str, history: list[dict] = [], system_prompt: Optional[str] = None) -> str:
        # Construct chat history for Gemini
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
            
        # Retry logic
        max_retries = 3
        base_delay = 5
        
        import time
        import random
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    if attempt < max_retries - 1:
                        delay = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                        print(f"DEBUG: Rate limit hit. Retrying in {delay:.2f}s...")
                        time.sleep(delay)
                        continue
                raise e
        return ""

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
