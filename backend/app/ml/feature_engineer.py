"""Feature Engineering module — handles encoding, scaling, and splitting."""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FeatureEngineer:
    def __init__(self, df: pd.DataFrame, target_column: str):
        self.df = df.copy()
        self.target_column = target_column
        self.label_encoder = None
        self.preprocessor = None
        
        # Determine feature types
        self.features = self.df.drop(columns=[self.target_column])
        self.target = self.df[self.target_column]
        
        # Identify numeric vs categorical columns
        self.numeric_features = self.features.select_dtypes(include=['int64', 'float64']).columns.tolist()
        self.categorical_features = self.features.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()

    def prepare_target(self):
        """Encode the target variable if it's categorical (classification)."""
        # If target is object/string, we assume classification and label encode it
        if self.target.dtype == 'object' or self.target.dtype.name == 'category' or self.target.dtype == 'bool':
            self.label_encoder = LabelEncoder()
            self.target = self.label_encoder.fit_transform(self.target)
            logger.info(f"Target '{self.target_column}' label encoded. Classes: {self.label_encoder.classes_}")
        else:
            # Check if it's actually classification (few unique integer values)
            if pd.api.types.is_integer_dtype(self.target) and self.target.nunique() < 20:
                self.label_encoder = LabelEncoder()
                self.target = self.label_encoder.fit_transform(self.target)
                logger.info(f"Numeric target '{self.target_column}' treated as classification. Classes: {self.label_encoder.classes_}")
            else:
                self.target = self.target.values

        return self.target

    def build_preprocessor(self):
        """Build the sklearn ColumnTransformer pipeline."""
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])

        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numeric_features),
                ('cat', categorical_transformer, self.categorical_features)
            ],
            remainder='drop'
        )
        return self.preprocessor

    def get_feature_names(self):
        """Extract output feature names from the ColumnTransformer."""
        feature_names = []
        if self.preprocessor is None:
            return feature_names

        # Numeric features remain the same
        if self.numeric_features:
            feature_names.extend(self.numeric_features)
            
        # Categorical features are one-hot encoded
        if self.categorical_features:
            # We need to fit the preprocessor first to get feature names
            cat_encoder = self.preprocessor.named_transformers_['cat'].named_steps['onehot']
            if hasattr(cat_encoder, 'get_feature_names_out'):
                cat_names = cat_encoder.get_feature_names_out(self.categorical_features)
                feature_names.extend(cat_names)
                
        return feature_names

    def split_data(self, test_size: float = 0.2, random_state: int = 42):
        """Split data into training and testing sets."""
        target_encoded = self.prepare_target()
        
        # Check if stratification is possible (only for classification)
        stratify = None
        if self.label_encoder is not None:
            # Only stratify if minimum class count > 1
            class_counts = pd.Series(target_encoded).value_counts()
            if class_counts.min() > 1:
                stratify = target_encoded

        X_train, X_test, y_train, y_test = train_test_split(
            self.features, 
            target_encoded, 
            test_size=test_size, 
            random_state=random_state,
            stratify=stratify
        )
        
        logger.info(f"Split data: Train shape {X_train.shape}, Test shape {X_test.shape}")
        return X_train, X_test, y_train, y_test
