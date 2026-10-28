import os
import json
import pytest
import numpy as np
import pandas as pd
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from rest_framework import status
from datasets.models import Dataset
from experiments.models import Experiment
from experiments.ml_engine import (
    MODEL_REGISTRY,
    train_and_evaluate_model,
    compute_classification_metrics,
    compute_regression_metrics,
    sanitize_hyperparameters
)
from experiments.services import compare_experiments, export_experiment_results
from rest_framework.exceptions import ValidationError


class TestModelTrainingAndEvaluation(TestCase):
    """
    Test suite for Issue #4 and Issue #5 corresponding to:
    - SRS: ML-EVAL-F-020 to F-023, ML-EVAL-F-030 to F-034, ML-EVAL-F-040 to F-043, ML-EVAL-SR-005
    - STP: TC-ML-01 to TC-ML-04, TC-TRAIN-01 to TC-TRAIN-03, TC-EVAL-01, TC-EVAL-02, TC-COMP-01, TC-HIST-01, TC-EXP-01, TC-SEC-06
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='ml_engineer', password='password123')

        # 1. Deterministic synthetic classification dataset (50 samples, 2 classes)
        np.random.seed(42)
        n = 50
        x1 = np.random.randn(n)
        x2 = np.random.randn(n)
        y_class = (x1 + x2 > 0).astype(int)
        self.clf_df = pd.DataFrame({'f1': x1, 'f2': x2, 'target_class': y_class})
        clf_csv = self.clf_df.to_csv(index=False).encode('utf-8')

        self.clf_file = SimpleUploadedFile("classification.csv", clf_csv, content_type="text/csv")
        self.clf_dataset = Dataset.objects.create(
            user=self.user,
            file=self.clf_file,
            filename="classification.csv",
            file_size=len(clf_csv),
            row_count=n,
            column_count=3,
            columns=['f1', 'f2', 'target_class']
        )

        # 2. Deterministic synthetic regression dataset (50 samples)
        y_reg = 2.5 * x1 - 1.5 * x2 + 5.0
        self.reg_df = pd.DataFrame({'f1': x1, 'f2': x2, 'target_reg': y_reg})
        reg_csv = self.reg_df.to_csv(index=False).encode('utf-8')

        self.reg_file = SimpleUploadedFile("regression.csv", reg_csv, content_type="text/csv")
        self.reg_dataset = Dataset.objects.create(
            user=self.user,
            file=self.reg_file,
            filename="regression.csv",
            file_size=len(reg_csv),
            row_count=n,
            column_count=3,
            columns=['f1', 'f2', 'target_reg']
        )

    def tearDown(self):
        for ds in [self.clf_dataset, self.reg_dataset]:
            if ds and ds.file and os.path.exists(ds.file.path):
                os.remove(ds.file.path)

    # -------------------------------------------------------------
    # TC-ML-02: All 6 Classification Models from SRS Registry
    # -------------------------------------------------------------
    def test_tc_ml_02_all_classification_models_train_and_predict(self):
        """
        TC-ML-02 & TC-TRAIN-01: Verify all 6 classification models can be trained and evaluated.
        Models: Logistic Regression, Decision Tree, Random Forest, KNN, SVM, Naive Bayes.
        """
        classification_models = ['logistic_regression', 'decision_tree', 'random_forest', 'knn', 'svm', 'naive_bayes']
        for model_name in classification_models:
            res = train_and_evaluate_model(
                df=self.clf_df,
                problem_type='classification',
                model_name=model_name,
                target_column='target_class',
                feature_columns=['f1', 'f2']
            )
            assert res['problem_type'] == 'classification'
            assert res['model_name'] == model_name
            assert 'accuracy' in res['metrics']
            assert 'f1_score' in res['metrics']
            assert 'confusion_matrix' in res['metrics']
            assert res['test_count'] > 0
            assert len(res['predictions_sample']) > 0

    # -------------------------------------------------------------
    # TC-ML-03: All 5 Regression Models from SRS Registry
    # -------------------------------------------------------------
    def test_tc_ml_03_all_regression_models_train_and_predict(self):
        """
        TC-ML-03 & TC-TRAIN-01: Verify all 5 regression models can be trained and evaluated.
        Models: Linear Regression, Decision Tree Regressor, Random Forest Regressor, SVR, Gradient Boosting.
        """
        regression_models = ['linear_regression', 'decision_tree_regressor', 'random_forest_regressor', 'svr', 'gradient_boosting_regressor']
        for model_name in regression_models:
            res = train_and_evaluate_model(
                df=self.reg_df,
                problem_type='regression',
                model_name=model_name,
                target_column='target_reg',
                feature_columns=['f1', 'f2']
            )
            assert res['problem_type'] == 'regression'
            assert res['model_name'] == model_name
            assert 'mae' in res['metrics']
            assert 'rmse' in res['metrics']
            assert 'r2_score' in res['metrics']
            assert res['test_count'] > 0
            assert len(res['predictions_sample']) > 0

    # -------------------------------------------------------------
    # TC-ML-04: Hyperparameters Configuration & TC-SEC-06
    # -------------------------------------------------------------
    def test_tc_ml_04_hyperparameter_configuration_and_sanitization(self):
        """
        TC-ML-04 & TC-SEC-06: Valid hyperparameter overrides are applied; illegal or unapproved parameters are ignored or raise error.
        """
        # Valid override
        params = sanitize_hyperparameters('classification', 'random_forest', {'n_estimators': '150', 'max_depth': '5'})
        assert params['n_estimators'] == 150
        assert params['max_depth'] == 5

        # Invalid type throws ValidationError
        with pytest.raises(ValidationError):
            sanitize_hyperparameters('classification', 'random_forest', {'n_estimators': 'invalid_string'})

    # -------------------------------------------------------------
    # TC-EVAL-01: Classification Metrics Accuracy
    # -------------------------------------------------------------
    def test_tc_eval_01_classification_reference_metrics(self):
        """
        TC-EVAL-01: Independent reference verification for classification metrics.
        """
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 1])
        # 4 out of 5 correct => accuracy = 0.8
        metrics = compute_classification_metrics(y_true, y_pred, None, None)
        assert metrics['accuracy'] == 0.8
        assert metrics['confusion_matrix'] == [[2, 0], [1, 2]]

    # -------------------------------------------------------------
    # TC-EVAL-02: Regression Metrics Accuracy
    # -------------------------------------------------------------
    def test_tc_eval_02_regression_reference_metrics(self):
        """
        TC-EVAL-02: Independent reference verification for regression metrics.
        """
        y_true = np.array([10.0, 20.0, 30.0])
        y_pred = np.array([12.0, 18.0, 31.0])
        # errors: 2, 2, 1 => MAE = 5/3 = 1.6667, MSE = (4+4+1)/3 = 3.0, RMSE = sqrt(3) ~ 1.7321
        metrics = compute_regression_metrics(y_true, y_pred)
        assert abs(metrics['mae'] - 1.6667) < 1e-3
        assert abs(metrics['mse'] - 3.0) < 1e-3
        assert abs(metrics['rmse'] - 1.7321) < 1e-3

    # -------------------------------------------------------------
    # TC-TRAIN-03: Controlled Error Handling
    # -------------------------------------------------------------
    def test_tc_train_03_incompatible_regression_target_controlled_error(self):
        """
        TC-TRAIN-03: Training regression on non-numeric strings results in controlled ValidationError without crash.
        """
        bad_df = pd.DataFrame({'f1': [1, 2, 3, 4, 5], 'bad_target': ['cat', 'dog', 'cat', 'dog', 'cat']})
        with pytest.raises(ValidationError) as exc:
            train_and_evaluate_model(
                df=bad_df,
                problem_type='regression',
                model_name='linear_regression',
                target_column='bad_target'
            )
        assert 'non-numeric' in str(exc.value)

    # -------------------------------------------------------------
    # REST API: Training, Results, Comparison, and Export
    # -------------------------------------------------------------
    def test_experiment_train_and_results_api_flow(self):
        """
        Verify end-to-end API: POST /api/experiments/train/ -> GET /api/experiments/<id>/results/
        """
        train_url = reverse('experiment-train-api')
        self.client.login(username='ml_engineer', password='password123')
        payload = {
            'dataset_id': self.clf_dataset.id,
            'problem_type': 'classification',
            'model_name': 'logistic_regression',
            'target_column': 'target_class',
            'feature_columns': ['f1', 'f2'],
            'hyperparameters': {'C': 1.0}
        }
        res = self.client.post(train_url, payload, content_type='application/json')
        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()
        assert data['status'] == 'success'
        exp_id = data['experiment_id']

        # Query results
        results_url = reverse('experiment-results-api', kwargs={'pk': exp_id})
        res_get = self.client.get(results_url)
        assert res_get.status_code == status.HTTP_200_OK
        res_data = res_get.json()
        assert res_data['status'] == 'success'
        assert res_data['model_name'] == 'logistic_regression'
        assert 'accuracy' in res_data['metrics']

    def test_tc_comp_01_multi_model_comparison_api(self):
        """
        TC-COMP-01: Compare two compatible experiments.
        """
        # Create two experiments
        exp1 = Experiment.objects.create(
            user=self.user,
            dataset=self.clf_dataset,
            name="Exp 1",
            problem_type="classification",
            model_name="logistic_regression",
            model_display_name="Logistic Regression",
            metrics={'accuracy': 0.85, 'f1_score': 0.84},
            training_time_seconds=0.05
        )
        exp2 = Experiment.objects.create(
            user=self.user,
            dataset=self.clf_dataset,
            name="Exp 2",
            problem_type="classification",
            model_name="random_forest",
            model_display_name="Random Forest",
            metrics={'accuracy': 0.92, 'f1_score': 0.91},
            training_time_seconds=0.15
        )

        compare_url = reverse('experiment-compare-api')
        self.client.login(username='ml_engineer', password='password123')
        res = self.client.post(compare_url, {'experiment_ids': [exp1.id, exp2.id]}, content_type='application/json')

        assert res.status_code == status.HTTP_200_OK
        comp = res.json()['comparison']
        assert comp['count'] == 2
        assert comp['best_experiment_id'] == exp2.id
        assert comp['best_model_name'] == 'Random Forest'

    def test_tc_comp_01_incompatible_problem_types_comparison_rejected(self):
        """
        TC-COMP-01: Comparing a classification experiment with a regression experiment returns 400 Bad Request.
        """
        exp_clf = Experiment.objects.create(
            user=self.user,
            dataset=self.clf_dataset,
            name="Exp Clf",
            problem_type="classification",
            model_name="logistic_regression",
            model_display_name="Logistic Regression",
            metrics={'accuracy': 0.85}
        )
        exp_reg = Experiment.objects.create(
            user=self.user,
            dataset=self.reg_dataset,
            name="Exp Reg",
            problem_type="regression",
            model_name="linear_regression",
            model_display_name="Linear Regression",
            metrics={'rmse': 1.2}
        )

        compare_url = reverse('experiment-compare-api')
        self.client.login(username='ml_engineer', password='password123')
        res = self.client.post(compare_url, {'experiment_ids': [exp_clf.id, exp_reg.id]}, content_type='application/json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cannot compare classification and regression' in res.json()['error']

    def test_tc_exp_01_export_json_and_csv(self):
        """
        TC-EXP-01: Verification that evaluation results can be exported correctly as JSON and CSV.
        """
        exp = Experiment.objects.create(
            user=self.user,
            dataset=self.clf_dataset,
            name="Export Test",
            problem_type="classification",
            model_name="decision_tree",
            model_display_name="Decision Tree Classifier",
            metrics={'accuracy': 0.90, 'f1_score': 0.89},
            predictions_sample=[{'index': 1, 'actual': 1, 'predicted': 1}]
        )

        export_url = reverse('experiment-export-api', kwargs={'pk': exp.id})
        self.client.login(username='ml_engineer', password='password123')

        # 1. JSON Export
        res_json = self.client.get(f"{export_url}?format=json")
        assert res_json.status_code == status.HTTP_200_OK
        assert res_json['Content-Type'] == 'application/json'
        data = json.loads(res_json.content.decode('utf-8'))
        assert data['experiment_id'] == exp.id
        assert data['metrics']['accuracy'] == 0.90

        # 2. CSV Export
        res_csv = self.client.get(f"{export_url}?format=csv")
        assert res_csv.status_code == status.HTTP_200_OK
        assert 'text/csv' in res_csv['Content-Type']
        assert b"--- Evaluation Metrics ---" in res_csv.content
        assert b"accuracy,0.9" in res_csv.content

    # -------------------------------------------------------------
    # Web UI Integration Tests
    # -------------------------------------------------------------
    def test_web_ui_training_and_results_flow(self):
        """
        Test web UI training flow: GET train form -> POST train form -> view results page.
        """
        train_web_url = reverse('experiment-train-web', kwargs={'dataset_id': self.clf_dataset.id})
        self.client.login(username='ml_engineer', password='password123')

        # 1. GET training form
        res_get = self.client.get(train_web_url)
        assert res_get.status_code == status.HTTP_200_OK
        assert b"Train Machine Learning Model" in res_get.content

        # 2. POST training form
        post_data = {
            'problem_type': 'classification',
            'model_name': 'decision_tree',
            'target_column': 'target_class',
            'feature_columns': ['f1', 'f2'],
            'missing_strategy': 'mean',
            'scaling': 'standard',
            'encoding': 'none',
            'test_size': 0.2
        }
        res_post = self.client.post(train_web_url, post_data, follow=True)
        assert res_post.status_code == status.HTTP_200_OK
        assert b"Evaluation Results: Decision Tree Classifier" in res_post.content
        assert b"Accuracy" in res_post.content

    def test_web_ui_history_and_compare_flow(self):
        """
        Test experiment history table and side-by-side comparison view.
        """
        exp1 = Experiment.objects.create(
            user=self.user,
            dataset=self.clf_dataset,
            name="Run 1",
            problem_type="classification",
            model_name="logistic_regression",
            model_display_name="Logistic Regression",
            metrics={'accuracy': 0.80, 'f1_score': 0.79}
        )
        exp2 = Experiment.objects.create(
            user=self.user,
            dataset=self.clf_dataset,
            name="Run 2",
            problem_type="classification",
            model_name="random_forest",
            model_display_name="Random Forest",
            metrics={'accuracy': 0.90, 'f1_score': 0.89}
        )

        history_url = reverse('experiment-history-web')
        self.client.login(username='ml_engineer', password='password123')
        res_hist = self.client.get(history_url)
        assert res_hist.status_code == status.HTTP_200_OK
        assert b"Historical Runs" in res_hist.content
        assert b"Logistic Regression" in res_hist.content
        assert b"Random Forest" in res_hist.content

        # Compare view
        compare_url = f"{reverse('experiment-compare-web')}?exp_id={exp1.id}&exp_id={exp2.id}"
        res_comp = self.client.get(compare_url)
        assert res_comp.status_code == status.HTTP_200_OK
        assert b"Multi-Model Experiment Comparison" in res_comp.content
        assert b"Recommended Top Performer" in res_comp.content
        assert b"Random Forest" in res_comp.content

    def test_tc_ml_02_logistic_regression_no_iprint_warning(self):
        """
        Verify Logistic Regression training does not produce 'Unknown solver options: iprint' warning
        under both default solver (liblinear) and explicit solver (lbfgs).
        """
        import warnings

        # Test 1: Default solver (liblinear)
        with warnings.catch_warnings(record=True) as recorded_warnings:
            warnings.simplefilter("always")
            res_default = train_and_evaluate_model(
                df=self.clf_df,
                problem_type='classification',
                model_name='logistic_regression',
                target_column='target_class',
                feature_columns=['f1', 'f2']
            )
            iprint_warnings = [
                str(w.message) for w in recorded_warnings if 'iprint' in str(w.message)
            ]
            assert len(iprint_warnings) == 0, f"Unexpected iprint warnings: {iprint_warnings}"
            assert res_default['metrics']['accuracy'] >= 0.0

        # Test 2: Explicit solver override (lbfgs)
        with warnings.catch_warnings(record=True) as recorded_warnings:
            warnings.simplefilter("always")
            res_lbfgs = train_and_evaluate_model(
                df=self.clf_df,
                problem_type='classification',
                model_name='logistic_regression',
                target_column='target_class',
                feature_columns=['f1', 'f2'],
                hyperparameters={'solver': 'lbfgs'}
            )
            iprint_warnings = [
                str(w.message) for w in recorded_warnings if 'iprint' in str(w.message)
            ]
            assert len(iprint_warnings) == 0, f"Unexpected iprint warnings: {iprint_warnings}"
            assert res_lbfgs['metrics']['accuracy'] >= 0.0

