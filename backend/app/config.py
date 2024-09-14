from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    llm_provider: str = "mock"  # mock | azure | openai_compatible
    statvisor_api_key: str = "dev-local-key"

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_chat_deployment: str = "gpt-4o-mini"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"

    openai_compatible_base_url: str = ""
    openai_compatible_api_key: str = ""
    openai_compatible_chat_model: str = "gpt-4o-mini"
    openai_compatible_embedding_model: str = "text-embedding-3-small"

    dense_weight: float = 0.65
    sparse_weight: float = 0.35
    top_k: int = 5
    index_dir: str = "data/index"
    database_url: str = "sqlite:///data/statvisor.db"
    statvisor_api_url: str = "http://127.0.0.1:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
