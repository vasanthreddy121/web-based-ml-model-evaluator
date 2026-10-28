import os
import math
import numpy as np
import pandas as pd
from typing import Dict, Any
from rest_framework.exceptions import ValidationError, NotFound


def clean_for_json(val):
    """Convert numpy / pandas types and NaN / Inf values into standard JSON-serializable types."""
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(val)
    if isinstance(val, (np.floating, np.float64, np.float32, float)):
        if math.isnan(val) or math.isinf(val):
            return None
        return round(float(val), 4)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    if isinstance(val, (pd.Timestamp, np.datetime64)):
        return str(val)
    return str(val)


def profile_dataset(file_path: str, preview_rows: int = 10) -> Dict[str, Any]:
    """
    Computes profiling metadata, data types, missing value counts, duplicate count,
    summary statistics, and preview rows from a CSV dataset.
    Corresponds to SRS ML-EVAL-F-012, SAD DataPipeline profiling, and TC-DATA-03.
    """
    if not os.path.exists(file_path):
        raise NotFound("Dataset file does not exist on storage.")

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValidationError(f"Failed to read dataset for profiling: {str(e)}")

    row_count, col_count = df.shape
    columns = list(df.columns)

    # 1. Column data types
    dtypes = {}
    for col in columns:
        dtype_str = str(df[col].dtype)
        if 'int' in dtype_str:
            friendly_type = 'integer'
        elif 'float' in dtype_str:
            friendly_type = 'numeric'
        elif 'bool' in dtype_str:
            friendly_type = 'boolean'
        elif 'datetime' in dtype_str:
            friendly_type = 'datetime'
        else:
            friendly_type = 'categorical'
        dtypes[col] = {
            'raw_type': dtype_str,
            'simplified_type': friendly_type
        }

    # 2. Missing values per column and total
    missing_by_col = {}
    total_missing = 0
    column_profiles = []
    for col in columns:
        col_missing = int(df[col].isna().sum())
        total_missing += col_missing
        pct = round((col_missing / row_count) * 100, 2) if row_count > 0 else 0.0
        missing_by_col[col] = {
            'count': col_missing,
            'percentage': pct
        }
        column_profiles.append({
            'name': col,
            'simplified_type': dtypes[col]['simplified_type'],
            'raw_type': dtypes[col]['raw_type'],
            'missing_count': col_missing,
            'missing_percentage': pct
        })

    # 3. Duplicate rows count
    duplicate_count = int(df.duplicated().sum())

    # 4. Preview rows (head)
    preview_df = df.head(preview_rows)
    preview_records = []
    preview_table_rows = []
    for idx, record in enumerate(preview_df.to_dict(orient='records')):
        clean_record = {k: clean_for_json(v) for k, v in record.items()}
        preview_records.append(clean_record)
        preview_table_rows.append([clean_for_json(record.get(c)) for c in columns])

    # 5. Descriptive statistics
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = [c for c in columns if c not in numeric_cols]

    statistics = {}
    if numeric_cols:
        num_desc = df[numeric_cols].describe().to_dict()
        for col, metrics in num_desc.items():
            statistics[col] = {
                'type': 'numeric',
                'count': clean_for_json(metrics.get('count')),
                'mean': clean_for_json(metrics.get('mean')),
                'std': clean_for_json(metrics.get('std')),
                'min': clean_for_json(metrics.get('min')),
                'q25': clean_for_json(metrics.get('25%')),
                'median': clean_for_json(metrics.get('50%')),
                'q75': clean_for_json(metrics.get('75%')),
                'max': clean_for_json(metrics.get('max')),
                '25%': clean_for_json(metrics.get('25%')),
                '50%': clean_for_json(metrics.get('50%')),
                '75%': clean_for_json(metrics.get('75%')),
            }

    if categorical_cols:
        for col in categorical_cols:
            col_series = df[col].dropna()
            val_counts = col_series.value_counts()
            top_val = val_counts.index[0] if not val_counts.empty else None
            top_freq = int(val_counts.iloc[0]) if not val_counts.empty else 0
            statistics[col] = {
                'type': 'categorical',
                'count': int(col_series.count()),
                'unique': int(col_series.nunique()),
                'top': clean_for_json(top_val),
                'freq': top_freq,
            }

    return {
        'row_count': row_count,
        'column_count': col_count,
        'columns': columns,
        'dtypes': dtypes,
        'column_profiles': column_profiles,
        'missing_values': {
            'by_column': missing_by_col,
            'total_missing': total_missing
        },
        'duplicate_rows_count': duplicate_count,
        'preview': preview_records,
        'preview_table_rows': preview_table_rows,
        'statistics': statistics
    }
