from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="openai/gpt-oss-20b", alias="GROQ_MODEL")
    fetch_timeout_seconds: int = Field(default=15, alias="FETCH_TIMEOUT_SECONDS")
    max_content_chars: int = Field(default=50_000, alias="MAX_CONTENT_CHARS")
    chunk_size: int = Field(default=4_000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, alias="CHUNK_OVERLAP")
    map_reduce_threshold: int = Field(default=6_000, alias="MAP_REDUCE_THRESHOLD")
    api_key: str | None = Field(default=None, alias="API_KEY")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
