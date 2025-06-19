from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE: str
    PG_USER: str
    PASSWORD: str
    HOST: str
    PORT: int

    ORCID_CLIENT_ID: Optional[str] = None
    ORCID_REDIRECT_URI: Optional[str] = None
    ORCID_CLIENT_SECRET: Optional[str] = None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    def get_connection_string(self) -> str:
        return f'postgresql://{self.PG_USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}'
