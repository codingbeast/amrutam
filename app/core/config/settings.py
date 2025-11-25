from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # DB
    DB_USER: str = Field(default="amrutam")
    DB_PASSWORD: str = Field(default="amrutam_pass")
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str = Field(default="amrutamdb")
    DB_ECHO: bool = Field(default=False)

    # Redis
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)

    # JWT
    JWT_SECRET_KEY: str = Field(default="change_me_in_prod")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
