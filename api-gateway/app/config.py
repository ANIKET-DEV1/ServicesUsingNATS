from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class GatewaySettings(BaseSettings):
    USER_SERVICE_URL: str = "http://127.0.0.1:8001"
    GATEWAY_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_config() -> GatewaySettings:
    return GatewaySettings()
