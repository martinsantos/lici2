from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # API settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Licitometro API"
    version: str = "2.0.0"
    public_api_url: str = "/api"
    api_port: str = "3003"
    api_host: str = "localhost"

    # Database (PostgreSQL only)
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_server: str = "localhost"
    postgres_port: str = "5432"
    postgres_db: str = "licitometro"

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def test_database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/licitometro_test"

    # JWT and Security
    app_secret_key: str = "your-secret-key"
    jwt_secret_key: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiry: str = "24h"
    access_token_expire_minutes: int = 30

    # Redis
    redis_url: Optional[str] = None

    # MinIO
    minio_bucket: str = "licitometro-docs"
    minio_endpoint: str = "localhost"
    minio_port: str = "9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='allow'  # Allow extra attributes
    )

settings = Settings()
