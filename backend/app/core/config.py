from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Basic app settings
    project_name: str = Field(default="BossolutionAI API", description="Application name")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Current deployment environment"
    )

    # Server/runtime settings (from .env)
    debug: bool = Field(default=False, description="Enable debug mode")
    host: str = Field(default="127.0.0.1", description="Host to bind the server to")
    port: int = Field(default=8000, description="Port to bind the server to")

    # Firebase settings
    FIREBASE_PROJECT_ID: Optional[str] = Field(default=None, description="Firebase Project ID")
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = Field(default=None, description="Firebase Private Key ID")
    FIREBASE_PRIVATE_KEY: Optional[str] = Field(default=None, description="Firebase Private Key")
    FIREBASE_CLIENT_EMAIL: Optional[str] = Field(default=None, description="Firebase Client Email")
    FIREBASE_CLIENT_ID: Optional[str] = Field(default=None, description="Firebase Client ID")

    # AI API Keys
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key for content generation")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic Claude API Key")
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY", description="Google Gemini API Key")

    # External integrations
    facebook_api_token: Optional[str] = Field(default=None, description="Facebook/Meta API Token for publishing")
    instagram_api_token: Optional[str] = Field(default=None, description="Instagram API Token")
    linkedin_api_token: Optional[str] = Field(default=None, description="LinkedIn API Token")
    twitter_api_key: Optional[str] = Field(default=None, description="Twitter/X API Key")

    # Uploads
    upload_dir: str = Field(default="temp_uploads", description="Directory for uploaded files")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True  # Allow both field name and alias


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
