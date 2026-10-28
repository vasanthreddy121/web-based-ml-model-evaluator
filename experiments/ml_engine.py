import time
import math
import warnings
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from scipy.optimize import OptimizeWarning
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, SVR
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score,
    mean_absolute_error, mean_squared_error, r2_score
)
from rest_framework.exceptions import ValidationError
from datasets.services import clean_for_json

# Filter upstream SciPy 1.15+ / scikit-learn solver option mismatch warning (iprint)
warnings.filterwarnings("ignore", category=OptimizeWarning, message=r".*iprint.*")


# Whitelist Model Registry (SRS ML-EVAL-F-021, ML-EVAL-F-022, ML-EVAL-SR-005, TC-SEC-06)
MODEL_REGISTRY = {
    'classification': {
        'logistic_regression': {
            'display_name': 'Logistic Regression',
            'class': LogisticRegression,
            'default_params': {'C': 1.0, 'max_iter': 200, 'solver': 'liblinear', 'random_state': 42},
            'param_types': {'C': float, 'max_iter': int, 'solver': str, 'random_state': int}
        },
        'decision_tree': {
            'display_name': 'Decision Tree Classifier',
            'class': DecisionTreeClassifier,
            'default_params': {'max_depth': None, 'min_samples_split': 2, 'random_state': 42},
            'param_types': {'max_depth': int, 'min_samples_split': int, 'random_state': int}
        },
        'random_forest': {
            'display_name': 'Random Forest Classifier',
            'class': RandomForestClassifier,
            'default_params': {'n_estimators': 100, 'max_depth': None, 'random_state': 42},
            'param_types': {'n_estimators': int, 'max_depth': int, 'random_state': int}
        },
        'knn': {
            'display_name': 'K-Nearest Neighbors (KNN)',
            'class': KNeighborsClassifier,
            'default_params': {'n_neighbors': 5, 'weights': 'uniform'},
            'param_types': {'n_neighbors': int, 'weights': str}
        },
        'svm': {
            'display_name': 'Support Vector Machine (SVM)',
            'class': SVC,
            'default_params': {'C': 1.0, 'kernel': 'rbf', 'probability': True, 'random_state': 42},
            'param_types': {'C': float, 'kernel': str, 'random_state': int}
        },
        'naive_bayes': {
            'display_name': 'Gaussian Naive Bayes',
            'class': GaussianNB,
            'default_params': {},
            'param_types': {}
        },
    },
    'regression': {
        'linear_regression': {
            'display_name': 'Linear Regression',
            'class': LinearRegression,
            'default_params': {},
            'param_types': {}
        },
        'decision_tree_regressor': {
            'display_name': 'Decision Tree Regressor',
            'class': DecisionTreeRegressor,
            'default_params': {'max_depth': None, 'min_samples_split': 2, 'random_state': 42},
            'param_types': {'max_depth': int, 'min_samples_split': int, 'random_state': int}
        },
        'random_forest_regressor': {
            'display_name': 'Random Forest Regressor',
            'class': RandomForestRegressor,
            'default_params': {'n_estimators': 100, 'max_depth': None, 'random_state': 42},
            'param_types': {'n_estimators': int, 'max_depth': int, 'random_state': int}
        },
        'svr': {
            'display_name': 'Support Vector Regressor (SVR)',
            'class': SVR,
            'default_params': {'C': 1.0, 'kernel': 'rbf'},
            'param_types': {'C': float, 'kernel': str}
        },
        'gradient_boosting_regressor': {
            'display_name': 'Gradient Boosting Regressor',
            'class': GradientBoostingRegressor,
            'default_params': {'n_estimators': 100, 'learning_rate': 0.1, 'random_state': 42},
            'param_types': {'n_estimators': int, 'learning_rate': float, 'random_state': int}
        },
    }
}


def sanitize_hyperparameters(problem_type: str, model_name: str, user_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and sanitizes hyperparameters against the registered whitelist.
    Prevents injection of arbitrary arguments or execution of unapproved code.
    """
    model_entry = MODEL_REGISTRY[problem_type][model_name]
    params = dict(model_entry['default_params'])
    param_types = model_entry['param_types']

    if user_params and isinstance(user_params, dict):
        for k, v in user_params.items():
            if k in param_types:
                if v is None or v == '' or v == 'null':
                    params[k] = None
                    continue
                try:
                    target_type = param_types[k]
                    if target_type == int:
                        params[k] = int(v)
                    elif target_type == float:
                        params[k] = float(v)
                    elif target_type == str:
                        params[k] = str(v)
                except (ValueError, TypeError):
                    raise ValidationError(f"Invalid value '{v}' for hyperparameter '{k}'. Expected {param_types[k].__name__}.")
    return params


def compute_classification_metrics(y_true, y_pred, model, X_test) -> Dict[str, Any]:
    """Computes SRS ML-EVAL-F-032 classification metrics."""
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, average='weighted', zero_division=0))
    rec = float(recall_score(y_true, y_pred, average='weighted', zero_division=0))
    f1 = float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
    cm = confusion_matrix(y_true, y_pred).tolist()
    unique_classes = [clean_for_json(c) for c in np.unique(y_true)]

    # ROC-AUC calculation for binary classification
    roc_auc = None
    if len(unique_classes) == 2 and hasattr(model, 'predict_proba'):
        try:
            probs = model.predict_proba(X_test)
            if probs.shape[1] == 2:
                # Map target classes to 0 and 1
                pos_label = unique_classes[1]
                y_bin = (y_true == pos_label).astype(int)
                roc_auc = round(float(roc_auc_score(y_bin, probs[:, 1])), 4)
        except Exception:
            roc_auc = None

    return {
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'roc_auc': roc_auc,
        'confusion_matrix': cm,
        'classes': unique_classes
    }


def compute_regression_metrics(y_true, y_pred) -> Dict[str, Any]:
    """Computes SRS ML-EVAL-F-033 regression metrics."""
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))

    return {
        'mae': round(mae, 4),
        'mse': round(mse, 4),
        'rmse': round(rmse, 4),
        'r2_score': round(r2, 4)
    }


def train_and_evaluate_model(
    df: pd.DataFrame,
    problem_type: str,
    model_name: str,
    target_column: str,
    feature_columns: list = None,
    hyperparameters: dict = None,
    preprocessing_config: dict = None
) -> Dict[str, Any]:
    """
    Coordinates preprocessing, model training, prediction, and metric evaluation.
    Implements SRS ML-EVAL-F-020 to ML-EVAL-F-034.
    """
    problem_type = str(problem_type).lower()
    if problem_type not in MODEL_REGISTRY:
        raise ValidationError(f"Invalid problem type '{problem_type}'. Supported: {list(MODEL_REGISTRY.keys())}")

    model_name = str(model_name).lower()
    if model_name not in MODEL_REGISTRY[problem_type]:
        raise ValidationError(f"Model '{model_name}' is not supported for {problem_type}. Supported: {list(MODEL_REGISTRY[problem_type].keys())}")

    # 1. Preprocess data
    prep_config = preprocessing_config or {}
    from datasets.preprocessing import PreprocessingPipeline
    pipeline = PreprocessingPipeline(
        target_column=target_column,
        feature_columns=feature_columns,
        missing_strategy=prep_config.get('missing_strategy', 'mean'),
        handle_duplicates=prep_config.get('handle_duplicates', True),
        encoding=prep_config.get('encoding', 'one_hot'),
        scaling=prep_config.get('scaling', 'standard'),
        test_size=prep_config.get('test_size', 0.2),
        random_state=prep_config.get('random_state', 42)
    )
    prep_result = pipeline.process_and_split(df)

    X_train = prep_result['X_train']
    X_test = prep_result['X_test']
    y_train = prep_result['y_train']
    y_test = prep_result['y_test']

    # Problem-type target validation
    if problem_type == 'regression':
        if not np.issubdtype(y_train.dtype, np.number):
            raise ValidationError(f"Target '{target_column}' is non-numeric and cannot be used for regression.")
    elif problem_type == 'classification':
        # Target should have reasonable distinct classes
        if y_train.nunique() < 2:
            raise ValidationError(f"Classification target '{target_column}' must have at least 2 distinct classes in training set.")

    # 2. Model configuration & Hyperparameter sanitization
    model_entry = MODEL_REGISTRY[problem_type][model_name]
    sanitized_params = sanitize_hyperparameters(problem_type, model_name, hyperparameters or {})
    model_instance = model_entry['class'](**sanitized_params)

    # 3. Model training
    start_time = time.time()
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=OptimizeWarning, message=r".*iprint.*")
            model_instance.fit(X_train, y_train)
    except Exception as e:
        raise ValidationError(f"Model training failed: {str(e)}")
    training_duration = round(time.time() - start_time, 4)

    # 4. Predictions on test data
    try:
        y_pred = model_instance.predict(X_test)
    except Exception as e:
        raise ValidationError(f"Model prediction failed: {str(e)}")

    # 5. Evaluate Metrics
    if problem_type == 'classification':
        metrics = compute_classification_metrics(y_test, y_pred, model_instance, X_test)
    else:
        metrics = compute_regression_metrics(y_test, y_pred)

    # 6. Sample predictions for preview/comparison
    sample_records = []
    y_test_list = list(y_test)
    y_pred_list = list(y_pred)
    sample_count = min(20, len(y_test_list))
    for i in range(sample_count):
        actual = clean_for_json(y_test_list[i])
        predicted = clean_for_json(y_pred_list[i])
        rec = {
            'index': i + 1,
            'actual': actual,
            'predicted': predicted,
        }
        if problem_type == 'regression':
            try:
                rec['error'] = round(float(abs(float(actual) - float(predicted))), 4)
            except Exception:
                rec['error'] = None
        sample_records.append(rec)

    return {
        'problem_type': problem_type,
        'model_name': model_name,
        'model_display_name': model_entry['display_name'],
        'hyperparameters': sanitized_params,
        'preprocessing_summary': {
            'train_samples': prep_result['train_size'],
            'test_samples': prep_result['test_size'],
            'feature_names': prep_result['feature_names'],
            'scaling': prep_result['scaling_used'],
            'encoding': prep_result['encoding_used'],
        },
        'metrics': metrics,
        'predictions_sample': sample_records,
        'training_time_seconds': training_duration,
        'test_count': len(y_test_list)
    }

