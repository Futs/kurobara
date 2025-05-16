import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings configuration class.
    
    Handles all configuration settings for the Kurobara application,
    including API, database, authentication, email, and feature settings.
    """
    # API Settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 8))
    SERVER_NAME: str = os.getenv("SERVER_NAME", "kurobara")
    SERVER_HOST: AnyHttpUrl = os.getenv("SERVER_HOST", "http://localhost")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Kurobara")
    
    # CORS Settings
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Rate Limiting Settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RATE_LIMITING_ENABLED: bool = os.getenv("RATE_LIMITING_ENABLED", "False").lower() == "true"

    # Frontend URLs (added to fix validation errors)
    REACT_APP_API_URL: Optional[str] = None
    NEXT_PUBLIC_API_URL: Optional[str] = None

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from string or list format."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(f"Invalid CORS origins format: {v}")

    # Database Settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "kurobara")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_URL: Optional[PostgresDsn] = None
    DATABASE_CONNECT_ARGS: Dict[str, Any] = {}

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Build PostgreSQL connection string if not explicitly provided."""
        if isinstance(v, str):
            return v
        
        # Access data using values.data instead of values.get
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=int(values.data.get("POSTGRES_PORT")),  # Convert string to integer
            path=f"/{values.data.get('POSTGRES_DB') or ''}",
        )

    # Email Settings
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() == "true"
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT", "0")) or None
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[str] = os.getenv("EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: Optional[str] = os.getenv("EMAILS_FROM_NAME")
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = int(os.getenv("EMAIL_RESET_TOKEN_EXPIRE_HOURS", "48"))
    EMAIL_TEMPLATES_DIR: str = os.getenv("EMAIL_TEMPLATES_DIR", "/app/app/email-templates/build")
    EMAILS_ENABLED: bool = False

    @field_validator("EMAILS_ENABLED", mode="before")
    @classmethod
    def check_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        """Determine if email functionality is enabled based on configuration."""
        return bool(
            values.data.get("SMTP_HOST")
            and values.data.get("SMTP_PORT")
            and values.data.get("EMAILS_FROM_EMAIL")
        )

    # User Settings
    EMAIL_TEST_USER: str = os.getenv("EMAIL_TEST_USER", "test@example.com")
    FIRST_SUPERUSER: str = os.getenv("FIRST_SUPERUSER", "admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "admin")
    USERS_OPEN_REGISTRATION: bool = os.getenv("USERS_OPEN_REGISTRATION", "True").lower() == "true"

    # OAuth Settings
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI")

    # Security Settings
    TWO_FACTOR_AUTH_REQUIRED: bool = os.getenv("TWO_FACTOR_AUTH_REQUIRED", "False").lower() == "true"

    # Content Settings
    DEFAULT_BLUR_NSFW: bool = os.getenv("DEFAULT_BLUR_NSFW", "True").lower() == "true"
    DEFAULT_SHOW_EXPLICIT_ON_DASHBOARD: bool = os.getenv("DEFAULT_SHOW_EXPLICIT_ON_DASHBOARD", "False").lower() == "true"

    model_config = SettingsConfigDict(
        case_sensitive=True, 
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"  # Changed from 'forbid' to 'ignore' to allow extra fields
    )


settings = Settings()
