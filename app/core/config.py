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

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str
    GOOGLE_PROJECT_ID: str
    GOOGLE_AUTH_URI: str
    GOOGLE_TOKEN_URI: str
    GOOGLE_CERT_URL: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URIS: str
    GOOGLE_JAVASCRIPT_ORIGINS: str
    
    # Google API Endpoints
    GOOGLE_TOKENINFO_URL: str
    GOOGLE_USERINFO_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
