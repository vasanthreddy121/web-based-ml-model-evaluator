from django.urls import path
from .views import (
    ExperimentTrainAPIView,
    ExperimentResultsAPIView,
    ExperimentCompareAPIView,
    ExperimentExportAPIView,
    experiment_train_web_view,
    experiment_results_web_view,
    experiment_history_web_view,
    experiment_compare_web_view,
)

urlpatterns = [
    # REST API endpoints (SAD 4.3.2)
    path('api/experiments/train/', ExperimentTrainAPIView.as_view(), name='experiment-train-api'),
    path('api/experiments/train', ExperimentTrainAPIView.as_view(), name='experiment-train-api-noslash'),
    path('api/experiments/<int:pk>/results/', ExperimentResultsAPIView.as_view(), name='experiment-results-api'),
    path('api/experiments/<int:pk>/results', ExperimentResultsAPIView.as_view(), name='experiment-results-api-noslash'),
    path('api/experiments/compare/', ExperimentCompareAPIView.as_view(), name='experiment-compare-api'),
    path('api/experiments/compare', ExperimentCompareAPIView.as_view(), name='experiment-compare-api-noslash'),
    path('api/experiments/<int:pk>/export/', ExperimentExportAPIView.as_view(), name='experiment-export-api'),
    path('api/experiments/<int:pk>/export', ExperimentExportAPIView.as_view(), name='experiment-export-api-noslash'),

    # Interactive Web UI
    path('experiments/train/<int:dataset_id>/', experiment_train_web_view, name='experiment-train-web'),
    path('experiments/<int:pk>/results/', experiment_results_web_view, name='experiment-results-web'),
    path('experiments/history/', experiment_history_web_view, name='experiment-history-web'),
    path('experiments/compare/', experiment_compare_web_view, name='experiment-compare-web'),
]

