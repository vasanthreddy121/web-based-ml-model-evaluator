from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    CurrentUserAPIView,
    register_web_view,
    login_web_view,
    logout_web_view,
)

urlpatterns = [
    # REST API endpoints (SRS ML-EVAL-F-001, F-002, F-003)
    path('api/auth/register/', RegisterAPIView.as_view(), name='auth-register-api'),
    path('api/auth/register', RegisterAPIView.as_view(), name='auth-register-api-noslash'),
    path('api/auth/login/', LoginAPIView.as_view(), name='auth-login-api'),
    path('api/auth/login', LoginAPIView.as_view(), name='auth-login-api-noslash'),
    path('api/auth/logout/', LogoutAPIView.as_view(), name='auth-logout-api'),
    path('api/auth/logout', LogoutAPIView.as_view(), name='auth-logout-api-noslash'),
    path('api/auth/me/', CurrentUserAPIView.as_view(), name='auth-me-api'),

    # Interactive Web UI
    path('auth/register/', register_web_view, name='register-web'),
    path('auth/login/', login_web_view, name='login-web'),
    path('auth/logout/', logout_web_view, name='logout-web'),
]

