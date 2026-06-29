"""Data cleaning engine — handles missing values, outliers, and duplicates."""

import pandas as pd
import numpy as np
from app.schemas.etl import CleaningConfig, CleaningStep
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DataCleaner:
    def __init__(self, df: pd.DataFrame, config: CleaningConfig):
        self.df = df.copy()
        self.config = config
        self.steps: list[CleaningStep] = []
        self.initial_rows = df.shape[0]
        self.initial_cols = df.shape[1]

    def _add_step(self, name: str, description: str, affected_cols: list[str], rows_before: int, details: dict = None):
        """Record a cleaning step in the log."""
        rows_after = self.df.shape[0]
        self.steps.append(CleaningStep(
            step_name=name,
            description=description,
            rows_before=rows_before,
            rows_after=rows_after,
            rows_affected=rows_before - rows_after,
            columns_affected=affected_cols,
            details=details or {}
        ))

    def remove_duplicates(self):
        """Remove exact duplicate rows."""
        if not self.config.remove_duplicates:
            return

        rows_before = self.df.shape[0]
        self.df.drop_duplicates(inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        
        if rows_before != self.df.shape[0]:
            self._add_step(
                name="remove_duplicates",
                description="Removed exact duplicate rows",
                affected_cols=[],
                rows_before=rows_before
            )

    def drop_high_null_columns(self):
        """Drop columns with too many missing values."""
        null_ratios = self.df.isnull().mean()
        cols_to_drop = null_ratios[null_ratios > self.config.null_threshold].index.tolist()
        
        if cols_to_drop:
            rows_before = self.df.shape[0]
            self.df.drop(columns=cols_to_drop, inplace=True)
            self._add_step(
                name="drop_high_null_columns",
                description=f"Dropped columns with >{self.config.null_threshold*100}% nulls",
                affected_cols=cols_to_drop,
                rows_before=rows_before,
                details={"threshold": self.config.null_threshold}
            )

    def remove_constant_columns(self):
        """Drop columns that have only a single unique value."""
        if not self.config.remove_constant_columns:
            return

        cols_to_drop = [col for col in self.df.columns if self.df[col].nunique() <= 1]
        if cols_to_drop:
            rows_before = self.df.shape[0]
            self.df.drop(columns=cols_to_drop, inplace=True)
            self._add_step(
                name="remove_constant_columns",
                description="Dropped columns with zero variance (constant values)",
                affected_cols=cols_to_drop,
                rows_before=rows_before
            )

    def handle_missing_values(self):
        """Impute or drop remaining missing values."""
        if self.config.handle_nulls == "none":
            return

        rows_before = self.df.shape[0]
        affected_cols = []
        impute_map = {}

        for col in self.df.columns:
            if self.df[col].isnull().sum() == 0:
                continue
                
            affected_cols.append(col)
            
            if self.config.handle_nulls == "drop":
                self.df.dropna(subset=[col], inplace=True)
            else:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    if self.config.handle_nulls == "fill_median" or self.config.handle_nulls == "auto":
                        val = self.df[col].median()
                    elif self.config.handle_nulls == "fill_mean":
                        val = self.df[col].mean()
                    else: # fill_zero
                        val = 0
                else:
                    # Categorical/Text
                    if self.config.handle_nulls in ["fill_mode", "auto"]:
                        val = self.df[col].mode()[0] if not self.df[col].mode().empty else "Unknown"
                    else:
                        val = "Missing"
                
                self.df[col] = self.df[col].fillna(val)
                impute_map[col] = val

        if affected_cols:
            self._add_step(
                name="handle_missing_values",
                description=f"Handled missing values using strategy: {self.config.handle_nulls}",
                affected_cols=affected_cols,
                rows_before=rows_before,
                details={"impute_map": impute_map} if impute_map else {}
            )

    def handle_outliers(self):
        """Clip or remove statistical outliers in numeric columns."""
        if self.config.handle_outliers == "none":
            return

        rows_before = self.df.shape[0]
        affected_cols = []
        outlier_bounds = {}

        for col in self.df.select_dtypes(include=[np.number]).columns:
            if self.config.outlier_method == "iqr":
                q1 = self.df[col].quantile(0.25)
                q3 = self.df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - (self.config.outlier_factor * iqr)
                upper_bound = q3 + (self.config.outlier_factor * iqr)
            else: # zscore
                mean = self.df[col].mean()
                std = self.df[col].std()
                lower_bound = mean - (3 * std)
                upper_bound = mean + (3 * std)

            # Check if any outliers exist
            outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            if not outlier_mask.any():
                continue

            affected_cols.append(col)
            outlier_bounds[col] = {"lower": lower_bound, "upper": upper_bound}

            if self.config.handle_outliers == "clip":
                self.df[col] = self.df[col].clip(lower=lower_bound, upper=upper_bound)
            elif self.config.handle_outliers == "remove":
                self.df = self.df[~outlier_mask]
            elif self.config.handle_outliers == "median":
                median = self.df[col].median()
                self.df.loc[outlier_mask, col] = median

        if affected_cols:
            self._add_step(
                name="handle_outliers",
                description=f"Handled outliers using strategy: {self.config.handle_outliers}",
                affected_cols=affected_cols,
                rows_before=rows_before,
                details={"bounds": outlier_bounds}
            )

    def standardize_strings(self):
        """Strip whitespace and normalize casing for text columns."""
        if not self.config.standardize_strings:
            return

        rows_before = self.df.shape[0]
        affected_cols = []

        for col in self.df.select_dtypes(include=["object", "string"]).columns:
            # Strip whitespace
            stripped = self.df[col].str.strip()
            if not self.df[col].equals(stripped):
                self.df[col] = stripped
                affected_cols.append(col)

        if affected_cols:
            self._add_step(
                name="standardize_strings",
                description="Stripped leading/trailing whitespace from string columns",
                affected_cols=affected_cols,
                rows_before=rows_before
            )

    def run(self) -> tuple[pd.DataFrame, list[CleaningStep]]:
        """Run the full cleaning pipeline."""
        logger.info("Starting data cleaning pipeline")
        self.remove_duplicates()
        self.drop_high_null_columns()
        self.remove_constant_columns()
        self.handle_missing_values()
        self.handle_outliers()
        self.standardize_strings()
        
        logger.info(f"Finished cleaning. Final shape: {self.df.shape}")
        return self.df, self.steps
