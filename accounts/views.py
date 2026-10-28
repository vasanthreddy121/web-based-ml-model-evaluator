from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer


class RegisterAPIView(APIView):
    """
    API endpoint for user registration.
    Endpoint: POST /api/auth/register/
    Corresponds to SRS ML-EVAL-F-001 and TC-AUTH-01.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response(
                {
                    'status': 'success',
                    'message': 'User registered and authenticated successfully.',
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    """
    API endpoint for user authentication.
    Endpoint: POST /api/auth/login/
    Corresponds to SRS ML-EVAL-F-002 and TC-AUTH-02.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response(
                {
                    'status': 'success',
                    'message': 'Authentication successful.',
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_200_OK
            )
        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """
    API endpoint to terminate session.
    Endpoint: POST /api/auth/logout/
    Corresponds to SRS ML-EVAL-F-003 and TC-AUTH-03.
    """
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({'status': 'success', 'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)


class CurrentUserAPIView(APIView):
    """
    API endpoint to inspect active session context.
    Endpoint: GET /api/auth/me/
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({'status': 'success', 'authenticated': True, 'user': UserSerializer(request.user).data})
        return Response({'status': 'success', 'authenticated': False, 'user': None})


# -------------------------------------------------------------
# WEB UI VIEWS
# -------------------------------------------------------------

def register_web_view(request):
    """Web view for user registration."""
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        serializer = UserRegisterSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been registered.')
            return redirect('/')
        else:
            for field, errs in serializer.errors.items():
                messages.error(request, f"{field.capitalize()}: {errs[0]}")

    return render(request, 'accounts/register.html')


def login_web_view(request):
    """Web view for user authentication."""
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        serializer = UserLoginSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_web_view(request):
    """Web view to log out."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login-web')
