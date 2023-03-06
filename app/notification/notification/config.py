from typing import Any, Dict, Optional

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Finlytik"
    GMAIL_ADDRESS: str
    GMAIL_PASSWORD: str
    MODEL_ADDRESS: str
    PROFILE_QUEUE: str

    class Config:
        case_sensitive = True
        env_file = "/home/main/Documents/kazispaces/dsrc/py/finlytik-app/app/auth/.env"


settings = Settings()
