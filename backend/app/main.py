"""FastAPI application factory and setup."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router
from app.core.database import engine
from app.core.exceptions import register_exception_handlers

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown events."""
    # Startup
    logger.info(
        "application_startup",
        app_name=settings.app_name,
        environment=settings.environment,
    )

    # Initialize Sentry if configured
    if settings.sentry_dsn:
        import sentry_sdk

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=0.1 if settings.is_production else 1.0,
        )
        logger.info("sentry_initialized")

    # Initialize Firebase Admin SDK if configured
    if settings.firebase_project_id:
        try:
            import firebase_admin
            from firebase_admin import credentials

            if settings.google_application_credentials:
                cred = credentials.Certificate(settings.google_application_credentials)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app(
                    options={"projectId": settings.firebase_project_id}
                )
            logger.info("firebase_initialized", project_id=settings.firebase_project_id)
        except ValueError:
            # Already initialized
            logger.debug("firebase_already_initialized")

    yield

    # Shutdown
    await engine.dispose()
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description=(
            "An evidence-driven AI interview simulator that researches the candidate's "
            "target role and organization, analyzes relevant interview patterns and core "
            "concepts, and conducts realistic adaptive interviews."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    register_exception_handlers(app)

    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            (
                structlog.dev.ConsoleRenderer()
                if not settings.is_production
                else structlog.processors.JSONRenderer()
            ),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            structlog.get_config()
            .get("wrapper_class", structlog.BoundLogger)
            .__module__
            and 0  # Default to DEBUG level
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Include API router
    app.include_router(api_router)

    # Health check
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok", "service": settings.app_name}

    return app


# Application instance
app = create_app()
