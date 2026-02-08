"""Unit tests for production config — T003 TDD target."""
import os
import pytest


class TestSettings:
    """Test Pydantic Settings loads from env vars with correct defaults."""

    def test_settings_loads_from_env(self, monkeypatch):
        """Settings should load DATABASE_URL from environment."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
        monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        from production.config import Settings
        settings = Settings(_env_file=None)
        assert settings.DATABASE_URL == "postgresql://test:test@localhost:5432/test_db"
        assert settings.KAFKA_BOOTSTRAP_SERVERS == "localhost:9092"
        assert settings.OPENAI_API_KEY == "sk-test-key"

    def test_settings_defaults(self, monkeypatch):
        """Settings should have sensible defaults for non-secret config."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
        monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.delenv("LOG_LEVEL", raising=False)
        from production.config import Settings
        settings = Settings(_env_file=None)
        assert settings.LOG_LEVEL == "INFO"
        assert settings.API_HOST == "0.0.0.0"
        assert settings.API_PORT == 8000
        assert "web_form" in settings.ENABLED_CHANNELS

    def test_settings_no_hardcoded_secrets(self):
        """Ensure no default values for secret fields."""
        from production.config import Settings
        fields = Settings.model_fields
        # Secret fields must not have defaults
        for secret_field in ["OPENAI_API_KEY"]:
            field = fields[secret_field]
            assert field.default is None or field.is_required(), (
                f"{secret_field} must not have a hardcoded default"
            )

    def test_get_settings_lazy_singleton(self, monkeypatch):
        """get_settings should return cached instance."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
        monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        from production.config import get_settings
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2
