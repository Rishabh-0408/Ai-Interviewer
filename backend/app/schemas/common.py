"""Shared Pydantic schemas — pagination, errors, common types."""

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    skip: int = 0
    limit: int = 20

    model_config = ConfigDict(frozen=True)


class PaginatedResponse[T](BaseModel):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    skip: int
    limit: int

    @property
    def has_more(self) -> bool:
        return self.skip + self.limit < self.total


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
