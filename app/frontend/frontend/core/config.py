
from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Finlytik"
    GATEWAY_SVC_ADDRESS: str = "gateway:3100/gateway/v1"


settings = Settings()
