import os
import json
import pytest
import numpy as np
import pandas as pd
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from rest_framework import status
from datasets.models import Dataset
from experiments.models import Experiment


class TestEndToEndWorkflow(TestCase):
    """
    Phase 7 & Acceptance Testing:
    Validates complete end-to-end user journey across all integrated layers:
    Authentication -> Dataset Upload -> Preview/Profiling -> Preprocessing ->
    Training -> Evaluation -> Comparison -> Export -> Authorization Isolation.
    """

    def setUp(self):
        self.client = Client()

    def test_complete_ml_evaluator_lifecycle(self):
        # 1. User Registration
        reg_url = reverse('auth-register-api')
        reg_payload = {
            'username': 'lead_researcher',
            'email': 'researcher@example.com',
            'password': 'ComplexPassword123!',
            'password_confirm': 'ComplexPassword123!'
        }
        res_reg = self.client.post(reg_url, reg_payload, content_type='application/json')
        assert res_reg.status_code == status.HTTP_201_CREATED

        # 2. Upload CSV Dataset
        upload_url = reverse('dataset-upload-api')
        csv_content = (
            b"feature_a,feature_b,category,target\n"
            b"1.5,10.0,Alpha,0\n"
            b"2.5,20.0,Beta,1\n"
            b"3.5,30.0,Alpha,0\n"
            b"4.5,40.0,Beta,1\n"
            b"5.5,50.0,Alpha,0\n"
            b"6.5,60.0,Beta,1\n"
            b"7.5,70.0,Alpha,0\n"
            b"8.5,80.0,Beta,1\n"
            b"9.5,90.0,Alpha,0\n"
            b"10.5,100.0,Beta,1\n"
        )
        csv_file = SimpleUploadedFile("study_cohort.csv", csv_content, content_type="text/csv")
        res_upload = self.client.post(upload_url, {'file': csv_file})
        assert res_upload.status_code == status.HTTP_201_CREATED
        dataset_id = res_upload.json()['dataset']['id']

        # 3. Preview & Profiling
        preview_url = reverse('dataset-preview-api', kwargs={'pk': dataset_id})
        res_preview = self.client.get(preview_url)
        assert res_preview.status_code == status.HTTP_200_OK
        prof = res_preview.json()['profiling']
        assert prof['row_count'] == 10
        assert prof['column_count'] == 4
        assert prof['dtypes']['category']['simplified_type'] == 'categorical'

        # 4. Preprocessing API Check
        prep_url = reverse('dataset-preprocess-api', kwargs={'pk': dataset_id})
        prep_payload = {
            'target_column': 'target',
            'feature_columns': ['feature_a', 'feature_b', 'category'],
            'missing_strategy': 'mean',
            'scaling': 'standard',
            'encoding': 'one_hot',
            'test_size': 0.2
        }
        res_prep = self.client.post(prep_url, prep_payload, content_type='application/json')
        assert res_prep.status_code == status.HTTP_200_OK
        assert res_prep.json()['summary']['train_samples'] == 8
        assert res_prep.json()['summary']['test_samples'] == 2

        # 5. Train Model 1 (Random Forest)
        train_url = reverse('experiment-train-api')
        rf_payload = {
            'dataset_id': dataset_id,
            'name': 'Random Forest Classifier Experiment',
            'problem_type': 'classification',
            'model_name': 'random_forest',
            'target_column': 'target',
            'feature_columns': ['feature_a', 'feature_b', 'category'],
            'hyperparameters': {'n_estimators': 50},
            'preprocessing_config': {'scaling': 'standard', 'encoding': 'one_hot', 'test_size': 0.2}
        }
        res_rf = self.client.post(train_url, rf_payload, content_type='application/json')
        assert res_rf.status_code == status.HTTP_201_CREATED
        exp1_id = res_rf.json()['experiment_id']

        # 6. Train Model 2 (Logistic Regression)
        lr_payload = {
            'dataset_id': dataset_id,
            'name': 'Logistic Regression Experiment',
            'problem_type': 'classification',
            'model_name': 'logistic_regression',
            'target_column': 'target',
            'feature_columns': ['feature_a', 'feature_b', 'category'],
            'hyperparameters': {'C': 1.0},
            'preprocessing_config': {'scaling': 'standard', 'encoding': 'one_hot', 'test_size': 0.2}
        }
        res_lr = self.client.post(train_url, lr_payload, content_type='application/json')
        assert res_lr.status_code == status.HTTP_201_CREATED
        exp2_id = res_lr.json()['experiment_id']

        # 7. Model Comparison
        compare_url = reverse('experiment-compare-api')
        res_comp = self.client.post(compare_url, {'experiment_ids': [exp1_id, exp2_id]}, content_type='application/json')
        assert res_comp.status_code == status.HTTP_200_OK
        comp_data = res_comp.json()['comparison']
        assert comp_data['count'] == 2
        assert comp_data['best_experiment_id'] in (exp1_id, exp2_id)

        # 8. Export Results
        export_url = reverse('experiment-export-api', kwargs={'pk': exp1_id})
        res_exp_json = self.client.get(f"{export_url}?format=json")
        assert res_exp_json.status_code == status.HTTP_200_OK
        res_exp_csv = self.client.get(f"{export_url}?format=csv")
        assert res_exp_csv.status_code == status.HTTP_200_OK

        # 9. Authorization Isolation Test with Second User
        other_client = Client()
        other_reg_payload = {
            'username': 'external_guest',
            'password': 'OtherPassword123!',
            'password_confirm': 'OtherPassword123!'
        }
        other_client.post(reg_url, other_reg_payload, content_type='application/json')

        # Guest cannot preview first user's dataset
        res_guest_preview = other_client.get(preview_url)
        assert res_guest_preview.status_code == status.HTTP_403_FORBIDDEN

        # Guest cannot export first user's experiment
        res_guest_export = other_client.get(export_url)
        assert res_guest_export.status_code == status.HTTP_403_FORBIDDEN

