import os
import io
import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from rest_framework import status
from datasets.models import Dataset
from datasets.validators import sanitize_filename, validate_csv_file
from rest_framework.exceptions import ValidationError


class TestDatasetUploadValidation(TestCase):
    """
    Test suite for Dataset Upload & Validation corresponding to:
    - SRS: ML-EVAL-F-010, ML-EVAL-F-011, ML-EVAL-SR-003
    - STP: TC-DATA-01, TC-DATA-02, TC-SEC-04
    - Issue #1: Implement dataset upload and validation
    """

    def setUp(self):
        self.client = Client()
        self.api_url = reverse('dataset-upload-api')
        self.web_url = reverse('dataset-web-upload')

    def test_tc_data_01_valid_csv_upload_api(self):
        """
        TC-DATA-01: Verify that a valid CSV file is accepted, validated, and persisted.
        """
        csv_content = b"feature1,feature2,feature3,target\n1.0,2.0,3.0,0\n4.0,5.0,6.0,1\n7.0,8.0,9.0,0\n"
        uploaded_file = SimpleUploadedFile("sample_dataset.csv", csv_content, content_type="text/csv")

        response = self.client.post(self.api_url, {'file': uploaded_file})

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['status'] == 'success'
        assert 'dataset' in data
        assert data['dataset']['filename'] == 'sample_dataset.csv'
        assert data['dataset']['row_count'] == 3
        assert data['dataset']['column_count'] == 4
        assert data['dataset']['columns'] == ['feature1', 'feature2', 'feature3', 'target']

        # Verify database persistence
        dataset_id = data['dataset']['id']
        ds = Dataset.objects.get(id=dataset_id)
        assert ds.row_count == 3
        assert ds.column_count == 4
        assert os.path.exists(ds.file.path)

    def test_tc_data_01_authenticated_user_upload(self):
        """
        TC-DATA-01 / TC-AUTH: Verify that authenticated user's dataset is associated with the user account.
        """
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='testanalyst', password='password123')
        self.client.login(username='testanalyst', password='password123')

        csv_content = b"a,b,c\n1,2,3\n4,5,6\n"
        uploaded_file = SimpleUploadedFile("auth_test.csv", csv_content, content_type="text/csv")
        response = self.client.post(self.api_url, {'file': uploaded_file})

        assert response.status_code == status.HTTP_201_CREATED
        ds = Dataset.objects.get(filename='auth_test.csv')
        assert ds.user == user

    def test_tc_data_02_missing_file_payload(self):
        """
        TC-DATA-02: Missing file payload returns 400 Bad Request.
        """
        response = self.client.post(self.api_url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['status'] == 'error'
        assert 'No file was provided' in data['error']

    def test_tc_data_02_invalid_file_extension(self):
        """
        TC-DATA-02: Non-CSV files (.txt, .exe, .json) are rejected.
        """
        text_file = SimpleUploadedFile("dataset.txt", b"col1,col2\n1,2", content_type="text/plain")
        response = self.client.post(self.api_url, {'file': text_file})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['status'] == 'error'
        assert 'Only CSV files' in data['error']

    def test_tc_data_02_empty_file(self):
        """
        TC-DATA-02: Upload of a completely empty file is rejected.
        """
        empty_file = SimpleUploadedFile("empty.csv", b"", content_type="text/csv")
        response = self.client.post(self.api_url, {'file': empty_file})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['status'] == 'error'
        assert 'empty' in data['error'].lower()

    def test_tc_data_02_whitespace_only_file(self):
        """
        TC-DATA-02: Upload of whitespace-only content is rejected.
        """
        ws_file = SimpleUploadedFile("whitespace.csv", b"   \n\n\t  \n", content_type="text/csv")
        response = self.client.post(self.api_url, {'file': ws_file})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['status'] == 'error'
        assert 'empty' in data['error'].lower()

    def test_tc_data_02_header_only_no_data_rows(self):
        """
        TC-DATA-02: CSV with header columns but zero data rows is rejected.
        """
        header_only = SimpleUploadedFile("no_data.csv", b"col1,col2,col3\n", content_type="text/csv")
        response = self.client.post(self.api_url, {'file': header_only})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['status'] == 'error'
        assert 'at least one data row' in data['error']

    def test_tc_data_02_malformed_csv(self):
        """
        TC-DATA-02: Malformed CSV with mismatched or broken token structure is rejected.
        """
        corrupted_content = b'col1,col2\n"unclosed quote line,2\n3,4\n'
        corrupted_file = SimpleUploadedFile("corrupted.csv", corrupted_content, content_type="text/csv")
        response = self.client.post(self.api_url, {'file': corrupted_file})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data['status'] == 'error'

    def test_tc_sec_04_oversized_file_rejected(self):
        """
        TC-SEC-04: File exceeding maximum permitted size (10 MB) is rejected.
        """
        oversized_file = SimpleUploadedFile(
            "large.csv",
            b"a,b\n1,2",
            content_type="text/csv"
        )
        oversized_file.size = 15 * 1024 * 1024  # Simulated 15 MB

        with pytest.raises(ValidationError) as excinfo:
            validate_csv_file(oversized_file)
        assert 'exceeds maximum allowed limit' in str(excinfo.value)

    def test_tc_sec_04_filename_sanitization(self):
        """
        TC-SEC-04: Malicious path traversal sequences in filenames are sanitized.
        """
        dangerous_name = "../../etc/passwd..///dataset.csv"
        sanitized = sanitize_filename(dangerous_name)
        assert '/' not in sanitized
        assert '\\' not in sanitized
        assert '..' not in sanitized
        assert sanitized.endswith('.csv')

    def test_dataset_str_representation_and_cleanup(self):
        """
        Verify Dataset string representation and that file is removed on deletion.
        """
        csv_content = b"a,b\n1,2\n3,4\n"
        f = SimpleUploadedFile("cleanup_test.csv", csv_content, content_type="text/csv")
        ds = Dataset.objects.create(
            file=f,
            filename="cleanup_test.csv",
            file_size=len(csv_content),
            row_count=2,
            column_count=2,
            columns=["a", "b"]
        )
        assert str(ds) == "cleanup_test.csv (2 rows, 2 columns)"
        file_path = ds.file.path
        assert os.path.exists(file_path)

        # Deletion cleans up file
        ds.delete()
        assert not os.path.exists(file_path)

    def test_web_ui_upload_success_and_error(self):
        """
        Verify web UI upload flow renders forms, shows success on valid upload, and errors on invalid file.
        """
        # GET request
        get_res = self.client.get(self.web_url)
        assert get_res.status_code == status.HTTP_200_OK
        assert b"Dataset Upload & Validation" in get_res.content

        # POST valid file
        valid_file = SimpleUploadedFile("web_valid.csv", b"x,y\n10,20\n30,40\n", content_type="text/csv")
        post_res = self.client.post(self.web_url, {'file': valid_file}, follow=True)
        assert post_res.status_code == status.HTTP_200_OK
        assert b"uploaded successfully" in post_res.content
        assert b"web_valid.csv" in post_res.content

        # POST invalid file
        invalid_file = SimpleUploadedFile("web_bad.txt", b"invalid", content_type="text/plain")
        bad_res = self.client.post(self.web_url, {'file': invalid_file}, follow=True)
        assert bad_res.status_code == status.HTTP_200_OK
        assert b"Validation error" in bad_res.content
