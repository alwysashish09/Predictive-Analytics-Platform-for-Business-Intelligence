"""ML Pipeline orchestrator — trains models, calculates metrics, and saves to disk."""

import time
import os
import joblib
import numpy as np
from sklearn.pipeline import Pipeline as SklearnPipeline
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, roc_auc_score
from app.ml.feature_engineer import FeatureEngineer
from app.ml.models import get_model
from app.schemas.model_run import ModelMetrics, FeatureImportance
from app.utils.logger import get_logger

logger = get_logger(__name__)

MODELS_DIR = os.path.join(os.getcwd(), "models")
os.makedirs(MODELS_DIR, exist_ok=True)


class MLPipeline:
    def __init__(self, run_id: str, df, target_column: str, model_type: str, hyperparameters: dict = None):
        self.run_id = run_id
        self.df = df
        self.target_column = target_column
        self.model_type = model_type
        self.hyperparameters = hyperparameters or {}
        
        self.engineer = FeatureEngineer(df, target_column)
        self.model = None
        self.pipeline = None
        self.metrics = None
        self.feature_importance = None
        self.model_path = None
        self.training_duration = 0

    def run(self):
        """Execute the full training pipeline."""
        start_time = time.time()
        
        # 1. Split Data
        X_train, X_test, y_train, y_test = self.engineer.split_data()
        
        # 2. Build Preprocessor
        preprocessor = self.engineer.build_preprocessor()
        
        # 3. Initialize Model
        self.model = get_model(self.model_type, self.hyperparameters)
        
        # 4. Create Scikit-Learn Pipeline
        self.pipeline = SklearnPipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', self.model)
        ])
        
        # 5. Train
        logger.info(f"Training {self.model_type} pipeline...")
        self.pipeline.fit(X_train, y_train)
        
        self.training_duration = time.time() - start_time
        logger.info(f"Training completed in {self.training_duration:.2f} seconds")
        
        # 6. Evaluate
        self._evaluate(X_test, y_test)
        
        # 7. Extract Feature Importance
        self._extract_feature_importance()
        
        # 8. Save Model
        self._save_model()
        
        return {
            "metrics": self.metrics,
            "feature_importance": self.feature_importance,
            "model_file_path": self.model_path,
            "training_duration_sec": self.training_duration
        }

    def _evaluate(self, X_test, y_test):
        """Calculate classification metrics."""
        y_pred = self.pipeline.predict(X_test)
        
        # Accuracy
        acc = accuracy_score(y_test, y_pred)
        
        # Precision, Recall, F1 (weighted for multiclass)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=0)
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # AUC-ROC (if probabilities are supported and binary classification)
        auc = None
        try:
            if hasattr(self.pipeline, "predict_proba"):
                y_prob = self.pipeline.predict_proba(X_test)
                num_classes = len(np.unique(y_test))
                if num_classes == 2:
                    auc = roc_auc_score(y_test, y_prob[:, 1])
                elif num_classes > 2:
                    # Multi-class AUC
                    auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
        except Exception as e:
            logger.warning(f"Could not calculate AUC-ROC: {e}")

        self.metrics = ModelMetrics(
            accuracy=acc,
            precision=precision,
            recall=recall,
            f1_score=f1,
            auc_roc=auc,
            confusion_matrix=cm.tolist()
        )
        logger.info(f"Evaluation metrics: Accuracy={acc:.4f}, F1={f1:.4f}")

    def _extract_feature_importance(self):
        """Extract feature importances from tree-based models."""
        try:
            classifier = self.pipeline.named_steps['classifier']
            
            # Not all models have feature_importances_
            if not hasattr(classifier, 'feature_importances_'):
                return
                
            importances = classifier.feature_importances_
            feature_names = self.engineer.get_feature_names()
            
            # If lengths don't match (shouldn't happen, but safe fallback)
            if len(importances) != len(feature_names):
                feature_names = [f"Feature_{i}" for i in range(len(importances))]
                
            # Create list of dicts, sorted by importance
            feat_imp = [
                {"feature": str(f), "importance": float(i)}
                for f, i in zip(feature_names, importances)
            ]
            feat_imp = sorted(feat_imp, key=lambda x: x['importance'], reverse=True)
            
            # Add rank and keep top 20
            self.feature_importance = []
            for rank, item in enumerate(feat_imp[:20], 1):
                self.feature_importance.append(
                    FeatureImportance(
                        feature=item['feature'],
                        importance=item['importance'],
                        rank=rank
                    )
                )
        except Exception as e:
            logger.error(f"Failed to extract feature importance: {e}")
            self.feature_importance = []

    def _save_model(self):
        """Serialize pipeline to disk."""
        filename = f"model_{self.run_id}.pkl"
        path = os.path.join(MODELS_DIR, filename)
        
        # Save the full sklearn pipeline AND the label encoder
        model_artifact = {
            "pipeline": self.pipeline,
            "label_encoder": self.engineer.label_encoder,
            "target_column": self.target_column
        }
        
        joblib.dump(model_artifact, path)
        self.model_path = path
        logger.info(f"Model saved to {path}")
