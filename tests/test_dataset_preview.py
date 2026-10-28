import os
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from rest_framework import status
from datasets.models import Dataset
from datasets.services import profile_dataset
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

