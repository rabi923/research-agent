import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Keys
    OPENAI_API_KEY: str = Field(default="")
    ANTHROPIC_API_KEY: str = Field(default="")
    GOOGLE_API_KEY: str = Field(default="AIzaSyD2sYdRVHLHT4UTi4MZyZ5hjlF5LBS3aPU")

    # Search Keys
    TAVILY_API_KEY: str = Field(default="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")
    SERPER_API_KEY: str = Field(default="")

    # TTS Keys
    ELEVENLABS_API_KEY: str = Field(default="sk_f16a30a800512abab7eed220b7e9d60fe7a33eee74c32ec2")

    # Defaults
    DEFAULT_LLM_PROVIDER: str = "openai"  # openai, anthropic, google, mock
    DEFAULT_SEARCH_PROVIDER: str = "tavily" # tavily, duckduckgo
    DEFAULT_TTS_PROVIDER: str = "elevenlabs"    # gtts, openai, elevenlabs

    # LLM Config
    LLM_TEMPERATURE: float = 0.7
    LLM_MODEL: str = "gpt-4o" # or gpt-3.5-turbo, etc.

    # Report Config
    REPORT_OUTPUT_DIR: str = "reports"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
