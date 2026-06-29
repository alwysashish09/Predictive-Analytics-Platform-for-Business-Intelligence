"""Type inference and validation engine."""

import pandas as pd
import numpy as np
from app.schemas.etl import InferredType, ValidationIssue, ValidationReport
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Validator:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def infer_types(self) -> list[InferredType]:
        """Infer semantic types (numeric, categorical, datetime, text, boolean) for all columns."""
        inferred = []
        for col in self.df.columns:
            series = self.df[col]
            pandas_dtype = str(series.dtype)
            semantic_type = "text"
            confidence = 1.0

            if pd.api.types.is_numeric_dtype(series):
                # Check if it's actually categorical (e.g., 0/1 or few distinct integers)
                if pd.api.types.is_integer_dtype(series) and series.nunique() < 10:
                    semantic_type = "categorical"
                    confidence = 0.8
                else:
                    semantic_type = "numeric"
            elif pd.api.types.is_bool_dtype(series):
                semantic_type = "boolean"
            elif pd.api.types.is_datetime64_any_dtype(series):
                semantic_type = "datetime"
            else:
                # Object/String dtype
                unique_ratio = series.nunique() / max(1, series.shape[0])
                if series.nunique() < 15 or unique_ratio < 0.05:
                    semantic_type = "categorical"
                else:
                    # Try to parse as datetime
                    try:
                        pd.to_datetime(series.dropna().head(10))
                        semantic_type = "datetime"
                        confidence = 0.7
                    except (ValueError, TypeError):
                        semantic_type = "text"

            sample_vals = series.dropna().head(3).tolist()
            # Serialize samples safely
            safe_samples = []
            for v in sample_vals:
                if pd.isna(v): continue
                if isinstance(v, pd.Timestamp): safe_samples.append(v.isoformat())
                elif hasattr(v, "item"): safe_samples.append(v.item())
                else: safe_samples.append(v)

            inferred.append(InferredType(
                column=col,
                pandas_dtype=pandas_dtype,
                semantic_type=semantic_type,
                confidence=confidence,
                sample_values=safe_samples
            ))
            
        return inferred

    def validate(self, dataset_id: str) -> ValidationReport:
        """Run validation checks on the dataset."""
        issues = []
        
        for col in self.df.columns:
            series = self.df[col]
            
            # 1. Missing values
            null_count = int(series.isnull().sum())
            if null_count > 0:
                null_pct = null_count / len(series)
                severity = "error" if null_pct > 0.5 else "warning"
                issues.append(ValidationIssue(
                    column=col,
                    issue_type="missing_values",
                    severity=severity,
                    row_count=null_count,
                    message=f"Column has {null_count} missing values ({null_pct*100:.1f}%)"
                ))

            # 2. Constant columns
            if series.nunique() <= 1:
                issues.append(ValidationIssue(
                    column=col,
                    issue_type="constant",
                    severity="warning",
                    row_count=len(series),
                    message="Column has a constant value and provides no variance."
                ))

            # 3. Type mismatches (mixed types in object columns)
            if pd.api.types.is_object_dtype(series):
                types = series.dropna().map(type).unique()
                if len(types) > 1:
                    type_names = [t.__name__ for t in types]
                    issues.append(ValidationIssue(
                        column=col,
                        issue_type="type_mismatch",
                        severity="error",
                        row_count=len(series),
                        message=f"Column contains mixed types: {', '.join(type_names)}"
                    ))

        # Count severity
        errors = sum(1 for i in issues if i.severity == "error")
        warnings = sum(1 for i in issues if i.severity == "warning")
        infos = sum(1 for i in issues if i.severity == "info")

        return ValidationReport(
            dataset_id=dataset_id,
            total_issues=len(issues),
            errors=errors,
            warnings=warnings,
            info=infos,
            issues=issues,
            is_valid=errors == 0
        )
