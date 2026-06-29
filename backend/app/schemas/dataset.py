"""Pydantic schemas for datasets."""

from pydantic import BaseModel
from datetime import datetime
from typing import Any


# ── Column Metadata ──────────────────────────────────────────

class ColumnStats(BaseModel):
    """Statistics for a single column."""
    dtype: str
    semantic_type: str | None = None
    null_count: int = 0
    null_percentage: float = 0.0
    unique_count: int = 0
    sample_values: list[Any] = []
    # Numeric-only stats
    mean: float | None = None
    median: float | None = None
    std: float | None = None
    min: float | None = None
    max: float | None = None
    q25: float | None = None
    q75: float | None = None


# ── Request Schemas ──────────────────────────────────────────

class DatasetCreate(BaseModel):
    """Metadata sent alongside file upload."""
    name: str | None = None


class DatasetUpdate(BaseModel):
    """Update dataset metadata."""
    name: str | None = None
    target_column: str | None = None
    problem_type: str | None = None


class SetTargetRequest(BaseModel):
    """Set the target column for ML."""
    target_column: str
    problem_type: str | None = None  # auto-detected if None


# ── Response Schemas ─────────────────────────────────────────

class DatasetResponse(BaseModel):
    """Full dataset representation."""
    id: str
    user_id: str
    name: str
    file_name: str
    file_url: str | None = None
    file_size_bytes: int | None = None
    row_count: int | None = None
    column_count: int | None = None
    column_metadata: dict[str, Any] | None = None
    status: str = "uploaded"
    problem_type: str | None = None
    target_column: str | None = None
    cleaning_log: list[dict] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DatasetListItem(BaseModel):
    """Lightweight dataset for list views."""
    id: str
    name: str
    file_name: str
    row_count: int | None = None
    column_count: int | None = None
    status: str = "uploaded"
    problem_type: str | None = None
    target_column: str | None = None
    created_at: datetime | None = None


class DatasetPreview(BaseModel):
    """Data preview with rows and column info."""
    columns: list[str]
    dtypes: dict[str, str]
    rows: list[dict[str, Any]]
    total_rows: int
    preview_rows: int


class DatasetStatsResponse(BaseModel):
    """Detailed statistics for a dataset."""
    dataset_id: str
    row_count: int
    column_count: int
    columns: dict[str, ColumnStats]
    memory_usage_mb: float | None = None
    correlations: dict[str, dict[str, float]] | None = None
