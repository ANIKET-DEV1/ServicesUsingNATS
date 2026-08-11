from pydantic import BaseSettings


class Settings(BaseSettings):
    service_name: str = "api-gateway"
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
