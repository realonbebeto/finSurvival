from typing import Any, Dict, Optional

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Finlytik"
    GMAIL_ADDRESS: str = "nyamwamu.omayio@students.jkuat.ac.ke"
    GMAIL_PASSWORD: str = "Hw8P7Ku0B6^gn@O9y"
    PROFILE_QUEUE: str = 'profile'


settings = Settings()
