from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseEnvConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class AppConfig(BaseEnvConfig):
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    APP_VERSION: str = "0.0.0"
    PROJECT_NAME: str = "App"
    DOCS_URL: str = "/docs/index.html"
    OPENAPI_URL: str = "/docs/openapi.json"
    CORS_ORIGINS_REGEX: str = ".*"

    DEBUG: bool = False


class LoggerConfig(BaseEnvConfig):
    MAX_FRAMES_TRACEBACK: int = 5
    LOG_DISABLE_MODULES: str = "uvicorn.access,uvicorn.error, asyncio"
    LOG_LEVEL: str = "INFO"


class DatabaseConfig(BaseEnvConfig):
    PG_HOST: str = "127.0.0.1"
    PG_PORT: int = 5432
    PG_USER: str = "postgres"
    PG_PASSWORD: str = "postgres"
    PG_DB: str = ""

    def get_pg_url(self) -> str:
        return f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"


class SentryConfig(BaseEnvConfig):
    SENTRY_DSN: str = "https://..."
    SENTRY_SAMPLE_RATE: float = 1.0
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0
    SENTRY_SESSION_SAMPLE_RATE: float = 1.0
    PROFILE_LIFECYCLE: str = "trace"
    SEND_DEFAULT_PII: bool = True
    ENABLE_LOGS: bool = False


class Settings(BaseEnvConfig):
    app: AppConfig = Field(default_factory=AppConfig)
    logger: LoggerConfig = Field(default_factory=LoggerConfig)
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    sentry: SentryConfig = Field(default_factory=SentryConfig)
