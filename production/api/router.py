"""Route registration — all endpoint routers under /api/v1/."""
from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")


def register_routes(api_router: APIRouter) -> None:
    """Import and include all endpoint routers."""
    from production.api.endpoints import health, support_form, tickets, metrics
    from production.api.endpoints import gmail_webhook, whatsapp_webhook

    api_router.include_router(health.router, tags=["health"])
    api_router.include_router(support_form.router, tags=["support"])
    api_router.include_router(tickets.router, tags=["tickets"])
    api_router.include_router(metrics.router, tags=["metrics"])
    api_router.include_router(gmail_webhook.router, tags=["gmail"])
    api_router.include_router(whatsapp_webhook.router, tags=["whatsapp"])
