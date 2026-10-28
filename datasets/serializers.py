from rest_framework import serializers
from .models import Dataset


class DatasetSerializer(serializers.ModelSerializer):
    """
    Serializer for Dataset metadata.
    """
    class Meta:
        model = Dataset
        fields = [
            'id',
            'filename',
            'file_size',
            'row_count',
            'column_count',
            'columns',
            'uploaded_at',
        ]
        read_only_fields = fields

