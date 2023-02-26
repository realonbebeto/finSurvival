from pydantic import BaseSettings


class Settings(BaseSettings):
    postgres_username: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_database: str
    secret_key: str
    algorithm: str
    token_expire_time: int

    # class Config:
    #     env_file = "/home/main/Documents/kazispaces/dsrc/py/finlytik-app/app/auth/.env"


settings = Settings()