from research_agent.core.tts.base import BaseTTSProvider
from research_agent.config.settings import settings
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

class ElevenLabsProvider(BaseTTSProvider):
    def __init__(self):
        self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        # Default to a popular male voice (e.g., "Adam" or a specific ID if known)
        # Users can change this ID to a "Jarvis" clone they find/create.
        self.voice_id = "Wq15xSaY3gWvazBRaGEU" # Adam (stable, deep male voice)

    def speak(self, text: str) -> bytes:
        # Updated for ElevenLabs SDK 2.x
        audio_generator = self.client.text_to_speech.convert(
            text=text,
            voice_id=self.voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        # Consume the generator to get bytes
        audio_bytes = b"".join(audio_generator)
        return audio_bytes
