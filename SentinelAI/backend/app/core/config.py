from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "sentinelai_super_secret_key_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()