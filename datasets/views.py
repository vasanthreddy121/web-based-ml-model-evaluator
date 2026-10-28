from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError, NotFound

from .models import Dataset
from .validators import validate_csv_file
from .serializers import DatasetSerializer
from .services import profile_dataset, clean_for_json
from .preprocessing import PreprocessingPipeline


class DatasetUploadAPIView(APIView):
    """
    API endpoint for uploading and validating CSV datasets.
    Endpoint: POST /api/datasets/upload/
    Corresponds to SAD 4.3.1 Dataset Management Interface and SRS ML-EVAL-F-010, ML-EVAL-F-011.
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {'status': 'error', 'error': 'No file was provided in the request under the key "file".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            df, sanitized_filename, file_size = validate_csv_file(uploaded_file)
        except ValidationError as e:
            error_message = e.detail[0] if isinstance(e.detail, list) else str(e.detail)
            return Response(
                {'status': 'error', 'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'status': 'error', 'error': f'Validation failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # File is valid; persist Dataset
        user = request.user if request.user.is_authenticated else None
        dataset = Dataset.objects.create(
            user=user,
            file=uploaded_file,
            filename=sanitized_filename,
            file_size=file_size,
            row_count=int(df.shape[0]),
            column_count=int(df.shape[1]),
            columns=list(df.columns),
        )

        serializer = DatasetSerializer(dataset)
        return Response(
            {
                'status': 'success',
                'message': 'Dataset uploaded and validated successfully.',
                'dataset': serializer.data
            },
            status=status.HTTP_201_CREATED
        )


def dataset_upload_web_view(request):
    """
    Web UI view for interactive CSV dataset upload and validation.
    """
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            messages.error(request, 'Please select a CSV file to upload.')
            return redirect('dataset-web-upload')

        try:
            df, sanitized_filename, file_size = validate_csv_file(uploaded_file)
            user = request.user if request.user.is_authenticated else None
            dataset = Dataset.objects.create(
                user=user,
                file=uploaded_file,
                filename=sanitized_filename,
                file_size=file_size,
                row_count=int(df.shape[0]),
                column_count=int(df.shape[1]),
                columns=list(df.columns),
            )
            messages.success(
                request,
                f'Dataset "{sanitized_filename}" uploaded successfully! ({dataset.row_count} rows, {dataset.column_count} columns)'
            )
            return redirect('dataset-web-upload')
        except ValidationError as e:
            err_msg = e.detail[0] if isinstance(e.detail, list) else str(e.detail)
            messages.error(request, f'Validation error: {err_msg}')
        except Exception as e:
            messages.error(request, f'Upload failed: {str(e)}')

    datasets = Dataset.objects.all().order_by('-uploaded_at')[:10]
    return render(request, 'datasets/upload.html', {'datasets': datasets})


class DatasetPreviewAPIView(APIView):
    """
    API endpoint to preview and profile an uploaded dataset.
    Endpoint: GET /api/datasets/{id}/preview/
    Corresponds to SAD 4.3.1, SRS ML-EVAL-F-012, TC-DATA-03, and TC-SEC-01.
    """
    def get(self, request, pk, *args, **kwargs):
        try:
            dataset = Dataset.objects.get(pk=pk)
        except Dataset.DoesNotExist:
            return Response(
                {'status': 'error', 'error': f'Dataset with id {pk} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Authorization check: object-level isolation (TC-SEC-01, TC-SEC-05)
        if dataset.user and request.user.is_authenticated and request.user != dataset.user:
            return Response(
                {'status': 'error', 'error': 'You do not have permission to access this dataset.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            profiling = profile_dataset(dataset.file.path)
        except NotFound as e:
            return Response(
                {'status': 'error', 'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'status': 'error', 'error': f'Failed to profile dataset: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'status': 'success',
                'dataset_id': dataset.id,
                'filename': dataset.filename,
                'profiling': profiling
            },
            status=status.HTTP_200_OK
        )


def dataset_preview_web_view(request, pk):
    """
    Web UI view to display dataset preview, profiling metrics, missing values, and statistics.
    """
    dataset = get_object_or_404(Dataset, pk=pk)
    if dataset.user and request.user.is_authenticated and request.user != dataset.user:
        messages.error(request, 'Access denied: You are not authorized to view this dataset.')
        return redirect('dataset-web-upload')

    try:
        profiling = profile_dataset(dataset.file.path)
    except Exception as e:
        messages.error(request, f'Could not profile dataset: {str(e)}')
        return redirect('dataset-web-upload')

    return render(request, 'datasets/preview.html', {
        'dataset': dataset,
        'profiling': profiling
    })


class DatasetPreprocessAPIView(APIView):
    """
    API endpoint to configure and execute data preprocessing, cleaning, encoding, scaling,
    and train/test splitting.
    Endpoint: POST /api/datasets/{id}/preprocess/
    Corresponds to SRS ML-EVAL-F-013, ML-EVAL-F-014, ML-EVAL-F-015, TC-DATA-04 to TC-DATA-06.
    """
    def post(self, request, pk, *args, **kwargs):
        try:
            dataset = Dataset.objects.get(pk=pk)
        except Dataset.DoesNotExist:
            return Response(
                {'status': 'error', 'error': f'Dataset with id {pk} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Authorization check
        if dataset.user and request.user.is_authenticated and request.user != dataset.user:
            return Response(
                {'status': 'error', 'error': 'You do not have permission to access this dataset.'},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data or {}
        target_column = data.get('target_column')
        feature_columns = data.get('feature_columns')
        missing_strategy = data.get('missing_strategy', 'mean')
        handle_duplicates = data.get('handle_duplicates', True)
        encoding = data.get('encoding', 'one_hot')
        scaling = data.get('scaling', 'standard')
        test_size = data.get('test_size', 0.2)
        random_state = data.get('random_state', 42)

        try:
            import pandas as pd
            df = pd.read_csv(dataset.file.path)
            pipeline = PreprocessingPipeline(
                target_column=target_column,
                feature_columns=feature_columns,
                missing_strategy=missing_strategy,
                handle_duplicates=handle_duplicates,
                encoding=encoding,
                scaling=scaling,
                test_size=test_size,
                random_state=random_state
            )
            result = pipeline.process_and_split(df)
        except ValidationError as e:
            err_msg = e.detail[0] if isinstance(e.detail, list) else str(e.detail)
            return Response({'status': 'error', 'error': err_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'error': f'Preprocessing failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Build clean JSON preview
        X_train_preview = []
        for rec in result['X_train'].head(5).to_dict(orient='records'):
            X_train_preview.append({k: clean_for_json(v) for k, v in rec.items()})

        y_train_preview = [clean_for_json(v) for v in result['y_train'].head(5).tolist()]

        return Response(
            {
                'status': 'success',
                'dataset_id': dataset.id,
                'summary': {
                    'train_samples': result['train_size'],
                    'test_samples': result['test_size'],
                    'transformed_features_count': len(result['feature_names']),
                    'transformed_features': result['feature_names'],
                    'duplicates_removed': result['duplicates_removed'],
                    'imputation_values': result['imputation_values'],
                    'scaling': result['scaling_used'],
                    'encoding': result['encoding_used'],
                    'test_ratio': result['test_ratio']
                },
                'preview': {
                    'X_train_head': X_train_preview,
                    'y_train_head': y_train_preview
                }
            },
            status=status.HTTP_200_OK
        )


def dataset_preprocess_web_view(request, pk):
    """
    Web UI view for interactive preprocessing configuration and preview.
    """
    dataset = get_object_or_404(Dataset, pk=pk)
    if dataset.user and request.user.is_authenticated and request.user != dataset.user:
        messages.error(request, 'Access denied: You are not authorized to view this dataset.')
        return redirect('dataset-web-upload')

    summary = None
    preview = None

    if request.method == 'POST':
        target_column = request.POST.get('target_column')
        feature_columns = request.POST.getlist('feature_columns')
        missing_strategy = request.POST.get('missing_strategy', 'mean')
        handle_duplicates = request.POST.get('handle_duplicates') == 'on'
        encoding = request.POST.get('encoding', 'one_hot')
        scaling = request.POST.get('scaling', 'standard')
        test_size = float(request.POST.get('test_size', 0.2))

        try:
            import pandas as pd
            df = pd.read_csv(dataset.file.path)
            pipeline = PreprocessingPipeline(
                target_column=target_column,
                feature_columns=feature_columns,
                missing_strategy=missing_strategy,
                handle_duplicates=handle_duplicates,
                encoding=encoding,
                scaling=scaling,
                test_size=test_size,
                random_state=42
            )
            result = pipeline.process_and_split(df)
            summary = {
                'train_samples': result['train_size'],
                'test_samples': result['test_size'],
                'transformed_features_count': len(result['feature_names']),
                'transformed_features': result['feature_names'],
                'duplicates_removed': result['duplicates_removed'],
                'scaling': result['scaling_used'],
                'encoding': result['encoding_used'],
                'test_ratio': result['test_ratio']
            }
            preview_rows = []
            for rec in result['X_train'].head(5).to_dict(orient='records'):
                preview_rows.append([clean_for_json(rec.get(c)) for c in result['feature_names']])
            preview = {
                'columns': result['feature_names'],
                'rows': preview_rows
            }
            messages.success(request, f'Preprocessing applied successfully! {result["train_size"]} training samples, {result["test_size"]} test samples.')
        except ValidationError as e:
            err_msg = e.detail[0] if isinstance(e.detail, list) else str(e.detail)
            messages.error(request, f'Configuration error: {err_msg}')
        except Exception as e:
            messages.error(request, f'Preprocessing failed: {str(e)}')

    return render(request, 'datasets/preprocess.html', {
        'dataset': dataset,
        'columns': dataset.columns,
        'summary': summary,
        'preview': preview
    })


