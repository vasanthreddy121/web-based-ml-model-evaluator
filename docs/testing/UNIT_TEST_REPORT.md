# Unit Testing Report

**Project:** Web-Based ML Model Evaluator (Team 16)  
**Date of Execution:** November 5, 2026  
**Test Runner:** `pytest 8.4.2` with `pytest-django 4.14.0`  
**Execution Environment:** Linux Ubuntu x86_64, Python 3.12.3, Django 5.1.15  
**Total Unit Tests:** **187**  
**Passed:** **187 (100%)**  
**Failed / Errored:** **0**  
**Total Duration:** **~41.9 seconds**  

---

## 1. Executive Summary

This report documents the unit-level verification of individual components, services, utility functions, validators, and serializers across the **Web-Based ML Model Evaluator**. Unit tests isolate specific functional behaviors, test boundary values, validate edge-case input handling, and confirm that mathematical metric evaluations and preprocessing algorithms produce expected outcomes without side-effects.

All 187 unit tests pass with zero failures and zero errors.

---

## 2. Unit Test Breakdown by Component

### 2.1. Authentication & Security Services (`tests/test_authentication.py`)
- **Unit Test Count:** 7 tests
- **Component Under Test:** `accounts/serializers.py`, `accounts/views.py`, Django `auth.models.User`
- **Scope & Verified Behaviors:**
  - `test_tc_auth_01_user_registration_api_success`: Verifies valid user payload creation, serialized JSON response, and status 201.
  - `test_tc_auth_01_registration_duplicate_username_rejected`: Asserts duplicate username collisions return status 400 with specific error messages.
  - `test_tc_auth_01_registration_password_mismatch_rejected`: Confirms password confirmation discrepancies trigger validation errors.
  - `test_tc_auth_02_user_login_api_success_and_invalid`: Validates session authentication tokens and rejects invalid credentials.
  - `test_tc_auth_03_user_logout_api`: Confirms session termination and cache clearing.
  - `test_tc_sec_03_password_hashing`: Direct cryptographic check confirming passwords utilize PBKDF2 with SHA-256 (no plaintext storage).
  - `test_web_ui_auth_views`: Tests HTML template rendering and CSRF token presence for login/register pages.

### 2.2. Dataset Upload & Validation Engine (`tests/test_dataset_upload.py`)
- **Unit Test Count:** 112 tests (extensive boundary and parameterized matrix)
- **Component Under Test:** `datasets/validators.py`, `datasets/services.py`, `datasets/models.py`
- **Scope & Verified Behaviors:**
  - **File Format Whitelist (18 parameterized tests):** Strict acceptance of `.csv` and explicit rejection of `.json`, `.xlsx`, `.xls`, `.tsv`, `.parquet`, `.zip`, `.pdf`, `.png`, `.jpg`, `.exe`, `.py`, extensionless files, double extensions (`.csv.txt`, `.csv.json`), case variations, and trailing dots.
  - **Empty File Validation (5 parameterized tests):** Rejection of 0-byte files, space-only files, tab-only files, newline-only files, and mixed whitespace files with `The uploaded file is empty.`
  - **Header-Only CSV Validation (4 parameterized tests):** Detection and rejection of CSV files containing column names but 0 data rows.
  - **Malformed & Tokenization Errors (6 parameterized tests):** Detection of delimiter-only files, unnamed header columns (`Unnamed: 0`), ragged row dimensions, unclosed quotation marks, and multiline quote leaks.
  - **Physical Byte Boundaries (Issue #14):** Verification of exact file size checks up to the 10 MB ceiling (10,485,760 bytes) and rejection of files exceeding the limit.
  - **Filename Sanitization:** Path traversal character neutralization (`../../etc/passwd` sanitized to safe basenames).

### 2.3. Dataset Profiling & Edge Cases (`tests/test_dataset_preview.py`)
- **Unit Test Count:** 37 tests
- **Component Under Test:** `datasets/services.py` (`profile_dataset`, `clean_for_json`), `datasets/views.py`
- **Scope & Verified Behaviors:**
  - **Descriptive Statistics:** Accurate computation of mean, median, standard deviation, variance, minimum, maximum, and quartile thresholds for numeric series.
  - **Categorical Profiling:** Unique count, mode identification, and frequency distribution calculations.
  - **Extreme Data Edge Cases:** Single-row datasets, single-column datasets, single-cell datasets, 100% duplicate datasets, and 0-variance constant columns.
  - **Missing Value Patterns:** Columns with 0%, partial, and 100% missing values across numeric and categorical types.
  - **JSON Serialization Integrity (Issue #19):** Special value sanitization converting `inf`, `-inf`, and `NaN` into JSON-compliant representations without runtime exceptions.
  - **Cross-User Preview Isolation:** Verification that unauthorized preview requests return 404/403.

### 2.4. Data Preprocessing & Feature Pipeline (`tests/test_preprocessing.py`)
- **Unit Test Count:** 10 tests
- **Component Under Test:** `datasets/preprocessing.py`
- **Scope & Verified Behaviors:**
  - **Duplicate Removal:** Deduplication of repeated rows without index corruption.
  - **Imputation Strategies:** Mean, median, and mode imputation applied specifically to missing cells without modifying observed values.
  - **Categorical Encoding:** One-Hot Encoding and Ordinal Label Encoding transformation fidelity.
  - **Feature Scaling:** `StandardScaler` (zero mean, unit variance) and `MinMaxScaler` (bounded [0, 1]) mathematical scaling accuracy.
  - **Data Leakage Defense:** Separate fitting on training splits and transformation on validation/test splits.
  - **Feature Selection:** Column subset extraction and target array partitioning.

### 2.5. Machine Learning Engine & Evaluation Metrics (`tests/test_model_training_and_evaluation.py`)
- **Unit Test Count:** 21 tests
- **Component Under Test:** `experiments/ml_engine.py`, `experiments/services.py`, `experiments/views.py`
- **Scope & Verified Behaviors:**
  - **11 Model Implementations:**
    - *Classification:* Logistic Regression, Decision Tree Classifier, Random Forest Classifier, K-Nearest Neighbors, Support Vector Classifier (SVC), Gaussian Naive Bayes.
    - *Regression:* Linear Regression, Decision Tree Regressor, Random Forest Regressor, Support Vector Regressor (SVR), Gradient Boosting Regressor.
  - **Metric Calculation Precision:**
    - Classification: Accuracy, Precision, Recall, F1-Score, Confusion Matrix, ROC-AUC.
    - Regression: Mean Absolute Error (MAE), Mean Squared Error (MSE), Root Mean Squared Error (RMSE), Coefficient of Determination (R²).
  - **Hyperparameter Whitelisting:** Parameter type validation and prevention of invalid parameter injections.
  - **Metric Explanations (Issue #20):** Dynamic textual interpretation of evaluation metrics tailored to the problem domain.
  - **Export Generation:** Serialized report output in CSV and JSON formats.

---

## 3. Unit Test Execution Summary Table

| Test Suite Module | Target Component | Unit Tests | Passed | Failed | Pass Rate |
|---|---|:---:|:---:|:---:|:---:|
| `test_authentication.py` | User Account & Auth Service | 7 | 7 | 0 | 100% |
| `test_dataset_upload.py` | CSV Ingestion & Byte Validator | 112 | 112 | 0 | 100% |
| `test_dataset_preview.py` | Profiling & Statistical Engine | 37 | 37 | 0 | 100% |
| `test_preprocessing.py` | Transformation & Pipeline Engine | 10 | 10 | 0 | 100% |
| `test_model_training_and_evaluation.py` | Scikit-Learn Engine & Metrics | 21 | 21 | 0 | 100% |
| **Total Unit Tests** | | **187** | **187** | **0** | **100%** |

---

## 4. Conclusion & Readiness

The unit test suite comprehensively exercises all critical algorithmic components, boundary conditions, and business rules. With 100% pass rate across 187 unit specifications, the unit testing criteria for academic evaluation are completely satisfied.

