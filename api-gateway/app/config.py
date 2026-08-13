from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# api-gateway/app/config.py → parent = api-gateway/app → parent = api-gateway → parent = project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # project root


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
