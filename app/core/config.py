from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
