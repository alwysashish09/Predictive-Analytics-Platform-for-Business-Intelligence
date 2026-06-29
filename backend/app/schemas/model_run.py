"""Pydantic schemas for model runs and predictions."""

from pydantic import BaseModel
from datetime import datetime
from typing import Any


# ── Model Run Schemas ────────────────────────────────────────

class ModelRunCreate(BaseModel):
    """Request to start a model training run."""
    dataset_id: str
    model_type: str = "ensemble"    # random_forest | xgboost | ensemble
    target_column: str | None = None
    hyperparameters: dict[str, Any] | None = None
    tune_hyperparameters: bool = False
    cv_folds: int = 5


class ModelMetrics(BaseModel):
    """Model performance metrics."""
    # Classification
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1_score: float | None = None
    auc_roc: float | None = None
    confusion_matrix: list[list[int]] | None = None
    classification_report: dict | None = None
    # Regression
    r2: float | None = None
    adjusted_r2: float | None = None
    rmse: float | None = None
    mae: float | None = None
    mape: float | None = None
    # Cross-validation
    cv_scores: list[float] | None = None
    cv_mean: float | None = None
    cv_std: float | None = None


class FeatureImportance(BaseModel):
    """Feature importance entry."""
    feature: str
    importance: float
    rank: int


class ModelRunResponse(BaseModel):
    """Full model run details."""
    id: str
    user_id: str
    dataset_id: str
    model_type: str
    hyperparameters: dict[str, Any] | None = None
    metrics: ModelMetrics | None = None
    feature_importance: list[FeatureImportance] | None = None
    model_file_path: str | None = None
    status: str = "training"
    training_duration_sec: float | None = None
    created_at: datetime | None = None


class ModelRunListItem(BaseModel):
    """Lightweight model run for list views."""
    id: str
    dataset_id: str
    model_type: str
    status: str
    metrics: dict[str, Any] | None = None
    training_duration_sec: float | None = None
    created_at: datetime | None = None


class ModelCompareResponse(BaseModel):
    """Side-by-side model comparison."""
    runs: list[ModelRunResponse]


class CVResults(BaseModel):
    """Cross-validation results."""
    fold_metrics: list[dict[str, Any]]
    mean_metrics: dict[str, float]
    std_metrics: dict[str, float]
    ensemble_weights: list[float] | None = None


# ── Prediction Schemas ───────────────────────────────────────

class PredictionRequest(BaseModel):
    """Request to make predictions."""
    model_run_id: str
    input_data: list[dict[str, Any]]


class PredictionResult(BaseModel):
    """Single prediction with confidence."""
    value: Any
    confidence_lower: float | None = None
    confidence_upper: float | None = None
    probability: float | None = None


class PredictionResponse(BaseModel):
    """Batch prediction results."""
    model_run_id: str
    predictions: list[PredictionResult]
    model_type: str
    created_at: datetime | None = None
