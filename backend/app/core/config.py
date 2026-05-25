import os
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    PROJECT_NAME: str = "LumenFlow"
    API_V1_STR: str = "/api/v1"

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "lumen"
    POSTGRES_PASSWORD: str = "lumen_pass"
    POSTGRES_DB: str = "lumenflow"
    POSTGRES_PORT: str = "5432"

    # Models / APIs
    GROQ_API_KEY: str = ""

    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True
    )
    
    # Model Configuration
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    REASONING_MODEL: str = "openai/gpt-oss-20b"

settings = Settings()