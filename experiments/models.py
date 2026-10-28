from django.db import models
from django.contrib.auth.models import User
from datasets.models import Dataset


class Experiment(models.Model):
    """
    Represents a trained machine learning experiment with its configuration,
    evaluation metrics, and predictions.
    Corresponds to SAD Experiment/Results Service and SRS ML-EVAL-F-042.
    """
    PROBLEM_TYPE_CHOICES = (
        ('classification', 'Classification'),
        ('regression', 'Regression'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='experiments')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='experiments')
    name = models.CharField(max_length=255, default='ML Experiment')
    problem_type = models.CharField(max_length=50, choices=PROBLEM_TYPE_CHOICES)
    model_name = models.CharField(max_length=100)
    model_display_name = models.CharField(max_length=150)
    hyperparameters = models.JSONField(default=dict)
    preprocessing_config = models.JSONField(default=dict)
    metrics = models.JSONField(default=dict)
    predictions_sample = models.JSONField(default=list)
    training_time_seconds = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, default='completed')
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.model_display_name} ({self.problem_type}) #{self.id}"
