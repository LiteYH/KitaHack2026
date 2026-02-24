from functools import lru_cache
from pathlib import Path
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
    tavily_api_key: Optional[str] = Field(default=None, alias="TAVILY_API_KEY", description="Tavily Search API Key")

    # External integrations
    facebook_api_token: Optional[str] = Field(default=None, description="Facebook/Meta API Token for publishing")
    instagram_api_token: Optional[str] = Field(default=None, description="Instagram API Token")
    linkedin_api_token: Optional[str] = Field(default=None, description="LinkedIn API Token")
    twitter_api_key: Optional[str] = Field(default=None, description="Twitter/X API Key")

    # Email / Notification Settings - Gmail SMTP (recommended, no domain required)
    # See EMAIL_SETUP_GUIDE.md for configuration instructions
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP server host (e.g., smtp.gmail.com)")
    SMTP_PORT: Optional[int] = Field(default=587, description="SMTP server port (587 for TLS, 465 for SSL)")
    SMTP_USER: Optional[str] = Field(default=None, description="SMTP username (your email)")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password (Gmail app password)")
    SMTP_FROM_EMAIL: Optional[str] = Field(default=None, description="From email address")
    SMTP_FROM_NAME: Optional[str] = Field(default="BossolutionAI", description="From name displayed in emails")
    SMTP_USE_TLS: Optional[bool] = Field(default=True, description="Use TLS encryption (recommended for port 587)")
    SMTP_USE_SSL: Optional[bool] = Field(default=False, description="Use SSL encryption (for port 465)")

    # Uploads
    upload_dir: str = Field(default="temp_uploads", description="Directory for uploaded files")

    image_output_dir: str = Field(
        default="generated_images", 
        description="Directory for AI-generated images"
    )
    imagen_model: str = Field(
        default="imagen-4.0-generate-001",
        description="Google Imagen model variant (fast-generate for cost efficiency)"
    )

    class Config:
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        env_file_encoding = "utf-8"
        populate_by_name = True  # Allow both field name and alias


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
