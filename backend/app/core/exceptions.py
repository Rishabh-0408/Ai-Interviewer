"""Custom exceptions and FastAPI exception handlers."""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()


# ── Domain Exceptions ────────────────────────────────────────────────────────


class AppException(Exception):
    """Base exception for application-level errors."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: str | None = None) -> None:
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=detail, status_code=status.HTTP_404_NOT_FOUND)


class ForbiddenException(AppException):
    """Access to resource is forbidden (ownership violation)."""

    def __init__(self, message: str = "You do not have access to this resource") -> None:
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class ConflictException(AppException):
    """Resource already exists or conflicts."""

    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT)


class ValidationException(AppException):
    """Custom validation error."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class FileTooLargeException(AppException):
    """Uploaded file exceeds size limit."""

    def __init__(self, max_size_mb: int = 10) -> None:
        super().__init__(
            message=f"File exceeds maximum size of {max_size_mb}MB",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )


class InvalidFileTypeException(AppException):
    """Uploaded file type is not allowed."""

    def __init__(self, allowed_types: list[str]) -> None:
        super().__init__(
            message=f"File type not allowed. Accepted types: {', '.join(allowed_types)}",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


# ── Exception Handlers ──────────────────────────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "app_exception",
            status_code=exc.status_code,
            detail=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "unhandled_exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )
