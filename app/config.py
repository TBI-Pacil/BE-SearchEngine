from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    frontend_url: str = 'http://localhost:3000'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
