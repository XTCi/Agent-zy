import os
from typing import List
from pydantic_settings import BaseSettings


# from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    OPENAI_API_BASE: str
    SERPAPI_API_KEY: str
    JWT_SECRET_KEY: str
    # model
    OPENAI_MODEL: str
    # App Settings
    APP_NAME: str = "FastAPI LLM Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS Settings
    ALLOW_ORIGINS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]

    # Database URLs
    DATABASE_URL: str
    REDIS_URL: str
    QDRANT_PATH: str
    QDRANT_NAME: str

    # Model Settings
    MODEL_CACHE_PATH: str = "local_models"  # 模型缓存路径

    # Log Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{line} | {message}"
    LOG_FILE: str = "logs/app.log"

    # Api jwt``
    API_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # JWT token 过期时间（分钟）

    # langsmith
    LANGCHAIN_TRACING_V2: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_PROJECT: str

    class Config:
        run_mod = os.getenv("RUN_MOD", "local")
        env_file = ".env." + run_mod  # Load environment variables from a file named .env-<RUN_MOD>

        case_sensitive = True


settings = Settings()
