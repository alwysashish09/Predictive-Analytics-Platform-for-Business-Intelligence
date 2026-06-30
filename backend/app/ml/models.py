"""ML Models definition — Random Forest and XGBoost."""

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_model(model_type: str, hyperparameters: dict = None):
    """
    Factory function to instantiate the correct ML model.
    Only Classification is supported in Phase 11.
    """
    params = hyperparameters or {}
    
    if model_type == "random_forest":
        return get_random_forest(**params)
    elif model_type == "xgboost":
        return get_xgboost(**params)
    elif model_type == "ensemble":
        # For simplicity in MVP, ensemble defaults to XGBoost
        logger.info("Ensemble selected — defaulting to XGBoost for MVP")
        return get_xgboost(**params)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")


def get_random_forest(**kwargs):
    """Instantiate a RandomForestClassifier."""
    default_params = {
        'n_estimators': 100,
        'max_depth': None,
        'min_samples_split': 2,
        'min_samples_leaf': 1,
        'random_state': 42,
        'n_jobs': -1  # Use all cores
    }
    # Update defaults with provided kwargs
    for k, v in kwargs.items():
        if k in default_params and v is not None:
            default_params[k] = v
            
    logger.info(f"Initializing RandomForest with params: {default_params}")
    return RandomForestClassifier(**default_params)


def get_xgboost(**kwargs):
    """Instantiate an XGBClassifier."""
    default_params = {
        'n_estimators': 100,
        'learning_rate': 0.1,
        'max_depth': 6,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'use_label_encoder': False,
        'eval_metric': 'logloss',
        'n_jobs': -1
    }
    # Update defaults with provided kwargs
    for k, v in kwargs.items():
        if k in default_params and v is not None:
            default_params[k] = v
            
    logger.info(f"Initializing XGBoost with params: {default_params}")
    return XGBClassifier(**default_params)
