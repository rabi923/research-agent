from io import BytesIO
from gtts import gTTS
from research_agent.core.tts.base import BaseTTSProvider

class GTTSProvider(BaseTTSProvider):
    def speak(self, text: str) -> bytes:
        tts = gTTS(text=text, lang='en')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
