from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent 

class app_config(BaseSettings):
    user_database_url: SecretStr
    secret_key: SecretStr
    algorithms: SecretStr
    ACCESS_TOKEN_EXPIRE_MINUTE: int

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_config() -> app_config:
    return app_config()