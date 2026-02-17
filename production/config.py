"""Application configuration — Pydantic Settings with lazy singleton."""
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Environment-based configuration. All secrets from env vars."""

    # Database
    DATABASE_URL: str
    DB_MIN_CONNECTIONS: int = 5
    DB_MAX_CONNECTIONS: int = 20

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_TOPIC_INCOMING: str = "fte.tickets.incoming"
    KAFKA_TOPIC_OUTGOING: str = "fte.tickets.outgoing"
    KAFKA_TOPIC_DLQ: str = "fte.tickets.dlq"

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"

    # Gmail (optional until Gmail channel enabled)
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REFRESH_TOKEN: str = ""
    GMAIL_WATCH_EMAIL: str = "support@techcorp.com"

    # Twilio (optional until WhatsApp channel enabled)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"

    # App
    LOG_LEVEL: str = "INFO"
    ENABLED_CHANNELS: str = "web_form,email,whatsapp"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    APP_VERSION: str = "0.1.0"

    model_config = {
        "env_file": [".env", "production/.env"],
        "env_file_encoding": "utf-8",
    }


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance (lazy singleton)."""
    return Settings()
