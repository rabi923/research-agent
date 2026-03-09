import asyncio
import nest_asyncio
import edge_tts
from research_agent.core.tts.base import BaseTTSProvider

# Apply nest_asyncio to allow nested event loops (useful for Streamlit/Jupyter)
nest_asyncio.apply()

class EdgeTTSProvider(BaseTTSProvider):
    def __init__(self):
        # User requested "en-GB-SoniaNeural"
        # We will use SSML to make it sound more "JARVIS-like" (Crisp, slightly faster, authoritative)
        self.voice = "en-GB-SoniaNeural"

    def speak(self, text: str) -> bytes:
        """
        Convert text to speech using Microsoft Edge TTS with SSML.
        Returns audio bytes (mp3).
        """
        # SSML (Speech Synthesis Markup Language) allows us to control pitch, rate, and style.
        # To sound like JARVIS (efficient, crisp):
        # - rate='+10%': Slightly faster to sound intelligent/efficient.
        # - pitch='-2Hz': Slightly deeper for authority (though Sonia is female, this adds gravitas).
        # - style='cheerful' or 'assistant': Some voices support styles. Sonia is quite neutral/professional by default.
        
        async def _generate():
            # Use direct arguments for rate and pitch instead of raw SSML
            # This avoids issues with the TTS reading XML tags aloud
            communicate = edge_tts.Communicate(
                text, 
                self.voice, 
                rate='+10%', 
                pitch='-2Hz'
            )
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data

        try:
            # Run the async function synchronously
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return loop.run_until_complete(_generate())
            else:
                return asyncio.run(_generate())
        except Exception as e:
            print(f"Error in EdgeTTS: {e}")
            return b""
