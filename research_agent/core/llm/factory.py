from research_agent.core.llm.base import BaseLLMProvider
from research_agent.core.llm.openai_provider import OpenAIProvider
from research_agent.core.llm.mock_provider import MockLLMProvider
from research_agent.config.settings import settings

def get_llm_provider() -> BaseLLMProvider:
    provider_name = settings.DEFAULT_LLM_PROVIDER.lower()
    
    if provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "mock":
        return MockLLMProvider()
    elif provider_name == "google":
        from research_agent.core.llm.google_provider import GoogleGeminiProvider
        return GoogleGeminiProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")
