from pydantic import BaseModel
from typing import Any, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Any = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: str | None = None


class PaginatedResponse(BaseModel):
    """Paginated list response."""
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class TimestampMixin(BaseModel):
    """Mixin for timestamps."""
    created_at: datetime | None = None
    updated_at: datetime | None = None
