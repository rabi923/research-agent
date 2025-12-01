from research_agent.core.tts.base import BaseTTSProvider
from research_agent.core.tts.gtts_provider import GTTSProvider
from research_agent.config.settings import settings

def get_tts_provider() -> BaseTTSProvider:
    provider_name = settings.DEFAULT_TTS_PROVIDER.lower()
    
    if provider_name == "gtts":
        return GTTSProvider()
    elif provider_name == "elevenlabs":
        from research_agent.core.tts.elevenlabs_provider import ElevenLabsProvider
        return ElevenLabsProvider()
    else:
        # Fallback to gTTS if unknown
        return GTTSProvider()
