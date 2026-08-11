from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import DirectoryPath, Field, SecretStr
from functools import lru_cache
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent

class app_config(BaseSettings):
    notification_database_url:SecretStr

    model_config=SettingsConfigDict(env_file=".env", extra="ignore")


def get_config() -> app_config:
    return app_config()