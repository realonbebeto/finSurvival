from pydantic import BaseSettings


class Settings(BaseSettings):
    database_username: str
    database_password: str
    database_host: str
    database_port: str
    database_name: str
    secret_key: str
    algorithm: str
    token_expire: int

    class Config:
        env_file = "/home/main/Documents/kazispaces/dsrc/py/finlytik-app/app/auth/.env"


settings = Settings()