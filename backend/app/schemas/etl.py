"""Pydantic schemas for ETL cleaning and validation."""

from pydantic import BaseModel
from typing import Any


# ── Cleaning Config ──────────────────────────────────────────

class CleaningConfig(BaseModel):
    """Configuration for the data cleaning pipeline."""
    handle_nulls: str = "auto"          # auto | drop | fill_median | fill_mode | fill_zero
    handle_outliers: str = "clip"       # clip | remove | median | none
    remove_duplicates: bool = True
    standardize_strings: bool = True
    remove_constant_columns: bool = True
    null_threshold: float = 0.7         # Drop columns with nulls above this %
    outlier_method: str = "iqr"         # iqr | zscore
    outlier_factor: float = 1.5         # IQR multiplier


# ── Cleaning Response ────────────────────────────────────────

class CleaningStep(BaseModel):
    """A single cleaning operation result."""
    step_name: str
    description: str
    rows_before: int
    rows_after: int
    rows_affected: int
    columns_affected: list[str] = []
    details: dict[str, Any] | None = None


class CleaningResponse(BaseModel):
    """Summary of the cleaning pipeline execution."""
    dataset_id: str
    status: str
    steps: list[CleaningStep]
    rows_before: int
    rows_after: int
    columns_before: int
    columns_after: int
    total_rows_removed: int
    total_columns_removed: int


# ── Type Inference ───────────────────────────────────────────

class InferredType(BaseModel):
    """Inferred semantic type for a column."""
    column: str
    pandas_dtype: str
    semantic_type: str
    confidence: float = 1.0
    sample_values: list[Any] = []


class TypeInferenceResponse(BaseModel):
    """Response from type inference."""
    dataset_id: str
    columns: list[InferredType]


class TypeOverride(BaseModel):
    """User override for a column type."""
    column: str
    semantic_type: str


class TypeOverrideRequest(BaseModel):
    """Batch type override request."""
    overrides: list[TypeOverride]


# ── Validation ───────────────────────────────────────────────

class ValidationIssue(BaseModel):
    """A single validation issue."""
    column: str
    issue_type: str       # type_mismatch | out_of_range | format_error | missing_values | constant
    severity: str         # error | warning | info
    row_count: int = 0
    sample_rows: list[int] = []
    message: str


class ValidationReport(BaseModel):
    """Complete validation report."""
    dataset_id: str
    total_issues: int
    errors: int
    warnings: int
    info: int
    issues: list[ValidationIssue]
    is_valid: bool
