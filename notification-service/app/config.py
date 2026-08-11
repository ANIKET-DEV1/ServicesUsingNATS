from pydantic import BaseSettings


class Settings(BaseSettings):
    service_name: str = "notification-service"
    nats_url: str = "nats://nats:4222"


settings = Settings()
