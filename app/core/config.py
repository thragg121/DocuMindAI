from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "DocuMindAI"
    APP_VERSION: str = "0.1.0"

    EMBEDDING_MODEL: str = (
        "sentence-transformers/" "paraphrase-multilingual-MiniLM-L12-v2"
    )
    EMBEDDING_BATCH_SIZE: int = 32

    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b"

    CHAT_RETRIEVAL_LIMIT: int = 5
    CHAT_MIN_SIMILARITY: float = 0.25

    UPLOAD_DIR: str = "data/uploads"
    VECTOR_STORE_DIR: str = "data/vector_store"
    VECTOR_COLLECTION_NAME: str = "document_chunks"

    MAX_FILE_SIZE_MB: int = 50

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
