import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OrdinalEncoder
from rest_framework.exceptions import ValidationError


class PreprocessingPipeline:
    """
    Reusable data preprocessing and feature selection pipeline.
    Implements SRS ML-EVAL-F-013, ML-EVAL-F-014, ML-EVAL-F-015, TC-DATA-04, TC-DATA-05, TC-DATA-06.
    Ensures strict protection against data leakage by fitting transformations on training data only.
    """

    SUPPORTED_MISSING_STRATEGIES = ('mean', 'median', 'mode', 'drop', 'none')
    SUPPORTED_ENCODINGS = ('one_hot', 'label', 'none')
    SUPPORTED_SCALINGS = ('standard', 'minmax', 'none')

    def __init__(
        self,
        target_column: str,
        feature_columns: Optional[List[str]] = None,
        missing_strategy: str = 'mean',
        handle_duplicates: bool = True,
        encoding: str = 'one_hot',
        scaling: str = 'standard',
        test_size: float = 0.2,
        random_state: int = 42
    ):
        self.target_column = target_column
        self.feature_columns = feature_columns
        self.missing_strategy = missing_strategy.lower() if missing_strategy else 'mean'
        self.handle_duplicates = handle_duplicates
        self.encoding = encoding.lower() if encoding else 'one_hot'
        self.scaling = scaling.lower() if scaling else 'standard'
        self.test_size = float(test_size)
        self.random_state = int(random_state)

        self._validate_configuration()

    def _validate_configuration(self):
        if not self.target_column:
            raise ValidationError("Target column must be specified.")
        if self.missing_strategy not in self.SUPPORTED_MISSING_STRATEGIES:
            raise ValidationError(
                f"Unsupported missing value strategy '{self.missing_strategy}'. "
                f"Supported: {self.SUPPORTED_MISSING_STRATEGIES}"
            )
        if self.encoding not in self.SUPPORTED_ENCODINGS:
            raise ValidationError(
                f"Unsupported encoding '{self.encoding}'. Supported: {self.SUPPORTED_ENCODINGS}"
            )
        if self.scaling not in self.SUPPORTED_SCALINGS:
            raise ValidationError(
                f"Unsupported scaling '{self.scaling}'. Supported: {self.SUPPORTED_SCALINGS}"
            )
        if not (0.05 <= self.test_size <= 0.5):
            raise ValidationError("Test split ratio must be between 0.05 and 0.5 (e.g. 0.2 for 80/20 split).")

    def process_and_split(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Executes cleaning, train-test splitting, imputation, encoding, and scaling.
        Guarantees no data leakage: scalers/encoders/imputers are fit ONLY on train split.
        """
        if df.empty:
            raise ValidationError("Cannot process an empty dataset.")

        data = df.copy()

        # 1. Validate target column
        if self.target_column not in data.columns:
            raise ValidationError(f"Target column '{self.target_column}' does not exist in dataset.")

        # 2. Validate feature columns
        available_features = [c for c in data.columns if c != self.target_column]
        if not available_features:
            raise ValidationError("Dataset must contain at least one feature column besides the target.")

        if self.feature_columns:
            # Validate user selections
            missing_cols = [c for c in self.feature_columns if c not in data.columns]
            if missing_cols:
                raise ValidationError(f"Selected features not found in dataset: {missing_cols}")
            if self.target_column in self.feature_columns:
                raise ValidationError("Target variable cannot be included in input features.")
            selected_features = [c for c in self.feature_columns if c in data.columns]
            if not selected_features:
                raise ValidationError("At least one valid feature must be selected.")
        else:
            selected_features = available_features

        # 3. Handle duplicates
        duplicates_removed = 0
        if self.handle_duplicates:
            before_len = len(data)
            data = data.drop_duplicates()
            duplicates_removed = before_len - len(data)

        # 4. Drop rows where target is missing
        data = data.dropna(subset=[self.target_column])
        if len(data) < 5:
            raise ValidationError("Dataset has insufficient rows after dropping missing targets for train/test split.")

        X = data[selected_features].copy()
        y = data[self.target_column].copy()

        # 5. Train-Test Split (BEFORE any transformations to prevent data leakage)
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=self.test_size,
                random_state=self.random_state
            )
        except Exception as e:
            raise ValidationError(f"Train/test split failed: {str(e)}")

        if len(X_train) == 0 or len(X_test) == 0:
            raise ValidationError("Split resulted in empty training or testing set. Adjust test size ratio.")

        # Identify numeric and categorical columns
        numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = [c for c in selected_features if c not in numeric_cols]

        # 6. Missing Value Handling
        imputation_values = {}
        if self.missing_strategy == 'drop':
            train_mask = X_train.isna().any(axis=1)
            test_mask = X_test.isna().any(axis=1)
            X_train = X_train.loc[~train_mask]
            y_train = y_train.loc[~train_mask]
            X_test = X_test.loc[~test_mask]
            y_test = y_test.loc[~test_mask]
        elif self.missing_strategy in ('mean', 'median', 'mode'):
            for col in numeric_cols:
                if self.missing_strategy == 'median':
                    fill_val = X_train[col].median()
                else:
                    fill_val = X_train[col].mean()
                fill_val = 0.0 if pd.isna(fill_val) else fill_val
                imputation_values[col] = float(fill_val)
                X_train[col] = X_train[col].fillna(fill_val)
                X_test[col] = X_test[col].fillna(fill_val)

            for col in categorical_cols:
                mode_series = X_train[col].mode()
                fill_val = mode_series.iloc[0] if not mode_series.empty else 'missing'
                imputation_values[col] = str(fill_val)
                X_train[col] = X_train[col].fillna(fill_val)
                X_test[col] = X_test[col].fillna(fill_val)

        # 7. Categorical Encoding
        if categorical_cols and self.encoding == 'one_hot':
            X_train = pd.get_dummies(X_train, columns=categorical_cols, drop_first=False)
            X_test = pd.get_dummies(X_test, columns=categorical_cols, drop_first=False)
            # Reindex test set columns to match training set columns exactly (avoid column mismatch)
            X_train, X_test = X_train.align(X_test, join='left', axis=1, fill_value=0)
        elif categorical_cols and self.encoding == 'label':
            encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
            X_train[categorical_cols] = encoder.fit_transform(X_train[categorical_cols].astype(str))
            X_test[categorical_cols] = encoder.transform(X_test[categorical_cols].astype(str))

        # 8. Feature Scaling (Fit on Train only!)
        scale_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
        scaler = None
        if scale_cols and self.scaling == 'standard':
            scaler = StandardScaler()
            X_train[scale_cols] = scaler.fit_transform(X_train[scale_cols])
            X_test[scale_cols] = scaler.transform(X_test[scale_cols])
        elif scale_cols and self.scaling == 'minmax':
            scaler = MinMaxScaler()
            X_train[scale_cols] = scaler.fit_transform(X_train[scale_cols])
            X_test[scale_cols] = scaler.transform(X_test[scale_cols])

        transformed_features = list(X_train.columns)

        return {
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'feature_names': transformed_features,
            'duplicates_removed': duplicates_removed,
            'imputation_values': imputation_values,
            'scaling_used': self.scaling,
            'encoding_used': self.encoding,
            'test_ratio': self.test_size
        }

