import os
import json
import math
import tempfile
import numpy as np
import pandas as pd
from unittest.mock import patch
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from rest_framework import status
from datasets.models import Dataset
from datasets.services import profile_dataset, clean_for_json
from rest_framework.exceptions import NotFound


class TestDatasetPreviewProfiling(TestCase):
    """
    Test suite for Dataset Preview & Profiling corresponding to:
    - SRS: ML-EVAL-F-012, ML-EVAL-NF-001, ML-EVAL-NF-004
    - STP: TC-DATA-03, TC-PERF-01, TC-SEC-01, TC-SEC-05
    - Issue #2: Implement dataset preview and profiling
    """

    def setUp(self):
        self.client = Client()
        self.user_a = User.objects.create_user(username='user_a', password='password123')
        self.user_b = User.objects.create_user(username='user_b', password='password123')

        # CSV with mixed types, 1 duplicate row, and 1 missing value
        csv_content = (
            b"age,salary,department,promoted\n"
            b"25,50000.0,Engineering,1\n"
            b"30,60000.0,Marketing,0\n"
            b"25,50000.0,Engineering,1\n"  # Duplicate of row 1
            b"40,,Sales,1\n"               # Missing salary
        )
        self.file = SimpleUploadedFile("employees.csv", csv_content, content_type="text/csv")
        self.dataset = Dataset.objects.create(
            user=self.user_a,
            file=self.file,
            filename="employees.csv",
            file_size=len(csv_content),
            row_count=4,
            column_count=4,
            columns=["age", "salary", "department", "promoted"]
        )

    def tearDown(self):
        if self.dataset and self.dataset.file and os.path.exists(self.dataset.file.path):
            os.remove(self.dataset.file.path)

    def test_tc_data_03_preview_and_profiling_api(self):
        """
        TC-DATA-03: Verify preview API returns correct rows, columns, data types,
        missing value counts, duplicate count, and summary statistics.
        """
        url = reverse('dataset-preview-api', kwargs={'pk': self.dataset.id})
        self.client.login(username='user_a', password='password123')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert data['dataset_id'] == self.dataset.id
        assert data['filename'] == 'employees.csv'

        profiling = data['profiling']
        assert profiling['row_count'] == 4
        assert profiling['column_count'] == 4
        assert profiling['columns'] == ["age", "salary", "department", "promoted"]

        # Missing values detection
        assert profiling['missing_values']['total_missing'] == 1
        assert profiling['missing_values']['by_column']['salary']['count'] == 1
        assert profiling['missing_values']['by_column']['age']['count'] == 0

        # Duplicate detection (1 duplicate row)
        assert profiling['duplicate_rows_count'] == 1

        # Dtypes detection
        assert profiling['dtypes']['age']['simplified_type'] == 'integer'
        assert profiling['dtypes']['salary']['simplified_type'] == 'numeric'
        assert profiling['dtypes']['department']['simplified_type'] == 'categorical'

        # Preview rows (up to 10)
        assert len(profiling['preview']) == 4

        # Statistics computation
        assert 'age' in profiling['statistics']
        assert profiling['statistics']['age']['min'] == 25
        assert profiling['statistics']['age']['max'] == 40
        assert 'department' in profiling['statistics']
        assert profiling['statistics']['department']['type'] == 'categorical'
        assert profiling['statistics']['department']['unique'] == 3

    def test_tc_data_03_preview_not_found(self):
        """
        TC-DATA-03: Requesting preview for non-existent dataset returns 404.
        """
        url = reverse('dataset-preview-api', kwargs={'pk': 99999})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'not found' in response.json()['error'].lower()

    def test_tc_sec_01_preview_cross_user_isolation(self):
        """
        TC-SEC-01 / TC-SEC-05: User B cannot access preview of dataset owned by User A.
        """
        url = reverse('dataset-preview-api', kwargs={'pk': self.dataset.id})
        self.client.login(username='user_b', password='password123')
        response = self.client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert data['status'] == 'error'
        assert 'permission' in data['error'].lower()

    def test_preview_web_view_success_and_forbidden(self):
        """
        Verify web UI displays dataset preview for owner and blocks unauthorized users.
        """
        web_url = reverse('dataset-preview-web', kwargs={'pk': self.dataset.id})

        # Owner access
        self.client.login(username='user_a', password='password123')
        res_a = self.client.get(web_url)
        assert res_a.status_code == status.HTTP_200_OK
        assert b"Dataset Profile: employees.csv" in res_a.content
        assert b"Engineering" in res_a.content

        # Unauthorized user access redirects with error
        self.client.login(username='user_b', password='password123')
        res_b = self.client.get(web_url, follow=True)
        assert res_b.status_code == status.HTTP_200_OK
        assert b"Access denied" in res_b.content

    def test_profile_dataset_nonexistent_file(self):
        """
        Verify service raises NotFound if the underlying file is missing.
        """
        with pytest.raises(NotFound):
            profile_dataset("/path/to/nonexistent/file.csv")


class TestDatasetProfilingEdgeCases(TestCase):
    """
    Comprehensive edge-case test suite for dataset profiling (GitHub Issue #15).
    Covers:
    - Minimal datasets (1-row, 1-col numeric, 1-col categorical, 1-cell)
    - Missing values (partial, multi-col, 100% missing numeric and categorical)
    - Duplicate rows (0 duplicates, partial duplicates, 100% duplicate datasets)
    - Numerical statistics edge cases (zero variance, negative, high precision float, large numbers)
    - Categorical statistics edge cases (single category, all unique, mode, frequency)
    - Special values (NaN, Inf, -Inf) and JSON serializability
    - Preview truncation (default limit, custom limit, smaller than limit)
    - API & Web UI integration for edge-case datasets
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='edge_user', password='password123')
        self._created_datasets = []
        self._temp_files = []

    def tearDown(self):
        for ds in self._created_datasets:
            if ds and ds.file and os.path.exists(ds.file.path):
                try:
                    os.remove(ds.file.path)
                except OSError:
                    pass
        for temp_path in self._temp_files:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    def _create_temp_csv(self, content_str: str) -> str:
        f = tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', encoding='utf-8')
        f.write(content_str)
        f.flush()
        f.close()
        self._temp_files.append(f.name)
        return f.name

    def _create_dataset(self, filename: str, content: bytes, user=None) -> Dataset:
        if user is None:
            user = self.user
        uploaded_file = SimpleUploadedFile(filename, content, content_type="text/csv")
        dataset = Dataset.objects.create(
            user=user,
            file=uploaded_file,
            filename=filename,
            file_size=len(content),
            row_count=0,
            column_count=0,
            columns=[]
        )
        self._created_datasets.append(dataset)
        return dataset

    # -------------------------------------------------------------------------
    # 1. Scalar types & Special Values (clean_for_json)
    # -------------------------------------------------------------------------

    def test_clean_for_json_scalar_types_and_edge_values(self):
        """
        Verify clean_for_json correctly serializes numpy scalars, booleans, timestamps,
        and sanitizes NaN/Inf values to None.
        """
        assert clean_for_json(None) is None
        assert clean_for_json(np.nan) is None
        assert clean_for_json(float('nan')) is None
        assert clean_for_json(np.inf) is None
        assert clean_for_json(float('inf')) is None
        assert clean_for_json(-np.inf) is None
        assert clean_for_json(float('-inf')) is None

        # Integer types (ordinary Python int and NumPy integers)
        assert clean_for_json(42) == 42
        assert isinstance(clean_for_json(42), int)
        assert not isinstance(clean_for_json(42), bool)

        int_val = clean_for_json(np.int64(42))
        assert int_val == 42
        assert isinstance(int_val, int)
        assert not isinstance(int_val, bool)

        # Floating types rounded to 4 decimals
        float_val = clean_for_json(np.float64(3.14159265))
        assert float_val == 3.1416
        assert isinstance(float_val, float)

        # Boolean and string
        assert clean_for_json(np.bool_(True)) is True
        assert clean_for_json("sample_string") == "sample_string"

        # Timestamp
        ts_val = clean_for_json(pd.Timestamp("2026-01-01 12:00:00"))
        assert ts_val == "2026-01-01 12:00:00"

    def test_clean_for_json_integer_preservation_and_type_fidelity(self):
        """
        Regression Test: Verify clean_for_json preserves integer types without
        converting them to strings, preserves booleans without coercion to ints,
        and cleanly handles nested dictionaries and lists.
        """
        # 1. clean_for_json(42) returns integer 42
        res_42 = clean_for_json(42)
        assert res_42 == 42
        assert isinstance(res_42, int)
        assert not isinstance(res_42, bool)

        # 2. clean_for_json(-10) returns integer -10
        res_neg = clean_for_json(-10)
        assert res_neg == -10
        assert isinstance(res_neg, int)
        assert not isinstance(res_neg, bool)

        # 3. clean_for_json(np.int64(42)) returns integer 42
        res_np_int = clean_for_json(np.int64(42))
        assert res_np_int == 42
        assert isinstance(res_np_int, int)
        assert not isinstance(res_np_int, bool)

        # 4. clean_for_json(95.5) remains a float
        res_float = clean_for_json(95.5)
        assert res_float == 95.5
        assert isinstance(res_float, float)

        # 5. clean_for_json(True) remains Boolean True
        res_true = clean_for_json(True)
        assert res_true is True
        assert isinstance(res_true, bool)

        # 6. clean_for_json(False) remains Boolean False
        res_false = clean_for_json(False)
        assert res_false is False
        assert isinstance(res_false, bool)

        # 7. clean_for_json(None) remains None
        assert clean_for_json(None) is None

        # 8. Nested dictionaries and lists preserve integer values
        nested_input = {
            "id": 42,
            "scores": [10, -5, 100],
            "meta": {
                "active": True,
                "verified": False,
                "count": 99,
                "ratio": 0.85
            }
        }
        nested_output = clean_for_json(nested_input)
        assert nested_output["id"] == 42
        assert isinstance(nested_output["id"], int)
        assert not isinstance(nested_output["id"], bool)

        assert nested_output["scores"] == [10, -5, 100]
        assert all(isinstance(x, int) and not isinstance(x, bool) for x in nested_output["scores"])

        assert nested_output["meta"]["active"] is True
        assert isinstance(nested_output["meta"]["active"], bool)

        assert nested_output["meta"]["verified"] is False
        assert isinstance(nested_output["meta"]["verified"], bool)

        assert nested_output["meta"]["count"] == 99
        assert isinstance(nested_output["meta"]["count"], int)
        assert not isinstance(nested_output["meta"]["count"], bool)

        assert nested_output["meta"]["ratio"] == 0.85
        assert isinstance(nested_output["meta"]["ratio"], float)

        # 10. The resulting preview / structure can be serialized with json.dumps()
        dumped = json.dumps(nested_output)
        loaded = json.loads(dumped)
        assert loaded == nested_input

    # -------------------------------------------------------------------------
    # 2. Minimal Datasets (1-row, 1-col, 1-cell)
    # -------------------------------------------------------------------------

    def test_minimal_dataset_one_row_multiple_columns(self):
        """
        Edge Case: 1 row with multiple columns (numeric and categorical).
        For 1-row datasets, standard deviation is undefined (NaN -> None),
        min == max == mean == median, unique == 1, duplicate_rows == 0.
        """
        csv_path = self._create_temp_csv(
            "age,score,city,active\n"
            "25,98.5,Boston,True\n"
        )
        profiling = profile_dataset(csv_path)

        assert profiling['row_count'] == 1
        assert profiling['column_count'] == 4
        assert profiling['duplicate_rows_count'] == 0
        assert profiling['columns'] == ['age', 'score', 'city', 'active']

        # Numeric stats for single row
        age_stats = profiling['statistics']['age']
        assert age_stats['count'] == 1.0
        assert age_stats['min'] == 25.0
        assert age_stats['max'] == 25.0
        assert age_stats['mean'] == 25.0
        assert age_stats['median'] == 25.0
        assert age_stats['std'] is None  # Sample std for N=1 is NaN -> sanitized to None

        score_stats = profiling['statistics']['score']
        assert score_stats['min'] == 98.5
        assert score_stats['max'] == 98.5
        assert score_stats['mean'] == 98.5
        assert score_stats['std'] is None

        # Categorical stats for single row
        city_stats = profiling['statistics']['city']
        assert city_stats['type'] == 'categorical'
        assert city_stats['count'] == 1
        assert city_stats['unique'] == 1
        assert city_stats['top'] == 'Boston'
        assert city_stats['freq'] == 1

        # Preview structures
        assert len(profiling['preview']) == 1
        assert profiling['preview'][0]['city'] == 'Boston'
        assert len(profiling['preview_table_rows']) == 1

        # JSON serializable
        assert json.loads(json.dumps(profiling)) is not None

    def test_minimal_dataset_multiple_rows_one_numeric_column(self):
        """
        Edge Case: Multiple rows with exactly one numeric column.
        """
        csv_path = self._create_temp_csv(
            "score\n"
            "10\n"
            "20\n"
            "30\n"
            "40\n"
            "50\n"
        )
        profiling = profile_dataset(csv_path)

        assert profiling['row_count'] == 5
        assert profiling['column_count'] == 1
        assert profiling['columns'] == ['score']
        assert profiling['duplicate_rows_count'] == 0

        score_stats = profiling['statistics']['score']
        assert score_stats['type'] == 'numeric'
        assert score_stats['count'] == 5.0
        assert score_stats['min'] == 10.0
        assert score_stats['max'] == 50.0
        assert score_stats['mean'] == 30.0
        assert score_stats['median'] == 30.0
        assert score_stats['std'] == 15.8114
        assert score_stats['q25'] == 20.0
        assert score_stats['q75'] == 40.0

    def test_minimal_dataset_multiple_rows_one_categorical_column(self):
        """
        Edge Case: Multiple rows with exactly one categorical column.
        """
        csv_path = self._create_temp_csv(
            "status\n"
            "pending\n"
            "approved\n"
            "pending\n"
            "rejected\n"
        )
        profiling = profile_dataset(csv_path)

        assert profiling['row_count'] == 4
        assert profiling['column_count'] == 1
        assert profiling['columns'] == ['status']
        assert profiling['duplicate_rows_count'] == 1  # 2nd 'pending' is duplicate

        status_stats = profiling['statistics']['status']
        assert status_stats['type'] == 'categorical'
        assert status_stats['count'] == 4
        assert status_stats['unique'] == 3
        assert status_stats['top'] == 'pending'
        assert status_stats['freq'] == 2

    def test_minimal_dataset_single_cell_one_row_one_column(self):
        """
        Boundary Case: 1 row by 1 column (single-cell dataset).
        """
        csv_path = self._create_temp_csv("id\n42\n")
        profiling = profile_dataset(csv_path)

        assert profiling['row_count'] == 1
        assert profiling['column_count'] == 1
        assert profiling['columns'] == ['id']
        assert profiling['duplicate_rows_count'] == 0
        assert profiling['missing_values']['total_missing'] == 0

        id_stats = profiling['statistics']['id']
        assert id_stats['count'] == 1.0
        assert id_stats['min'] == 42.0
        assert id_stats['max'] == 42.0
        assert id_stats['mean'] == 42.0
        assert id_stats['std'] is None

        assert len(profiling['preview']) == 1
        assert profiling['preview'][0] == {'id': 42}
        assert isinstance(profiling['preview'][0]['id'], int)
        assert not isinstance(profiling['preview'][0]['id'], bool)
        assert profiling['preview_table_rows'] == [[42]]
        assert isinstance(profiling['preview_table_rows'][0][0], int)
        assert not isinstance(profiling['preview_table_rows'][0][0], bool)

    # -------------------------------------------------------------------------
    # 3. Missing Values Edge Cases
    # -------------------------------------------------------------------------

    def test_missing_values_single_column_partial(self):
        """
        Verify missing value detection in a single column with partial missing entries.
        """
        csv_path = self._create_temp_csv(
            "a,b\n"
            "1,10\n"
            "2,\n"
            "3,30\n"
        )
        profiling = profile_dataset(csv_path)

        assert profiling['missing_values']['total_missing'] == 1
        assert profiling['missing_values']['by_column']['b']['count'] == 1
        assert profiling['missing_values']['by_column']['b']['percentage'] == 33.33
        assert profiling['missing_values']['by_column']['a']['count'] == 0
        assert profiling['missing_values']['by_column']['a']['percentage'] == 0.0

        b_profile = [p for p in profiling['column_profiles'] if p['name'] == 'b'][0]
        assert b_profile['missing_count'] == 1
        assert b_profile['missing_percentage'] == 33.33

    def test_missing_values_multiple_columns(self):
        """
        Verify missing values across multiple distinct columns.
        """
        csv_path = self._create_temp_csv(
            "x,y,z\n"
            ",2,3\n"
            "1,,3\n"
            "1,2,\n"
        )
        profiling = profile_dataset(csv_path)

        assert profiling['missing_values']['total_missing'] == 3
        for col in ['x', 'y', 'z']:
            assert profiling['missing_values']['by_column'][col]['count'] == 1
            assert profiling['missing_values']['by_column'][col]['percentage'] == 33.33

    def test_missing_values_100_percent_missing_numeric_column(self):
        """
        Edge Case: Numeric column where 100% of the entries are missing (all NaN).
        Descriptive statistics should return count 0 and None for mean, std, min, etc.
        """
        csv_path = self._create_temp_csv(
            "valid,empty_col\n"
            "10,\n"
            "20,\n"
            "30,\n"
        )
        profiling = profile_dataset(csv_path)

        assert profiling['missing_values']['by_column']['empty_col']['count'] == 3
        assert profiling['missing_values']['by_column']['empty_col']['percentage'] == 100.0

        empty_stats = profiling['statistics']['empty_col']
        assert empty_stats['count'] == 0.0
        assert empty_stats['mean'] is None
        assert empty_stats['std'] is None
        assert empty_stats['min'] is None
        assert empty_stats['max'] is None
        assert empty_stats['median'] is None

    def test_missing_values_100_percent_missing_categorical_column(self):
        """
        Edge Case: Categorical column where all values are missing (all None/NaN).
        Categorical statistics should return count 0, unique 0, top None, freq 0.
        """
        dummy_path = self._create_temp_csv("cat,id\na,1\n")
        df_mock = pd.DataFrame({
            'cat': pd.Series([None, None, None], dtype='object'),
            'id': [1, 2, 3]
        })

        with patch('pandas.read_csv', return_value=df_mock):
            profiling = profile_dataset(dummy_path)

        cat_stats = profiling['statistics']['cat']
        assert cat_stats['type'] == 'categorical'
        assert cat_stats['count'] == 0
        assert cat_stats['unique'] == 0
        assert cat_stats['top'] is None
        assert cat_stats['freq'] == 0

        assert profiling['missing_values']['by_column']['cat']['count'] == 3
        assert profiling['missing_values']['by_column']['cat']['percentage'] == 100.0

    # -------------------------------------------------------------------------
    # 4. Duplicate Rows Edge Cases
    # -------------------------------------------------------------------------

    def test_duplicate_rows_zero_duplicates(self):
        """
        Verify duplicate row count is 0 when all rows are unique.
        """
        csv_path = self._create_temp_csv(
            "a,b\n"
            "1,x\n"
            "2,y\n"
            "3,z\n"
            "4,w\n"
        )
        profiling = profile_dataset(csv_path)
        assert profiling['row_count'] == 4
        assert profiling['duplicate_rows_count'] == 0

    def test_duplicate_rows_partial_duplicates(self):
        """
        Verify duplicate row detection when multiple duplicate rows exist.
        """
        csv_path = self._create_temp_csv(
            "a,b\n"
            "1,x\n"
            "2,y\n"
            "1,x\n"  # Duplicate 1
            "3,z\n"
            "2,y\n"  # Duplicate 2
        )
        profiling = profile_dataset(csv_path)
        assert profiling['row_count'] == 5
        assert profiling['duplicate_rows_count'] == 2

    def test_duplicate_rows_100_percent_identical_rows(self):
        """
        Edge Case: 100% duplicate dataset where all rows are completely identical.
        Duplicate rows count should be N - 1.
        """
        csv_path = self._create_temp_csv(
            "a,b,c\n"
            "1,foo,bar\n"
            "1,foo,bar\n"
            "1,foo,bar\n"
            "1,foo,bar\n"
            "1,foo,bar\n"
        )
        profiling = profile_dataset(csv_path)
        assert profiling['row_count'] == 5
        assert profiling['duplicate_rows_count'] == 4

    # -------------------------------------------------------------------------
    # 5. Numerical Statistics Edge Cases
    # -------------------------------------------------------------------------

    def test_numeric_profiling_constant_column_zero_variance(self):
        """
        Edge Case: Numerical column with constant values (zero variance).
        Standard deviation should be exactly 0.0, and min == max == mean == median.
        """
        csv_path = self._create_temp_csv(
            "constant\n"
            "7\n"
            "7\n"
            "7\n"
            "7\n"
        )
        profiling = profile_dataset(csv_path)

        const_stats = profiling['statistics']['constant']
        assert const_stats['count'] == 4.0
        assert const_stats['min'] == 7.0
        assert const_stats['max'] == 7.0
        assert const_stats['mean'] == 7.0
        assert const_stats['median'] == 7.0
        assert const_stats['std'] == 0.0

    def test_numeric_profiling_negative_numbers(self):
        """
        Verify statistics correctly handle all-negative numerical values.
        """
        csv_path = self._create_temp_csv(
            "val\n"
            "-100\n"
            "-50\n"
            "-10\n"
        )
        profiling = profile_dataset(csv_path)

        val_stats = profiling['statistics']['val']
        assert val_stats['min'] == -100.0
        assert val_stats['max'] == -10.0
        assert val_stats['mean'] == -53.3333
        assert val_stats['median'] == -50.0

    def test_numeric_profiling_high_precision_floating_point(self):
        """
        Verify clean_for_json rounds high-precision floats to 4 decimal places.
        """
        csv_path = self._create_temp_csv(
            "val\n"
            "0.1234567\n"
            "0.9876543\n"
        )
        profiling = profile_dataset(csv_path)

        assert profiling['preview'][0]['val'] == 0.1235
        assert profiling['preview'][1]['val'] == 0.9877

        val_stats = profiling['statistics']['val']
        assert val_stats['min'] == 0.1235
        assert val_stats['max'] == 0.9877
        assert val_stats['mean'] == 0.5556

    def test_numeric_profiling_large_numbers(self):
        """
        Verify statistics calculation for very large numbers (billions) without overflow.
        """
        csv_path = self._create_temp_csv(
            "big\n"
            "1000000000\n"
            "2000000000\n"
            "3000000000\n"
        )
        profiling = profile_dataset(csv_path)

        big_stats = profiling['statistics']['big']
        assert big_stats['min'] == 1000000000.0
        assert big_stats['max'] == 3000000000.0
        assert big_stats['mean'] == 2000000000.0
        assert big_stats['median'] == 2000000000.0
        assert big_stats['std'] == 1000000000.0

    # -------------------------------------------------------------------------
    # 6. Categorical Statistics Edge Cases
    # -------------------------------------------------------------------------

    def test_categorical_profiling_single_category(self):
        """
        Edge Case: Categorical column where all rows contain the same single category.
        """
        csv_path = self._create_temp_csv(
            "cat\n"
            "alpha\n"
            "alpha\n"
            "alpha\n"
        )
        profiling = profile_dataset(csv_path)

        cat_stats = profiling['statistics']['cat']
        assert cat_stats['count'] == 3
        assert cat_stats['unique'] == 1
        assert cat_stats['top'] == 'alpha'
        assert cat_stats['freq'] == 3

    def test_categorical_profiling_all_unique_categories(self):
        """
        Edge Case: Categorical column where every row is a distinct unique value.
        """
        csv_path = self._create_temp_csv(
            "cat\n"
            "red\n"
            "green\n"
            "blue\n"
            "yellow\n"
        )
        profiling = profile_dataset(csv_path)

        cat_stats = profiling['statistics']['cat']
        assert cat_stats['count'] == 4
        assert cat_stats['unique'] == 4
        assert cat_stats['freq'] == 1

    def test_categorical_profiling_mode_and_frequencies(self):
        """
        Verify mode ('top') and highest frequency ('freq') for categorical column.
        """
        csv_path = self._create_temp_csv(
            "label\n"
            "cat\n"
            "dog\n"
            "cat\n"
            "bird\n"
            "cat\n"
            "dog\n"
        )
        profiling = profile_dataset(csv_path)

        label_stats = profiling['statistics']['label']
        assert label_stats['count'] == 6
        assert label_stats['unique'] == 3
        assert label_stats['top'] == 'cat'
        assert label_stats['freq'] == 3

    # -------------------------------------------------------------------------
    # 7. Special Numeric Values (Inf, -Inf, NaN) & JSON Serializability
    # -------------------------------------------------------------------------

    def test_special_values_inf_and_nan_json_serializability(self):
        """
        Edge Case: CSV containing inf, -inf, nan literal values.
        Verify they are sanitized to None and the resulting dict is valid JSON.
        """
        csv_path = self._create_temp_csv(
            "val\n"
            "1.5\n"
            "inf\n"
            "-inf\n"
            "nan\n"
            "3.5\n"
        )
        profiling = profile_dataset(csv_path)

        # Preview rows: inf, -inf, nan must be sanitized to None
        assert profiling['preview'][0]['val'] == 1.5
        assert profiling['preview'][1]['val'] is None
        assert profiling['preview'][2]['val'] is None
        assert profiling['preview'][3]['val'] is None
        assert profiling['preview'][4]['val'] == 3.5

        # Entire dict must be JSON-dumpable without ValueError: Out of range float values
        dumped = json.dumps(profiling)
        loaded = json.loads(dumped)
        assert loaded['preview'][1]['val'] is None

    # -------------------------------------------------------------------------
    # 8. Preview Truncation & Preview Sizing
    # -------------------------------------------------------------------------

    def test_preview_truncation_default_limit(self):
        """
        Verify preview truncates to 10 rows by default when dataset has 25 rows.
        """
        lines = ["id,val"] + [f"{i},{i*10}" for i in range(25)]
        csv_path = self._create_temp_csv("\n".join(lines) + "\n")

        profiling = profile_dataset(csv_path)

        assert profiling['row_count'] == 25
        assert len(profiling['preview']) == 10
        assert len(profiling['preview_table_rows']) == 10
        assert profiling['preview'][0] == {'id': 0, 'val': 0}
        assert isinstance(profiling['preview'][0]['id'], int)
        assert not isinstance(profiling['preview'][0]['id'], bool)
        assert profiling['preview'][9] == {'id': 9, 'val': 90}
        assert isinstance(profiling['preview'][9]['val'], int)

    def test_preview_truncation_custom_limit(self):
        """
        Verify preview honors custom preview_rows limit.
        """
        lines = ["id,val"] + [f"{i},{i*10}" for i in range(25)]
        csv_path = self._create_temp_csv("\n".join(lines) + "\n")

        profiling = profile_dataset(csv_path, preview_rows=5)

        assert profiling['row_count'] == 25
        assert len(profiling['preview']) == 5
        assert len(profiling['preview_table_rows']) == 5
        assert profiling['preview'][4] == {'id': 4, 'val': 40}
        assert isinstance(profiling['preview'][4]['id'], int)
        assert isinstance(profiling['preview'][4]['val'], int)

    def test_preview_truncation_smaller_than_limit(self):
        """
        Verify preview returns all rows when dataset size is smaller than preview_rows.
        """
        csv_path = self._create_temp_csv(
            "id,val\n"
            "1,10\n"
            "2,20\n"
            "3,30\n"
        )
        profiling = profile_dataset(csv_path, preview_rows=10)

        assert profiling['row_count'] == 3
        assert len(profiling['preview']) == 3
        assert len(profiling['preview_table_rows']) == 3

    # -------------------------------------------------------------------------
    # 9. API & Web UI Integration with Edge Cases
    # -------------------------------------------------------------------------

    def test_api_preview_with_one_row_dataset(self):
        """
        Verify GET dataset-preview-api handles 1-row dataset returning HTTP 200 and valid JSON.
        """
        csv_content = b"feature_a,feature_b\n42,single_entry\n"
        ds = self._create_dataset("api_one_row.csv", csv_content)

        self.client.login(username='edge_user', password='password123')
        url = reverse('dataset-preview-api', kwargs={'pk': ds.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert data['profiling']['row_count'] == 1
        assert data['profiling']['statistics']['feature_a']['std'] is None
        assert data['profiling']['statistics']['feature_b']['top'] == 'single_entry'

    def test_api_preview_with_100_percent_duplicate_dataset(self):
        """
        Verify GET dataset-preview-api handles 100% duplicate rows dataset returning HTTP 200.
        """
        csv_content = b"a,b\n1,x\n1,x\n1,x\n1,x\n1,x\n"
        ds = self._create_dataset("api_all_dup.csv", csv_content)

        self.client.login(username='edge_user', password='password123')
        url = reverse('dataset-preview-api', kwargs={'pk': ds.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert data['profiling']['row_count'] == 5
        assert data['profiling']['duplicate_rows_count'] == 4

    def test_api_preview_with_all_missing_numeric_column(self):
        """
        Verify GET dataset-preview-api handles dataset with 100% missing column returning HTTP 200.
        """
        csv_content = b"id,empty_score\n1,\n2,\n3,\n"
        ds = self._create_dataset("api_all_missing.csv", csv_content)

        self.client.login(username='edge_user', password='password123')
        url = reverse('dataset-preview-api', kwargs={'pk': ds.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'
        assert data['profiling']['missing_values']['by_column']['empty_score']['percentage'] == 100.0
        assert data['profiling']['statistics']['empty_score']['mean'] is None

    def test_web_preview_with_one_row_dataset(self):
        """
        Verify GET dataset-preview-web renders successfully without template error for 1-row dataset.
        """
        csv_content = b"col1,col2\n99,single\n"
        ds = self._create_dataset("web_one_row.csv", csv_content)

        self.client.login(username='edge_user', password='password123')
        url = reverse('dataset-preview-web', kwargs={'pk': ds.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert b"web_one_row.csv" in response.content
        assert b"single" in response.content

    def test_web_preview_with_missing_values(self):
        """
        Verify GET dataset-preview-web renders successfully for dataset with missing values.
        """
        csv_content = b"name,val\nAlice,10\nBob,\nCharlie,30\n"
        ds = self._create_dataset("web_missing.csv", csv_content)

        self.client.login(username='edge_user', password='password123')
        url = reverse('dataset-preview-web', kwargs={'pk': ds.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert b"web_missing.csv" in response.content
        assert b"Alice" in response.content
        assert b"Charlie" in response.content

    def test_profile_dataset_preview_integer_columns_numeric_types(self):
        """
        Regression Test: Verify that dataset profiling preserves integer types as
        numeric values (not strings) in preview records and table rows, and that
        the entire profiling dictionary serializes cleanly with json.dumps().
        """
        csv_path = self._create_temp_csv(
            "id,score,count,active\n"
            "1,95,100,True\n"
            "2,88,200,False\n"
        )
        profiling = profile_dataset(csv_path)

        # 9. A dataset preview containing integer columns returns numeric JSON values, not strings
        first_row = profiling['preview'][0]
        assert first_row['id'] == 1
        assert isinstance(first_row['id'], int)
        assert not isinstance(first_row['id'], bool)
        assert not isinstance(first_row['id'], str)

        assert first_row['score'] == 95
        assert isinstance(first_row['score'], int)
        assert not isinstance(first_row['score'], bool)

        assert first_row['count'] == 100
        assert isinstance(first_row['count'], int)
        assert not isinstance(first_row['count'], bool)

        assert first_row['active'] is True
        assert isinstance(first_row['active'], bool)

        # Table rows verification
        assert profiling['preview_table_rows'][0] == [1, 95, 100, True]
        assert isinstance(profiling['preview_table_rows'][0][0], int)
        assert not isinstance(profiling['preview_table_rows'][0][0], bool)

        # 10. The resulting preview can be serialized with json.dumps()
        dumped = json.dumps(profiling)
        loaded = json.loads(dumped)
        assert loaded['preview'][0]['id'] == 1
        assert isinstance(loaded['preview'][0]['id'], int)

    def test_api_preview_with_integer_columns_numeric_json_response(self):
        """
        Regression Test: Verify that GET dataset-preview-api returns JSON where integer
        columns are represented as numeric JSON integers, not stringified integers.
        """
        csv_content = b"student_id,grade,credits\n101,95,4\n102,88,3\n"
        ds = self._create_dataset("students.csv", csv_content)

        self.client.login(username='edge_user', password='password123')
        url = reverse('dataset-preview-api', kwargs={'pk': ds.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'success'

        first_preview = data['profiling']['preview'][0]
        assert first_preview['student_id'] == 101
        assert isinstance(first_preview['student_id'], int)
        assert not isinstance(first_preview['student_id'], str)
        assert not isinstance(first_preview['student_id'], bool)

        assert first_preview['grade'] == 95
        assert isinstance(first_preview['grade'], int)

        assert first_preview['credits'] == 4
        assert isinstance(first_preview['credits'], int)

