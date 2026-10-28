import io
import os
import re
import pandas as pd
from django.conf import settings
from rest_framework.exceptions import ValidationError


ALLOWED_EXTENSIONS = ('.csv',)
MAX_UPLOAD_SIZE = getattr(settings, 'MAX_UPLOAD_SIZE_BYTES', 10 * 1024 * 1024)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize uploaded filename to prevent directory traversal and injection attacks.
    """
    if not filename:
        return 'dataset.csv'
    # Remove directory separators and null bytes
    cleaned = os.path.basename(filename).replace('\x00', '')
    # Strip dangerous characters, retain alphanumerics, dots, underscores, dashes
    cleaned = re.sub(r'[^a-zA-Z0-9._-]', '_', cleaned)
    # Ensure it still ends with .csv
    if not cleaned.lower().endswith('.csv'):
        cleaned += '.csv'
    return cleaned


def validate_csv_file(uploaded_file):
    """
    Validates uploaded CSV file according to SRS ML-EVAL-F-010, ML-EVAL-F-011, and ML-EVAL-SR-003.

    Returns:
        tuple: (pandas.DataFrame, str sanitized_filename, int file_size)

    Raises:
        ValidationError: When the file fails any validation check.
    """
    if not uploaded_file:
        raise ValidationError('No file was provided.')

    # 1. Filename & extension validation
    original_name = getattr(uploaded_file, 'name', '')
    if not original_name or not original_name.lower().endswith('.csv'):
        raise ValidationError('Unsupported file format. Only CSV files (.csv) are accepted.')

    # 2. File size validation
    file_size = getattr(uploaded_file, 'size', 0)
    if file_size <= 0:
        raise ValidationError('The uploaded file is empty.')

    if file_size > MAX_UPLOAD_SIZE:
        max_mb = MAX_UPLOAD_SIZE / (1024 * 1024)
        raise ValidationError(f'File size exceeds maximum allowed limit of {max_mb:.0f} MB.')

    # 3. Read content & check encoding / tabular structure
    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)
        content_bytes = uploaded_file.read()
        uploaded_file.seek(0)
    except Exception as e:
        raise ValidationError(f'Failed to read uploaded file: {str(e)}')

    if not content_bytes or len(content_bytes.strip()) == 0:
        raise ValidationError('The uploaded file is empty.')

    # Attempt decoding with UTF-8, fallback to Latin-1
    decoded = None
    for encoding in ('utf-8', 'utf-8-sig', 'latin-1'):
        try:
            decoded = content_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    if decoded is None:
        raise ValidationError('Invalid file encoding. File must be valid UTF-8 text.')

    # 4. Tabular parsing using Pandas
    try:
        string_buffer = io.StringIO(decoded)
        df = pd.read_csv(string_buffer)
    except pd.errors.EmptyDataError:
        raise ValidationError('The CSV file does not contain any readable data.')
    except pd.errors.ParserError as e:
        raise ValidationError(f'Malformed CSV file: {str(e)}')
    except Exception as e:
        raise ValidationError(f'Failed to parse CSV file: {str(e)}')

    # 5. Row and column structure validation
    if df.shape[1] == 0:
        raise ValidationError('Dataset must contain at least one column.')

    if df.shape[0] == 0:
        raise ValidationError('Dataset must contain at least one data row.')

    # Ensure column headers are not all unnamed/empty
    non_empty_cols = [c for c in df.columns if str(c).strip() and not str(c).startswith('Unnamed:')]
    if not non_empty_cols:
        raise ValidationError('Dataset columns are invalid or missing names.')

    sanitized_name = sanitize_filename(original_name)
    return df, sanitized_name, file_size

