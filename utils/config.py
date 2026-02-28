from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field
from typing import Optional

class Settings(BaseSettings):
    bot_token: str = Field(..., alias="BOT_TOKEN")
    chat_id: int = Field(..., alias="CHAT_ID")
    gemini_api_key: SecretStr = Field(..., alias="GEMINI_API_KEY")
    groq_api_key: Optional[SecretStr] = Field(None, alias="GROQ_API_KEY")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

config = Settings()
