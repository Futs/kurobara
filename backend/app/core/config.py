import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    # Application
    APP_NAME: str = "Kurobara"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_URL: str = "http://localhost:8000"
    SECRET_KEY: str
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    # Database
    DB_CONNECTION: str = "postgresql"
    DB_HOST: str = "postgres"
    DB_PORT: str = "5432"
    DB_DATABASE: str = "kurobara"
    DB_USERNAME: str = "kurobara"
    DB_PASSWORD: str = "password"
    DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme=values.data.get("DB_CONNECTION", "postgresql"),
            username=values.data.get("DB_USERNAME", ""),
            password=values.data.get("DB_PASSWORD", ""),
            host=values.data.get("DB_HOST", ""),
            port=int(values.data.get("DB_PORT", 5432)),
            path=f"{values.data.get('DB_DATABASE', '')}",
        )

    # Valkey (Redis)
    VALKEY_HOST: str = "valkey"
    VALKEY_PORT: int = 6379
    VALKEY_PASSWORD: Optional[str] = None
    VALKEY_DB: int = 0

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    # Storage
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "/app/storage"
    MAX_UPLOAD_SIZE: str = "100MB"

    # Email
    MAIL_MAILER: str = "smtp"
    MAIL_HOST: str = "mailhog"
    MAIL_PORT: int = 1025
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_ENCRYPTION: Optional[str] = None
    MAIL_FROM_ADDRESS: str = "noreply@kurobara.app"
    MAIL_FROM_NAME: str = "Kurobara"

    # 2FA
    TWO_FA_ISSUER: str = "Kurobara"


settings = Settings()
