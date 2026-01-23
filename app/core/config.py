"""Configuration centrale de l'application."""
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Configuration de l'application."""

    # Application
    app_name: str = Field(default="Lis-Moi API", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="production", alias="ENVIRONMENT")


    # MongoDB
    database_url: str = Field(..., alias="DATABASE_URL")

    # Redis
    redis_url: str = Field(..., alias="REDIS_URL")
    app_redis_prefixe: str = Field(..., alias="APP_REDIS_PREFIX")


    # JWT
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://192.168.88.39:8009"],
        alias="CORS_ORIGINS"
    )

    # File Upload
    max_upload_size: int = Field(default=10485760, alias="MAX_UPLOAD_SIZE")


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


def reload_settings():
    load_dotenv(override=True)  # Recharge les variables d'environnement
    return Settings()

settings = reload_settings()
