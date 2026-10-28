import io
import csv
import json
from typing import List, Dict, Any
from django.http import HttpResponse
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from .models import Experiment


def compare_experiments(experiment_ids: List[int], user=None) -> Dict[str, Any]:
    """
    Compares two or more compatible experiments.
    Implements SRS ML-EVAL-F-040 and TC-COMP-01.
    """
    if not experiment_ids or len(experiment_ids) < 2:
        raise ValidationError("Comparison requires at least two experiment IDs.")

    experiments = list(Experiment.objects.filter(id__in=experiment_ids))
    if len(experiments) < 2:
        raise NotFound("Could not find at least two valid experiments for the requested IDs.")

    # Authorization check
    if user and user.is_authenticated:
        for exp in experiments:
            if exp.user and exp.user != user:
                raise PermissionDenied(f"You do not have permission to view experiment #{exp.id}.")

    # Compatibility check (all must share the same problem_type)
    problem_types = set(exp.problem_type for exp in experiments)
    if len(problem_types) > 1:
        raise ValidationError("Incompatible experiments: cannot compare classification and regression experiments together.")

    problem_type = experiments[0].problem_type

    # Compile comparison rows
    comparison_table = []
    best_exp = None
    best_score = -float('inf') if problem_type == 'classification' else float('inf')

    for exp in experiments:
        m = exp.metrics or {}
        row = {
            'id': exp.id,
            'name': exp.name,
            'model_display_name': exp.model_display_name,
            'model_name': exp.model_name,
            'training_time_seconds': exp.training_time_seconds,
            'created_at': exp.created_at.strftime('%Y-%m-%d %H:%M'),
            'metrics': m
        }
        comparison_table.append(row)

        # Primary metric calculation for best model badge
        if problem_type == 'classification':
            score = m.get('f1_score', m.get('accuracy', 0.0))
            if score > best_score:
                best_score = score
                best_exp = exp
        else:
            score = m.get('rmse', float('inf'))
            if score < best_score:
                best_score = score
                best_exp = exp

    # Visual chart payload
    chart_labels = [f"#{e.id} {e.model_display_name}" for e in experiments]
    chart_datasets = []

    if problem_type == 'classification':
        chart_datasets = [
            {'label': 'Accuracy', 'data': [e.metrics.get('accuracy', 0.0) for e in experiments]},
            {'label': 'Precision', 'data': [e.metrics.get('precision', 0.0) for e in experiments]},
            {'label': 'Recall', 'data': [e.metrics.get('recall', 0.0) for e in experiments]},
            {'label': 'F1 Score', 'data': [e.metrics.get('f1_score', 0.0) for e in experiments]},
        ]
    else:
        chart_datasets = [
            {'label': 'MAE', 'data': [e.metrics.get('mae', 0.0) for e in experiments]},
            {'label': 'RMSE', 'data': [e.metrics.get('rmse', 0.0) for e in experiments]},
            {'label': 'R² Score', 'data': [e.metrics.get('r2_score', 0.0) for e in experiments]},
        ]

    return {
        'problem_type': problem_type,
        'count': len(experiments),
        'best_experiment_id': best_exp.id if best_exp else None,
        'best_model_name': best_exp.model_display_name if best_exp else None,
        'comparison_table': comparison_table,
        'charts': {
            'labels': chart_labels,
            'datasets': chart_datasets
        }
    }


def export_experiment_results(experiment: Experiment, export_format: str = 'json') -> HttpResponse:
    """
    Exports experiment evaluation results as downloadable CSV or JSON.
    Implements SRS ML-EVAL-F-043 and TC-EXP-01.
    """
    export_format = export_format.lower().strip()
    filename = f"experiment_{experiment.id}_{experiment.model_name}_results"

    if export_format == 'csv':
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        # Write Experiment Header
        writer.writerow(['Experiment ID', experiment.id])
        writer.writerow(['Model', experiment.model_display_name])
        writer.writerow(['Problem Type', experiment.problem_type])
        writer.writerow(['Dataset', experiment.dataset.filename])
        writer.writerow(['Training Time (s)', experiment.training_time_seconds])
        writer.writerow([])

        # Write Evaluation Metrics
        writer.writerow(['--- Evaluation Metrics ---'])
        writer.writerow(['Metric', 'Value'])
        for k, v in (experiment.metrics or {}).items():
            if k not in ('confusion_matrix', 'classes'):
                writer.writerow([k, v])
        writer.writerow([])

        # Write Test Predictions Sample
        writer.writerow(['--- Test Predictions Sample ---'])
        samples = experiment.predictions_sample or []
        if samples:
            headers = list(samples[0].keys())
            writer.writerow(headers)
            for row in samples:
                writer.writerow([row.get(h, '') for h in headers])

        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        return response

    # Default: JSON format
    data = {
        'experiment_id': experiment.id,
        'name': experiment.name,
        'problem_type': experiment.problem_type,
        'model_name': experiment.model_name,
        'model_display_name': experiment.model_display_name,
        'dataset_id': experiment.dataset.id,
        'dataset_filename': experiment.dataset.filename,
        'training_time_seconds': experiment.training_time_seconds,
        'hyperparameters': experiment.hyperparameters,
        'preprocessing_config': experiment.preprocessing_config,
        'metrics': experiment.metrics,
        'predictions_sample': experiment.predictions_sample,
        'created_at': experiment.created_at.isoformat()
    }
    json_str = json.dumps(data, indent=2)
    response = HttpResponse(json_str, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
    return response

