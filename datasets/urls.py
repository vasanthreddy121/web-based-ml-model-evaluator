from django.urls import path
from .views import (
    DatasetUploadAPIView,
    DatasetPreviewAPIView,
    DatasetPreprocessAPIView,
    dataset_upload_web_view,
    dataset_preview_web_view,
    dataset_preprocess_web_view,
)

urlpatterns = [
    # REST API endpoints (SAD 4.3)
    path('api/datasets/upload/', DatasetUploadAPIView.as_view(), name='dataset-upload-api'),
    path('api/datasets/upload', DatasetUploadAPIView.as_view(), name='dataset-upload-api-noslash'),
    path('api/datasets/<int:pk>/preview/', DatasetPreviewAPIView.as_view(), name='dataset-preview-api'),
    path('api/datasets/<int:pk>/preview', DatasetPreviewAPIView.as_view(), name='dataset-preview-api-noslash'),
    path('api/datasets/<int:pk>/preprocess/', DatasetPreprocessAPIView.as_view(), name='dataset-preprocess-api'),
    path('api/datasets/<int:pk>/preprocess', DatasetPreprocessAPIView.as_view(), name='dataset-preprocess-api-noslash'),

    # Interactive Web UI
    path('datasets/<int:pk>/preview/', dataset_preview_web_view, name='dataset-preview-web'),
    path('datasets/<int:pk>/preprocess/', dataset_preprocess_web_view, name='dataset-preprocess-web'),
    path('upload/', dataset_upload_web_view, name='dataset-web-upload'),
    path('', dataset_upload_web_view, name='dataset-home'),
]

