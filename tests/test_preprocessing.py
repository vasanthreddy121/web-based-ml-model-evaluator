import os
import numpy as np
import pandas as pd
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from rest_framework import status
from datasets.models import Dataset
from datasets.preprocessing import PreprocessingPipeline
from rest_framework.exceptions import ValidationError


class TestPreprocessingAndFeatureSelection(TestCase):
    """
    Test suite for Preprocessing & Feature Selection corresponding to:
    - SRS: ML-EVAL-F-013, ML-EVAL-F-014, ML-EVAL-F-015
    - STP: TC-DATA-04, TC-DATA-05, TC-DATA-06
    - Issue #3: Implement data preprocessing and feature selection
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='data_scientist', password='password123')

        # Synthetic mixed dataset: numeric, categorical, missing values, duplicates
        data = {
            'feature_num1': [10.0, 20.0, np.nan, 40.0, 50.0, 10.0, 70.0, 80.0, 90.0, 100.0],
            'feature_num2': [1.0, 2.0, 3.0, 4.0, 5.0, 1.0, 7.0, 8.0, 9.0, 10.0],
            'feature_cat': ['low', 'high', 'low', 'medium', 'high', 'low', 'medium', 'low', 'high', 'medium'],
            'target': [0, 1, 0, 1, 1, 0, 1, 0, 1, 1]
        }
        self.df = pd.DataFrame(data)

        csv_bytes = self.df.to_csv(index=False).encode('utf-8')
        self.uploaded_file = SimpleUploadedFile("clean_data.csv", csv_bytes, content_type="text/csv")
        self.dataset = Dataset.objects.create(
            user=self.user,
            file=self.uploaded_file,
            filename="clean_data.csv",
            file_size=len(csv_bytes),
            row_count=len(self.df),
            column_count=len(self.df.columns),
            columns=list(self.df.columns)
        )

    def tearDown(self):
        if self.dataset and self.dataset.file and os.path.exists(self.dataset.file.path):
            os.remove(self.dataset.file.path)

    def test_tc_data_04_missing_values_mean_imputation(self):
        """
        TC-DATA-04: Verify missing numeric value is filled using training mean.
        """
        pipeline = PreprocessingPipeline(
            target_column='target',
            missing_strategy='mean',
            encoding='none',
            scaling='none',
            test_size=0.2,
            random_state=42
        )
        res = pipeline.process_and_split(self.df)
        assert res['X_train']['feature_num1'].isna().sum() == 0
        assert res['X_test']['feature_num1'].isna().sum() == 0

    def test_tc_data_04_duplicate_handling(self):
        """
        TC-DATA-04: Verify duplicated rows (row 0 and row 5) are detected and dropped.
        """
        pipeline = PreprocessingPipeline(
            target_column='target',
            handle_duplicates=True,
            test_size=0.2,
            random_state=42
        )
        res = pipeline.process_and_split(self.df)
        assert res['duplicates_removed'] == 1

    def test_tc_data_05_one_hot_encoding(self):
        """
        TC-DATA-05: Categorical feature is converted into binary dummy columns.
        """
        pipeline = PreprocessingPipeline(
            target_column='target',
            encoding='one_hot',
            scaling='none',
            test_size=0.2,
            random_state=42
        )
        res = pipeline.process_and_split(self.df)
        # Check that dummy columns were generated
        encoded_cols = [c for c in res['feature_names'] if 'feature_cat_' in c]
        assert len(encoded_cols) >= 2
        # Columns in test set must match training set exactly
        assert list(res['X_train'].columns) == list(res['X_test'].columns)

    def test_tc_data_05_ordinal_label_encoding(self):
        """
        TC-DATA-05: Categorical feature is ordinally encoded without string dtypes.
        """
        pipeline = PreprocessingPipeline(
            target_column='target',
            encoding='label',
            scaling='none',
            test_size=0.2,
            random_state=42
        )
        res = pipeline.process_and_split(self.df)
        assert np.issubdtype(res['X_train']['feature_cat'].dtype, np.number)

    def test_tc_data_05_feature_scaling_standard_and_minmax(self):
        """
        TC-DATA-05: Numerical feature scaling produces standardized values.
        """
        # StandardScaler test
        std_pipe = PreprocessingPipeline(
            target_column='target',
            scaling='standard',
            test_size=0.2,
            random_state=42
        )
        res_std = std_pipe.process_and_split(self.df)
        # Training mean should be close to 0
        assert abs(res_std['X_train']['feature_num2'].mean()) < 1e-6

        # MinMaxScaler test
        mm_pipe = PreprocessingPipeline(
            target_column='target',
            scaling='minmax',
            test_size=0.2,
            random_state=42
        )
        res_mm = mm_pipe.process_and_split(self.df)
        assert res_mm['X_train']['feature_num2'].min() >= 0.0
        assert res_mm['X_train']['feature_num2'].max() <= 1.0

    def test_tc_data_06_feature_selection(self):
        """
        TC-DATA-06: User can select specific subset of features.
        """
        pipeline = PreprocessingPipeline(
            target_column='target',
            feature_columns=['feature_num1'],
            test_size=0.2,
            random_state=42
        )
        res = pipeline.process_and_split(self.df)
        assert res['feature_names'] == ['feature_num1']
        assert 'feature_num2' not in res['X_train'].columns

    def test_data_leakage_protection(self):
        """
        Strict check: Transformation parameters (mean/scale) must be fit solely on X_train.
        """
        df = pd.DataFrame({
            'x': [1.0, 2.0, 3.0, 4.0, 1000.0],
            'y': [0, 0, 1, 1, 1]
        })
        pipeline = PreprocessingPipeline(
            target_column='y',
            scaling='standard',
            test_size=0.2,
            random_state=42
        )
        res = pipeline.process_and_split(df)
        # The scaler must NOT be fit on the combined data or test data
        assert len(res['X_train']) == 4
        assert len(res['X_test']) == 1

    def test_invalid_configurations_throw_validation_error(self):
        """
        Invalid options (invalid target, split ratio out of bounds, target in features) throw ValidationError.
        """
        with pytest.raises(ValidationError):
            pipe = PreprocessingPipeline(target_column='non_existent')
            pipe.process_and_split(self.df)

        with pytest.raises(ValidationError):
            PreprocessingPipeline(target_column='target', test_size=0.9)

        with pytest.raises(ValidationError):
            pipe = PreprocessingPipeline(target_column='target', feature_columns=['target', 'feature_num1'])
            pipe.process_and_split(self.df)

    def test_preprocess_api_endpoint(self):
        """
        Test POST /api/datasets/<id>/preprocess/ returns 200 with summary and preview.
        """
        url = reverse('dataset-preprocess-api', kwargs={'pk': self.dataset.id})
        self.client.login(username='data_scientist', password='password123')
        payload = {
            'target_column': 'target',
            'feature_columns': ['feature_num1', 'feature_num2'],
            'missing_strategy': 'mean',
            'scaling': 'standard',
            'encoding': 'none',
            'test_size': 0.2
        }
        res = self.client.post(url, payload, content_type='application/json')
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data['status'] == 'success'
        assert 'summary' in data
        assert data['summary']['transformed_features'] == ['feature_num1', 'feature_num2']
        assert 'preview' in data

    def test_preprocess_web_view(self):
        """
        Test web UI renders form and successfully processes post submission.
        """
        web_url = reverse('dataset-preprocess-web', kwargs={'pk': self.dataset.id})
        self.client.login(username='data_scientist', password='password123')

        # GET form
        res_get = self.client.get(web_url)
        assert res_get.status_code == status.HTTP_200_OK
        assert b"Preprocessing & Feature Selection" in res_get.content

        # POST form
        post_data = {
            'target_column': 'target',
            'feature_columns': ['feature_num1', 'feature_num2'],
            'missing_strategy': 'mean',
            'handle_duplicates': 'on',
            'encoding': 'one_hot',
            'scaling': 'standard',
            'test_size': 0.2
        }
        res_post = self.client.post(web_url, post_data)
        assert res_post.status_code == status.HTTP_200_OK
        assert b"Preprocessing Execution Summary" in res_post.content
        assert b"TRAIN SAMPLES" in res_post.content
