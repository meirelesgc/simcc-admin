from typing import Optional

from pydantic import HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    ORCID_CLIENT_ID: Optional[str] = None
    ORCID_REDIRECT_URI: Optional[str] = None
    ORCID_CLIENT_SECRET: Optional[str] = None

    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    PROXY_URL: HttpUrl = 'http://localhost:9999'
    FRONTEND_URL: HttpUrl = 'http://localhost:8080'

    PROD: bool = True

    REDIS: str = 'redis://localhost:6379/0'

    ROOT_PATH: str = str()

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
