import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    frontend_url: str = 'http://localhost:3000'
    index_path: str = os.path.join(os.path.abspath(
        os.curdir), "downloads/index/pyterrier")

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
