from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/ims"
    TIMESCALE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/ims"
    MONGO_URL: str = "mongodb://admin:password@localhost:27017"
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"

settings = Settings()
