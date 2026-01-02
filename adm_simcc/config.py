from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None

    ADM_DATABASE: str = "admin"
    ADM_USER: str = "postgres"
    ADM_HOST: str = "localhost"
    ADM_PASSWORD: str = "postgres"
    ADM_PORT: int = 5432

    ALTERNATIVE_CNPQ_SERVICE: bool = False
    HOP_LOCK_FILE_PATH: Optional[str] = None
    HOP_LOG_FILE_PATH: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
