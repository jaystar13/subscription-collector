from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str
    YOUTUBE_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()    