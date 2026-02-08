"""Pydantic schemas for health endpoint — per contracts/health.md."""
from datetime import datetime

from pydantic import BaseModel


class ComponentHealth(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    latency_ms: float | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    components: dict[str, ComponentHealth]
    version: str
    timestamp: datetime
