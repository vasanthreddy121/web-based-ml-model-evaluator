import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from rest_framework import status
from datasets.models import Dataset
from experiments.models import Experiment


class TestDashboardLayoutIssue7(TestCase):
    """
    Tests for GitHub Issue #7: Improve dashboard layout and responsive spacing.
    Verifies:
    - Dashboard hero header and workflow stage tracker
    - Dashboard metrics overview cards
    - Responsive card layout and table wrapper
    - Clear visual hierarchy and typography
    """

    def setUp(self):
        self.client = Client()
        self.url = reverse('dataset-home')

    def test_dashboard_hero_and_workflow_stages_rendered(self):
        """Verify dashboard banner with title, subtitle, and 4 workflow progress stages."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

        content = response.content
        assert b"ML Experimentation Dashboard" in content
        assert b"Upload &amp; Validate" in content or b"Upload & Validate" in content
        assert b"Profile &amp; Preprocess" in content or b"Profile & Preprocess" in content
        assert b"Train &amp; Evaluate" in content or b"Train & Evaluate" in content
        assert b"Compare Benchmarks" in content

    def test_dashboard_metrics_overview_rendered(self):
        """Verify dashboard summary metrics row is displayed."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

        content = response.content
        assert b"Catalog Datasets" in content
        assert b"Supported Algorithms" in content
        assert b"Upload Size Limit" in content
        assert b"10 MB" in content

    def test_dashboard_table_responsive_container(self):
        """Verify uploaded datasets table is wrapped in an accessible responsive container."""
        # Create a dataset so table renders
        f = SimpleUploadedFile("dash_test.csv", b"a,b\n1,2\n", content_type="text/csv")
        ds = Dataset.objects.create(
            file=f,
            filename="dash_test.csv",
            file_size=8,
            row_count=1,
            column_count=2,
            columns=["a", "b"]
        )

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert b'class="table-container"' in response.content
        assert b'role="region"' in response.content
        assert b'aria-label="Uploaded datasets list"' in response.content

        # Cleanup
        ds.delete()


class TestEmptyStatesIssue8(TestCase):
    """
    Tests for GitHub Issue #8: Add clear empty states to dashboard and dataset lists.
    Verifies:
    - Empty state displayed when no datasets are uploaded
    - Empty state disappears when datasets exist
    - Empty state displayed on experiment history when no experiments exist
    - Empty state disappears when experiments exist
    - Empty state includes explanatory text and actionable next step
    """

    def setUp(self):
        self.client = Client()

    def test_dashboard_empty_state_when_no_datasets(self):
        """When 0 datasets exist, clear empty state component is shown with call-to-action."""
        Dataset.objects.all().delete()

        response = self.client.get(reverse('dataset-home'))
        assert response.status_code == status.HTTP_200_OK
        content = response.content

        assert b'class="empty-state"' in content
        assert b"No datasets uploaded yet" in content
        assert b"Choose CSV File Above" in content or b"Choose a CSV file" in content

    def test_dashboard_empty_state_disappears_when_dataset_exists(self):
        """When datasets are present, the empty state disappears and the table displays."""
        f = SimpleUploadedFile("not_empty.csv", b"x,y\n10,20\n", content_type="text/csv")
        ds = Dataset.objects.create(
            file=f,
            filename="not_empty.csv",
            file_size=10,
            row_count=1,
            column_count=2,
            columns=["x", "y"]
        )

        response = self.client.get(reverse('dataset-home'))
        assert response.status_code == status.HTTP_200_OK
        content = response.content

        # Table is rendered, empty state is not
        assert b"not_empty.csv" in content
        assert b'<caption class="visually-hidden">Uploaded datasets and available actions</caption>' in content
        assert b'<div class="empty-state">' not in content

        # Cleanup
        ds.delete()

    def test_experiment_history_empty_state_when_no_experiments(self):
        """When 0 experiments exist, history page displays a clear empty state with upload CTA."""
        Experiment.objects.all().delete()

        response = self.client.get(reverse('experiment-history-web'))
        assert response.status_code == status.HTTP_200_OK
        content = response.content

        assert b'class="empty-state"' in content
        assert b"No experiments found" in content
        assert b"+ Upload a Dataset to Train" in content or b"Upload a dataset" in content

    def test_experiment_history_empty_state_disappears_when_experiments_exist(self):
        """When experiments exist, the empty state is replaced by the historical runs table."""
        f = SimpleUploadedFile("exp_ds.csv", b"a,target\n1,0\n", content_type="text/csv")
        ds = Dataset.objects.create(
            file=f,
            filename="exp_ds.csv",
            file_size=15,
            row_count=1,
            column_count=2,
            columns=["a", "target"]
        )
        exp = Experiment.objects.create(
            dataset=ds,
            name="Test Experiment",
            problem_type="classification",
            model_name="logistic_regression",
            model_display_name="Logistic Regression",
            metrics={'accuracy': 0.85, 'f1_score': 0.84},
            training_time_seconds=0.12
        )

        response = self.client.get(reverse('experiment-history-web'))
        assert response.status_code == status.HTTP_200_OK
        content = response.content

        assert b"Logistic Regression" in content
        assert b'name="exp_id"' in content
        assert b'<div class="empty-state">' not in content

        # Cleanup
        exp.delete()
        ds.delete()


class TestNavigationConsistencyIssue9(TestCase):
    """
    Tests for GitHub Issue #9: Improve navigation consistency across application pages.
    Verifies:
    - Active page highlighting for Datasets, Experiments, Sign In, Register
    - Authenticated user chip and sign out button
    - Unauthenticated sign in and register buttons
    - Consistent navigation links across views
    - Breadcrumb / Back buttons on sub-pages
    """

    def setUp(self):
        self.client = Client()

    def test_active_nav_highlighting_on_datasets_home(self):
        """Verify 'Datasets' link receives active styling and aria-current='page' on home."""
        response = self.client.get('/')
        assert response.status_code == status.HTTP_200_OK
        content = response.content

        assert b'class="nav-link active"' in content
        assert b'aria-current="page"' in content
        assert b'Datasets' in content

    def test_active_nav_highlighting_on_experiments_history(self):
        """Verify 'Experiments' link receives active styling and aria-current on history page."""
        response = self.client.get(reverse('experiment-history-web'))
        assert response.status_code == status.HTTP_200_OK
        content = response.content

        assert b'class="nav-link active"' in content
        assert b'aria-current="page"' in content
        assert b'Experiments' in content

    def test_active_nav_highlighting_on_login_page(self):
        """Verify 'Sign In' link receives active styling on login page."""
        response = self.client.get(reverse('login-web'))
        assert response.status_code == status.HTTP_200_OK
        content = response.content

        assert b'aria-current="page"' in content
        assert b'Sign In' in content

    def test_authenticated_navigation_displays_user_chip_and_signout(self):
        """Verify authenticated session renders user avatar/chip and sign out button."""
        User.objects.create_user(username='navuser', password='password123')
        self.client.login(username='navuser', password='password123')

        response = self.client.get('/')
        assert response.status_code == status.HTTP_200_OK
        content = response.content

        assert b'navuser' in content
        assert b'Sign Out' in content
        assert b'Sign In' not in content

    def test_unauthenticated_navigation_displays_signin_and_register(self):
        """Verify unauthenticated user sees Sign In and Register links."""
        response = self.client.get('/')
        assert response.status_code == status.HTTP_200_OK
        content = response.content

        assert b'Sign In' in content
        assert b'Register' in content
        assert b'Sign Out' not in content

    def test_subpage_secondary_navigation_buttons(self):
        """Verify sub-pages provide consistent back navigation to catalog or profile."""
        f = SimpleUploadedFile("nav_ds.csv", b"a,b\n1,2\n", content_type="text/csv")
        ds = Dataset.objects.create(
            file=f,
            filename="nav_ds.csv",
            file_size=8,
            row_count=1,
            column_count=2,
            columns=["a", "b"]
        )

        # Preprocess page back link
        res_prep = self.client.get(reverse('dataset-preprocess-web', kwargs={'pk': ds.id}))
        assert res_prep.status_code == status.HTTP_200_OK
        assert b"View Profile" in res_prep.content

        # Train page back link
        res_train = self.client.get(reverse('experiment-train-web', kwargs={'dataset_id': ds.id}))
        assert res_train.status_code == status.HTTP_200_OK
        assert b"View Profile" in res_train.content

        # Cleanup
        ds.delete()


class TestFormLabelsAndInlineHelpIssue10(TestCase):
    """
    Tests for GitHub Issue #10: Improve form labels and inline help text.
    Verifies:
    - Meaningful visible labels associated with form inputs via 'for' and 'id'
    - Inline help text with aria-describedby linkage
    - Accurate application validation constraints (.csv, 10 MB, headers, rows)
    - Fieldset and legend structure for grouped inputs
    - Clear error indications and input requirements
    """

    def setUp(self):
        self.client = Client()

    def test_upload_form_labels_and_inline_descriptions(self):
        """Verify upload form contains associated label, file-help, and specification guides."""
        response = self.client.get(reverse('dataset-web-upload'))
        assert response.status_code == status.HTTP_200_OK
        content = response.content

        # Label associated with input
        assert b'<label for="file"' in content
        assert b'<input type="file" name="file" id="file"' in content
        assert b'aria-describedby="file-help"' in content

        # Inline help text explains real application validation rules
        assert b'id="file-help"' in content
        assert b".csv" in content
        assert b"10 MB" in content
        assert b"UTF-8" in content
        assert b"named headers and at least one data row" in content

    def test_preprocess_form_labels_and_help_text(self):
        """Verify preprocess form has explicit labels, legends, and help text."""
        f = SimpleUploadedFile("help_ds.csv", b"feat1,feat2,target\n1,2,0\n", content_type="text/csv")
        ds = Dataset.objects.create(
            file=f,
            filename="help_ds.csv",
            file_size=20,
            row_count=1,
            column_count=3,
            columns=["feat1", "feat2", "target"]
        )

        response = self.client.get(reverse('dataset-preprocess-web', kwargs={'pk': ds.id}))
        assert response.status_code == status.HTTP_200_OK
        content = response.content

        # Target variable label and help
        assert b'<label class="form-label" for="target_column">' in content
        assert b'id="target_column"' in content
        assert b'id="target-help"' in content

        # Group legends
        assert b'<legend class="form-label">Missing Value Strategy</legend>' in content
        assert b'<legend class="form-label">Categorical Encoding</legend>' in content
        assert b'<legend class="form-label">Feature Scaling</legend>' in content

        # Test size split ratio
        assert b'<label class="form-label" for="test_size">' in content
        assert b'id="test_size"' in content
        assert b'id="test-size-help"' in content

        # Duplicate handling
        assert b'<input type="checkbox" name="handle_duplicates" id="handle_duplicates"' in content
        assert b'id="dup-help"' in content

        # Cleanup
        ds.delete()

    def test_train_form_labels_and_help_text(self):
        """Verify train model form has explicit labels and inline hints."""
        f = SimpleUploadedFile("train_help_ds.csv", b"x1,x2,y\n1,2,0\n", content_type="text/csv")
        ds = Dataset.objects.create(
            file=f,
            filename="train_help_ds.csv",
            file_size=15,
            row_count=1,
            column_count=3,
            columns=["x1", "x2", "y"]
        )

        response = self.client.get(reverse('experiment-train-web', kwargs={'dataset_id': ds.id}))
        assert response.status_code == status.HTTP_200_OK
        content = response.content

        # Algorithm label & help
        assert b'<label class="form-label" for="model_name">' in content
        assert b'id="model_name"' in content
        assert b'id="model-help"' in content

        # Target column label & help
        assert b'<label class="form-label" for="target_column">' in content
        assert b'id="target_column"' in content
        assert b'id="target-help"' in content

        # Hyperparameters labels & hints
        assert b'<label class="form-label" for="max_depth"' in content
        assert b'id="max_depth"' in content
        assert b'id="depth-help"' in content

        assert b'<label class="form-label" for="n_estimators"' in content
        assert b'id="n_estimators"' in content
        assert b'id="est-help"' in content

        assert b'<label class="form-label" for="n_neighbors"' in content
        assert b'id="n_neighbors"' in content
        assert b'id="knn-help"' in content

        # Cleanup
        ds.delete()

    def test_login_and_register_form_labels_and_hints(self):
        """Verify login and register forms contain accessible labels and inline instructions."""
        # Login
        login_res = self.client.get(reverse('login-web'))
        assert login_res.status_code == status.HTTP_200_OK
        assert b'<label class="form-label" for="username">' in login_res.content
        assert b'<label class="form-label" for="password">' in login_res.content
        assert b'id="username-hint"' in login_res.content
        assert b'id="password-hint"' in login_res.content

        # Register
        reg_res = self.client.get(reverse('register-web'))
        assert reg_res.status_code == status.HTTP_200_OK
        assert b'<label class="form-label" for="username">' in reg_res.content
        assert b'<label class="form-label" for="email">' in reg_res.content
        assert b'<label class="form-label" for="password">' in reg_res.content
        assert b'<label class="form-label" for="password_confirm">' in reg_res.content
        assert b'id="reg-username-hint"' in reg_res.content
        assert b'id="reg-password-hint"' in reg_res.content
        assert b'id="reg-confirm-hint"' in reg_res.content

