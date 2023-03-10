import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/auth/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 7 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    # SERVER_HOST: AnyHttpUrl
    ALGORITHM: str = "HS256"
    BACKEND_CORS_ORIGINS: List[Any] = [
        "*", "http://finlytik.com", "https://finlytik.com"]

    # @validator("BACKEND_CORS_ORIGINS", pre=True)
    # def assembleCorsOrigins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
    #     if isinstance(v, str) and not v.startswith("["):
    #         return [i.strip() for i in v.split(",")]
    #     elif isinstance(v, (list, str)):
    #         return v
    #     raise ValueError(v)

    PROJECT_NAME: str = "Finlytik"
    # SENTRY_DSN: Optional[HttpUrl] = None

    # @validator("SENTRY_DSN", pre=True)
    # def sentryDsnCanBeBlank(cls, v: str) -> Optional[str]:
    #     if len(v) == 0:
    #         return None
    #     return v

    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assembleDbConnection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    FIRST_SUPERUSER: EmailStr = "projobs254@gmail.com"
    FIRST_SUPERUSER_PASSWORD: str = "main123"
    USERS_OPEN_REGISTRATION: bool = True
    # EMAIL_TEST_USER: EmailStr

    # class Config:
    #     case_sensitive = True
    #     env_file = "/home/main/Documents/kazispaces/dsrc/py/finlytik-app/app/auth/.env"


settings = Settings()
