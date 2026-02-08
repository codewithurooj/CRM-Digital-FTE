"""Unit tests for FastAPI app factory — T024 TDD target."""
import pytest


class TestAppFactory:
    """Test FastAPI application creation and configuration."""

    def test_app_creates(self):
        from production.api.main import create_app
        app = create_app()
        assert app is not None
        assert app.title == "CRM Digital FTE"

    def test_app_has_cors(self):
        from production.api.main import create_app
        app = create_app()
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes

    def test_app_has_routes(self):
        from production.api.main import create_app
        app = create_app()
        route_paths = [r.path for r in app.routes]
        assert "/api/v1/health" in route_paths
