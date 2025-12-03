import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Keys
    OPENAI_API_KEY: str = Field(default="")
    ANTHROPIC_API_KEY: str = Field(default="")
    GOOGLE_API_KEY: str = Field(default="")

    # Search Keys
    TAVILY_API_KEY: str = Field(default="")
    SERPER_API_KEY: str = Field(default="")

    # TTS Keys
    ELEVENLABS_API_KEY: str = Field(default="")
    
    # AWS Keys (for Polly)
    AWS_ACCESS_KEY_ID: str = Field(default="")
    AWS_SECRET_ACCESS_KEY: str = Field(default="")
    AWS_REGION: str = Field(default="us-east-1")

    # Defaults
    DEFAULT_LLM_PROVIDER: str = "google"  # openai, anthropic, google, mock
    DEFAULT_SEARCH_PROVIDER: str = "serper" # serper, tavily, duckduckgo
    DEFAULT_TTS_PROVIDER: str = "gtts"    # gtts, polly, openai, elevenlabs

    # LLM Config
    LLM_TEMPERATURE: float = 0.7
    LLM_MODEL: str = "gpt-4o" # or gpt-3.5-turbo, etc.

    # Report Config
    REPORT_OUTPUT_DIR: str = "reports"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
