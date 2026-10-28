import os
from django.db import models
from django.contrib.auth.models import User


class Dataset(models.Model):
    """
    Represents an uploaded and validated tabular CSV dataset.
    Corresponds to SRS ML-EVAL-F-010, ML-EVAL-F-011, and SAD DatasetModule.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='datasets')
    file = models.FileField(upload_to='datasets/')
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(help_text='File size in bytes')
    row_count = models.IntegerField(help_text='Number of data rows excluding header')
    column_count = models.IntegerField(help_text='Number of columns')
    columns = models.JSONField(default=list, help_text='List of column names')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} ({self.row_count} rows, {self.column_count} columns)"

    def delete(self, *args, **kwargs):
        # Clean up storage file on model deletion
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)
