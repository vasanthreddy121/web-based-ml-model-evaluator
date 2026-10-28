import json
import pandas as pd
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from datasets.models import Dataset
from .models import Experiment
from .ml_engine import MODEL_REGISTRY, train_and_evaluate_model
from .services import compare_experiments, export_experiment_results


class ExperimentTrainAPIView(APIView):
    """
    API endpoint to train and evaluate an ML model on a dataset.
    Endpoint: POST /api/experiments/train/
    Corresponds to SAD 4.3.2, SRS ML-EVAL-F-020 to ML-EVAL-F-034.
    """
    def post(self, request, *args, **kwargs):
        data = request.data or {}
        dataset_id = data.get('dataset_id')
        if not dataset_id:
            return Response({'status': 'error', 'error': 'dataset_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dataset = Dataset.objects.get(pk=dataset_id)
        except Dataset.DoesNotExist:
            return Response({'status': 'error', 'error': f'Dataset #{dataset_id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Authorization check
        if dataset.user and request.user.is_authenticated and request.user != dataset.user:
            return Response({'status': 'error', 'error': 'You do not have permission to use this dataset.'}, status=status.HTTP_403_FORBIDDEN)

        problem_type = data.get('problem_type')
        model_name = data.get('model_name')
        target_column = data.get('target_column')
        feature_columns = data.get('feature_columns')
        hyperparameters = data.get('hyperparameters', {})
        preprocessing_config = data.get('preprocessing_config', {})
        name = data.get('name', f"{model_name} on {dataset.filename}")

        if not problem_type or not model_name or not target_column:
            return Response(
                {'status': 'error', 'error': 'problem_type, model_name, and target_column are required fields.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            df = pd.read_csv(dataset.file.path)
            res = train_and_evaluate_model(
                df=df,
                problem_type=problem_type,
                model_name=model_name,
                target_column=target_column,
                feature_columns=feature_columns,
                hyperparameters=hyperparameters,
                preprocessing_config=preprocessing_config
            )
        except ValidationError as e:
            err_msg = e.detail[0] if isinstance(e.detail, list) else str(e.detail)
            return Response({'status': 'error', 'error': err_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'error': f'Training failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Persist Experiment
        user = request.user if request.user.is_authenticated else None
        experiment = Experiment.objects.create(
            user=user,
            dataset=dataset,
            name=name,
            problem_type=res['problem_type'],
            model_name=res['model_name'],
            model_display_name=res['model_display_name'],
            hyperparameters=res['hyperparameters'],
            preprocessing_config=preprocessing_config,
            metrics=res['metrics'],
            predictions_sample=res['predictions_sample'],
            training_time_seconds=res['training_time_seconds'],
            status='completed'
        )

        return Response(
            {
                'status': 'success',
                'message': 'Model trained and evaluated successfully.',
                'experiment_id': experiment.id,
                'name': experiment.name,
                'problem_type': experiment.problem_type,
                'model': experiment.model_display_name,
                'metrics': experiment.metrics,
                'training_time_seconds': experiment.training_time_seconds,
                'predictions_sample': experiment.predictions_sample
            },
            status=status.HTTP_201_CREATED
        )


class ExperimentResultsAPIView(APIView):
    """
    API endpoint to retrieve evaluation results of an experiment.
    Endpoint: GET /api/experiments/{id}/results/
    Corresponds to SAD 4.3.2 and SRS ML-EVAL-F-042.
    """
    def get(self, request, pk, *args, **kwargs):
        try:
            exp = Experiment.objects.get(pk=pk)
        except Experiment.DoesNotExist:
            return Response({'status': 'error', 'error': f'Experiment #{pk} not found.'}, status=status.HTTP_404_NOT_FOUND)

        if exp.user and request.user.is_authenticated and request.user != exp.user:
            return Response({'status': 'error', 'error': 'You do not have permission to view this experiment.'}, status=status.HTTP_403_FORBIDDEN)

        return Response(
            {
                'status': 'success',
                'experiment_id': exp.id,
                'name': exp.name,
                'problem_type': exp.problem_type,
                'model': exp.model_display_name,
                'model_name': exp.model_name,
                'dataset_id': exp.dataset.id,
                'dataset_filename': exp.dataset.filename,
                'training_time_seconds': exp.training_time_seconds,
                'hyperparameters': exp.hyperparameters,
                'preprocessing_config': exp.preprocessing_config,
                'metrics': exp.metrics,
                'predictions_sample': exp.predictions_sample,
                'created_at': exp.created_at.isoformat()
            },
            status=status.HTTP_200_OK
        )


class ExperimentCompareAPIView(APIView):
    """
    API endpoint to compare 2+ compatible model experiments.
    Endpoint: POST /api/experiments/compare/
    Corresponds to SAD 4.3.2 and SRS ML-EVAL-F-040.
    """
    def post(self, request, *args, **kwargs):
        data = request.data or {}
        experiment_ids = data.get('experiment_ids', [])
        if not experiment_ids or len(experiment_ids) < 2:
            return Response({'status': 'error', 'error': 'Please provide a list of at least two experiment_ids to compare.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            comparison = compare_experiments(experiment_ids, user=request.user)
            return Response({'status': 'success', 'comparison': comparison}, status=status.HTTP_200_OK)
        except ValidationError as e:
            err_msg = e.detail[0] if isinstance(e.detail, list) else str(e.detail)
            return Response({'status': 'error', 'error': err_msg}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except NotFound as e:
            return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'error': f'Comparison failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class ExperimentExportAPIView(APIView):
    """
    API endpoint to export evaluation results in CSV or JSON.
    Endpoint: GET /api/experiments/{id}/export/?format=csv|json
    Corresponds to SAD 4.3.2 and SRS ML-EVAL-F-043.
    """
    def perform_content_negotiation(self, request, force=False):
        # Override DRF content negotiation so ?format=csv does not trigger 404
        renderers = self.get_renderers()
        return (renderers[0], renderers[0].media_type)

    def get(self, request, pk, *args, **kwargs):
        try:
            exp = Experiment.objects.get(pk=pk)
        except Experiment.DoesNotExist:
            return Response({'status': 'error', 'error': f'Experiment #{pk} not found.'}, status=status.HTTP_404_NOT_FOUND)

        if exp.user and request.user.is_authenticated and request.user != exp.user:
            return Response({'status': 'error', 'error': 'You do not have permission to export this experiment.'}, status=status.HTTP_403_FORBIDDEN)

        export_format = request.GET.get('format', 'json').lower()
        if export_format not in ('csv', 'json'):
            return Response({'status': 'error', 'error': "Supported export formats: 'json' or 'csv'."}, status=status.HTTP_400_BAD_REQUEST)

        return export_experiment_results(exp, export_format=export_format)


# -------------------------------------------------------------
# WEB UI VIEWS
# -------------------------------------------------------------

def experiment_train_web_view(request, dataset_id):
    """Web UI view to select model, problem type, parameters, and train."""
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    if dataset.user and request.user.is_authenticated and request.user != dataset.user:
        messages.error(request, 'Access denied: You are not authorized to use this dataset.')
        return redirect('dataset-web-upload')

    if request.method == 'POST':
        problem_type = request.POST.get('problem_type')
        model_name = request.POST.get('model_name')
        target_column = request.POST.get('target_column')
        feature_columns = request.POST.getlist('feature_columns')
        missing_strategy = request.POST.get('missing_strategy', 'mean')
        scaling = request.POST.get('scaling', 'standard')
        encoding = request.POST.get('encoding', 'one_hot')
        test_size = float(request.POST.get('test_size', 0.2))

        # Hyperparameter values
        hyperparameters = {}
        if model_name in ('decision_tree', 'decision_tree_regressor', 'random_forest', 'random_forest_regressor'):
            max_depth = request.POST.get('max_depth')
            if max_depth and max_depth.isdigit():
                hyperparameters['max_depth'] = int(max_depth)
        if model_name in ('random_forest', 'random_forest_regressor', 'gradient_boosting_regressor'):
            n_est = request.POST.get('n_estimators')
            if n_est and n_est.isdigit():
                hyperparameters['n_estimators'] = int(n_est)
        if model_name in ('knn',):
            n_nbrs = request.POST.get('n_neighbors')
            if n_nbrs and n_nbrs.isdigit():
                hyperparameters['n_neighbors'] = int(n_nbrs)

        prep_config = {
            'missing_strategy': missing_strategy,
            'scaling': scaling,
            'encoding': encoding,
            'test_size': test_size,
            'random_state': 42
        }

        try:
            df = pd.read_csv(dataset.file.path)
            res = train_and_evaluate_model(
                df=df,
                problem_type=problem_type,
                model_name=model_name,
                target_column=target_column,
                feature_columns=feature_columns,
                hyperparameters=hyperparameters,
                preprocessing_config=prep_config
            )
            user = request.user if request.user.is_authenticated else None
            exp = Experiment.objects.create(
                user=user,
                dataset=dataset,
                name=f"{res['model_display_name']} on {dataset.filename}",
                problem_type=res['problem_type'],
                model_name=res['model_name'],
                model_display_name=res['model_display_name'],
                hyperparameters=res['hyperparameters'],
                preprocessing_config=prep_config,
                metrics=res['metrics'],
                predictions_sample=res['predictions_sample'],
                training_time_seconds=res['training_time_seconds'],
                status='completed'
            )
            messages.success(request, f"Model {exp.model_display_name} trained successfully in {exp.training_time_seconds}s!")
            return redirect('experiment-results-web', pk=exp.id)
        except ValidationError as e:
            err_msg = e.detail[0] if isinstance(e.detail, list) else str(e.detail)
            messages.error(request, f"Configuration Error: {err_msg}")
        except Exception as e:
            messages.error(request, f"Training Failed: {str(e)}")

    return render(request, 'experiments/train.html', {
        'dataset': dataset,
        'columns': dataset.columns,
        'model_registry': MODEL_REGISTRY
    })


def experiment_results_web_view(request, pk):
    """Web UI view to display evaluation metrics, charts, predictions, and export."""
    exp = get_object_or_404(Experiment, pk=pk)
    if exp.user and request.user.is_authenticated and request.user != exp.user:
        messages.error(request, 'Access denied: You are not authorized to view this experiment.')
        return redirect('experiment-history-web')

    return render(request, 'experiments/results.html', {
        'experiment': exp,
        'metrics': exp.metrics,
        'predictions': exp.predictions_sample
    })


def experiment_history_web_view(request):
    """Web UI view to list historical experiments and select for comparison."""
    if request.user.is_authenticated:
        experiments = Experiment.objects.filter(models.Q(user=request.user) | models.Q(user__isnull=True))
    else:
        experiments = Experiment.objects.all()

    return render(request, 'experiments/history.html', {
        'experiments': experiments
    })


def experiment_compare_web_view(request):
    """Web UI view to display side-by-side experiment comparison and charts."""
    exp_ids = request.GET.getlist('exp_id') or request.POST.getlist('exp_id')
    if not exp_ids or len(exp_ids) < 2:
        messages.error(request, 'Please select at least two experiments to compare.')
        return redirect('experiment-history-web')

    try:
        int_ids = [int(i) for i in exp_ids]
        comparison = compare_experiments(int_ids, user=request.user)
    except Exception as e:
        messages.error(request, f"Comparison Error: {str(e)}")
        return redirect('experiment-history-web')

    return render(request, 'experiments/compare.html', {
        'comparison': comparison
    })
