import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework import status


class TestAuthenticationAndSecurity(TestCase):
    """
    Test suite for User Authentication and Session Management corresponding to:
    - SRS: ML-EVAL-F-001, ML-EVAL-F-002, ML-EVAL-F-003, ML-EVAL-SR-002, ML-EVAL-SR-003
    - STP: TC-AUTH-01, TC-AUTH-02, TC-AUTH-03, TC-SEC-01, TC-SEC-03
    """

    def setUp(self):
        self.client = Client()
        self.reg_url = reverse('auth-register-api')
        self.login_url = reverse('auth-login-api')
        self.logout_url = reverse('auth-logout-api')
        self.me_url = reverse('auth-me-api')

    def test_tc_auth_01_user_registration_api_success(self):
        """
        TC-AUTH-01: Valid user registration creates account and authenticates session.
        """
        payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!'
        }
        res = self.client.post(self.reg_url, payload, content_type='application/json')
        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()
        assert data['status'] == 'success'
        assert data['user']['username'] == 'newuser'

        user = User.objects.get(username='newuser')
        assert user.email == 'newuser@example.com'

    def test_tc_auth_01_registration_duplicate_username_rejected(self):
        """
        TC-AUTH-01: Duplicate username is rejected with validation error.
        """
        User.objects.create_user(username='existinguser', password='password123')
        payload = {
            'username': 'existinguser',
            'password': 'password123',
            'password_confirm': 'password123'
        }
        res = self.client.post(self.reg_url, payload, content_type='application/json')
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already exists' in str(res.json()['errors'])

    def test_tc_auth_01_registration_password_mismatch_rejected(self):
        """
        TC-AUTH-01: Mismatched password and password_confirm is rejected.
        """
        payload = {
            'username': 'mismatchuser',
            'password': 'password123',
            'password_confirm': 'differentpassword'
        }
        res = self.client.post(self.reg_url, payload, content_type='application/json')
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Passwords do not match' in str(res.json()['errors'])

    def test_tc_auth_02_user_login_api_success_and_invalid(self):
        """
        TC-AUTH-02: Valid credentials authenticate; invalid credentials produce 400 error.
        """
        User.objects.create_user(username='validuser', password='correctpassword')

        # Invalid login
        bad_res = self.client.post(self.login_url, {'username': 'validuser', 'password': 'wrongpassword'}, content_type='application/json')
        assert bad_res.status_code == status.HTTP_400_BAD_REQUEST

        # Valid login
        good_res = self.client.post(self.login_url, {'username': 'validuser', 'password': 'correctpassword'}, content_type='application/json')
        assert good_res.status_code == status.HTTP_200_OK
        assert good_res.json()['status'] == 'success'

        # Verify active session via /api/auth/me/
        me_res = self.client.get(self.me_url)
        assert me_res.status_code == status.HTTP_200_OK
        assert me_res.json()['authenticated'] is True
        assert me_res.json()['user']['username'] == 'validuser'

    def test_tc_auth_03_user_logout_api(self):
        """
        TC-AUTH-03: Logout terminates session; subsequent requests reflect unauthenticated state.
        """
        User.objects.create_user(username='logoutuser', password='password123')
        self.client.login(username='logoutuser', password='password123')

        logout_res = self.client.post(self.logout_url)
        assert logout_res.status_code == status.HTTP_200_OK

        me_res = self.client.get(self.me_url)
        assert me_res.json()['authenticated'] is False
        assert me_res.json()['user'] is None

    def test_tc_sec_03_password_hashing(self):
        """
        TC-SEC-03: Passwords must be securely hashed and never stored in plaintext.
        """
        raw_pw = "SuperSecret123!"
        user = User.objects.create_user(username='secureuser', password=raw_pw)

        # Ensure raw password string does not appear in database hash
        assert raw_pw not in user.password
        assert user.password.startswith('pbkdf2_') or user.password.startswith('argon2')
        assert user.check_password(raw_pw) is True

    def test_web_ui_auth_views(self):
        """
        Test web UI views for register, login, and logout.
        """
        reg_web_url = reverse('register-web')
        login_web_url = reverse('login-web')
        logout_web_url = reverse('logout-web')

        # 1. Register Web Form
        reg_get = self.client.get(reg_web_url)
        assert reg_get.status_code == status.HTTP_200_OK
        assert b"Create Account" in reg_get.content

        reg_post = self.client.post(reg_web_url, {
            'username': 'webuser',
            'email': 'web@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        }, follow=True)
        assert reg_post.status_code == status.HTTP_200_OK
        assert b"webuser" in reg_post.content

        # 2. Logout Web Form
        logout_res = self.client.get(logout_web_url, follow=True)
        assert logout_res.status_code == status.HTTP_200_OK
        assert b"logged out successfully" in logout_res.content

        # 3. Login Web Form
        login_post = self.client.post(login_web_url, {
            'username': 'webuser',
            'password': 'password123'
        }, follow=True)
        assert login_post.status_code == status.HTTP_200_OK
        assert b"Welcome back, webuser" in login_post.content

