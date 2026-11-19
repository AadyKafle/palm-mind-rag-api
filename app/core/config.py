from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str
    openai_base_url: str | None = None
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    chat_model: str = "gpt-4o-mini"

    qdrant_url: str | None = None  # if None, uses local on-disk Qdrant
    qdrant_api_key: str | None = None
    qdrant_path: str = "./qdrant_data"
    qdrant_collection: str = "documents"

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "sqlite:///./app.db"
    upload_dir: str = "./uploads"

    top_k: int = 4
    history_limit: int = 10
    chat_ttl_seconds: int = 3600


settings = Settings()