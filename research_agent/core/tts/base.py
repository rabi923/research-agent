from abc import ABC, abstractmethod

class BaseTTSProvider(ABC):
    @abstractmethod
    def speak(self, text: str) -> bytes:
        """
        Convert text to speech and return the audio bytes.
        """
        pass
