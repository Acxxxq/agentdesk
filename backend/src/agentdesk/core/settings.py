from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "mysql+asyncmy://support:support_dev_only@127.0.0.1:53306/support?charset=utf8mb4"
    redis_url: str = "redis://127.0.0.1:56379/0"
    milvus_uri: str = "http://127.0.0.1:29530"
    objectstore_endpoint: str = "127.0.0.1:19000"
    objectstore_access_key: str = ""
    objectstore_secret_key: str = ""
    objectstore_bucket: str = "agentdesk-documents"
    objectstore_secure: bool = False


@lru_cache

def get_settings() -> Settings:
    return Settings()
