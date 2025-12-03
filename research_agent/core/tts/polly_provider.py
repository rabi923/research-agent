import boto3
from io import BytesIO
from research_agent.core.tts.base import BaseTTSProvider
from research_agent.config.settings import settings

class PollyProvider(BaseTTSProvider):
    def __init__(self):
        """
        Initialize Amazon Polly TTS provider.
        Requires AWS credentials to be set in environment or AWS config.
        """
        # Initialize boto3 client for Polly
        # Credentials can be set via:
        # 1. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
        # 2. AWS credentials file (~/.aws/credentials)
        # 3. IAM role (if running on AWS)
        
        aws_access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        aws_secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        aws_region = getattr(settings, 'AWS_REGION', 'us-east-1')
        
        if aws_access_key and aws_secret_key:
            self.polly = boto3.client(
                'polly',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )
        else:
            # Use default credentials (from ~/.aws/credentials or environment)
            self.polly = boto3.client('polly', region_name=aws_region)
        
        # Voice settings
        self.voice_id = 'Joanna'  # Female US English voice
        # Other popular voices: Matthew (Male), Salli (Female), Joey (Male)
        self.engine = 'neural'  # 'neural' for better quality, 'standard' for cheaper
    
    def speak(self, text: str) -> bytes:
        """
        Convert text to speech using Amazon Polly.
        Returns audio bytes in MP3 format.
        """
        try:
            # Limit text length (Polly has a 3000 character limit for neural voices)
            if len(text) > 3000:
                text = text[:2997] + "..."
            
            # Request speech synthesis
            response = self.polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=self.voice_id,
                Engine=self.engine
            )
            
            # Read audio stream
            if 'AudioStream' in response:
                audio_stream = response['AudioStream']
                return audio_stream.read()
            else:
                raise Exception("No audio stream in Polly response")
                
        except Exception as e:
            print(f"Polly TTS Error: {e}")
            # Fallback to gTTS if Polly fails
            from research_agent.core.tts.gtts_provider import GTTSProvider
            fallback = GTTSProvider()
            return fallback.speak(text)
