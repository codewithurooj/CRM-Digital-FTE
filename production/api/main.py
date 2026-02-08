"""FastAPI application factory — CRM Digital FTE."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from production.api.router import api_router, register_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and teardown shared resources."""
    from production.database.pool import get_pool, close_pool
    # Initialize DB pool on startup
    await get_pool()
    yield
    # Close pool on shutdown
    await close_pool()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    from production.config import get_settings
    settings = get_settings()

    app = FastAPI(
        title="CRM Digital FTE",
        description="24/7 AI Customer Success Agent",
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global error handler — never surface raw errors (FR-036)
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
            },
        )

    # Register routes
    register_routes(api_router)
    app.include_router(api_router)

    return app


app = create_app()
