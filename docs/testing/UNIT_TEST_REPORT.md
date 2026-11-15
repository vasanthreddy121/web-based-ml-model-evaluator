# Unit Testing Report

**Project:** Web-Based ML Model Evaluator (Team 16)  
**Date of Execution:** November 5, 2026  
**Test Runner:** `pytest 8.4.2` with `pytest-django 4.14.0`  
**Execution Environment:** Linux Ubuntu x86_64, Python 3.12.3, Django 5.1.15  
**Total Unit Tests:** **187**  
**Total Non-E2E Test Cases:** **187**  
**Passed:** **187 (100%)**  
**Failed / Errored:** **0**  
**Total Duration:** **~41.9 seconds**  

---

## 1. Executive Summary

This report documents the unit-level verification of individual components, services, utility functions, validators, and serializers across the **Web-Based ML Model Evaluator**. Unit tests isolate specific functional behaviors, test boundary values, validate edge-case input handling, and confirm that mathematical metric evaluations and preprocessing algorithms produce expected outcomes without side-effects.
This report documents the unit-level and component-level verification across the **Web-Based ML Model Evaluator**. The test suite is architected across two distinct execution tiers:

All 187 unit tests pass with zero failures and zero errors.
1. **Pure Isolated Unit Tests (Algorithmic & In-Memory):** Direct tests of functions, validators, data profiling mathematical routines, and scikit-learn model fitting executed strictly in memory without database persistence or HTTP middleware overhead.
2. **Component-Level Tests (API / Client / ORM Integration):** Tests verifying view logic, serializer validation, HTTP response status codes, session lifecycles, and Django ORM transactional behaviors using Django's `TestCase` and REST Framework's `APIClient` against an in-memory SQLite database.

All 187 non-E2E tests pass with zero failures and zero errors.

---

## 2. Unit Test Breakdown by Component
## 2. Test Architecture: Isolated Unit vs. Component-Level Tests

### 2.1. Authentication & Security Services (`tests/test_authentication.py`)
- **Unit Test Count:** 7 tests
| Test Suite Module | Target Component | Pure Isolated Unit Tests | Component / API / ORM Tests | Total Tests | Pass Rate |
|---|---|:---:|:---:|:---:|:---:|
| `test_authentication.py` | User Account & Auth Service | 1 | 6 | 7 | 100% |
| `test_dataset_upload.py` | CSV Ingestion & Byte Validator | 83 | 29 | 112 | 100% |
| `test_dataset_preview.py` | Profiling & Statistical Engine | 31 | 6 | 37 | 100% |
| `test_preprocessing.py` | Transformation & Pipeline Engine | 8 | 2 | 10 | 100% |
| `test_model_training_and_evaluation.py` | Scikit-Learn Engine & Metrics | 17 | 4 | 21 | 100% |
| **Total Non-E2E Tests** | | **140** | **47** | **187** | **100%** |

---

## 3. Component Breakdown & Verified Behaviors

### 3.1. Authentication & Security Services (`tests/test_authentication.py`)
- **Total Tests:** 7 tests (1 pure cryptographic unit test, 6 API/Client component tests)
- **Component Under Test:** `accounts/serializers.py`, `accounts/views.py`, Django `auth.models.User`
- **Scope & Verified Behaviors:**
  - `test_tc_auth_01_user_registration_api_success`: Verifies valid user payload creation, serialized JSON response, and status 201.
  - `test_tc_auth_01_registration_duplicate_username_rejected`: Asserts duplicate username collisions return status 400 with specific error messages.
  - `test_tc_auth_01_registration_password_mismatch_rejected`: Confirms password confirmation discrepancies trigger validation errors.
  - `test_tc_auth_02_user_login_api_success_and_invalid`: Validates session authentication tokens and rejects invalid credentials.
  - `test_tc_auth_03_user_logout_api`: Confirms session termination and cache clearing.
  - `test_tc_sec_03_password_hashing`: Direct cryptographic check confirming passwords utilize PBKDF2 with SHA-256 (no plaintext storage).
  - `test_web_ui_auth_views`: Tests HTML template rendering and CSRF token presence for login/register pages.
  - *Isolated Unit Test:* `test_tc_sec_03_password_hashing` performs a direct cryptographic assertion confirming passwords utilize PBKDF2 with SHA-256 (no plaintext storage).
  - *Component / API Tests (6 tests):* Registration API status 201 (`test_tc_auth_01_user_registration_api_success`), duplicate username collision 400 rejection, password confirmation mismatch handling, session login token verification (`test_tc_auth_02`), session logout invalidation (`test_tc_auth_03`), and HTML template rendering / CSRF token presence.

### 2.2. Dataset Upload & Validation Engine (`tests/test_dataset_upload.py`)
- **Unit Test Count:** 112 tests (extensive boundary and parameterized matrix)
### 3.2. Dataset Upload & Validation Engine (`tests/test_dataset_upload.py`)
- **Total Tests:** 112 tests (83 pure validator unit tests, 29 client/ORM component tests)
- **Component Under Test:** `datasets/validators.py`, `datasets/services.py`, `datasets/models.py`
- **Scope & Verified Behaviors:**
  - **File Format Whitelist (18 parameterized tests):** Strict acceptance of `.csv` and explicit rejection of `.json`, `.xlsx`, `.xls`, `.tsv`, `.parquet`, `.zip`, `.pdf`, `.png`, `.jpg`, `.exe`, `.py`, extensionless files, double extensions (`.csv.txt`, `.csv.json`), case variations, and trailing dots.
  - **Empty File Validation (5 parameterized tests):** Rejection of 0-byte files, space-only files, tab-only files, newline-only files, and mixed whitespace files with `The uploaded file is empty.`
  - **Header-Only CSV Validation (4 parameterized tests):** Detection and rejection of CSV files containing column names but 0 data rows.
  - **Malformed & Tokenization Errors (6 parameterized tests):** Detection of delimiter-only files, unnamed header columns (`Unnamed: 0`), ragged row dimensions, unclosed quotation marks, and multiline quote leaks.
  - **Physical Byte Boundaries (Issue #14):** Verification of exact file size checks up to the 10 MB ceiling (10,485,760 bytes) and rejection of files exceeding the limit.
  - **Filename Sanitization:** Path traversal character neutralization (`../../etc/passwd` sanitized to safe basenames).
  - *Isolated Unit Tests (83 tests):* Direct invocation of `validate_csv_file()` and `sanitize_filename()` with in-memory byte buffers:
    - Whitelist validation across 18 parameterized extensions (strict `.csv` acceptance; rejection of `.json`, `.xlsx`, `.zip`, `.exe`, etc.).
    - Empty file detection across 5 parameterized whitespace patterns (0 bytes, spaces, tabs, newlines).
    - Header-only CSV rejection (4 parameterized cases).
    - Malformed CSV tokenization detection (6 parameterized cases: delimiter-only, ragged rows, unclosed quotes).
    - Physical byte boundary validation at the 10 MB limit (10,485,760 bytes).
    - Path traversal regex sanitization stripping `../` basenames.
  - *Component / API Tests (29 tests):* Multipart form upload view POST requests, file persistence in media directory, model instance creation in `datasets_dataset`, and error response serialization.

### 2.3. Dataset Profiling & Edge Cases (`tests/test_dataset_preview.py`)
- **Unit Test Count:** 37 tests
### 3.3. Dataset Profiling & Edge Cases (`tests/test_dataset_preview.py`)
- **Total Tests:** 37 tests (31 pure algorithmic unit tests, 6 client/view component tests)
- **Component Under Test:** `datasets/services.py` (`profile_dataset`, `clean_for_json`), `datasets/views.py`
- **Scope & Verified Behaviors:**
  - **Descriptive Statistics:** Accurate computation of mean, median, standard deviation, variance, minimum, maximum, and quartile thresholds for numeric series.
  - **Categorical Profiling:** Unique count, mode identification, and frequency distribution calculations.
  - **Extreme Data Edge Cases:** Single-row datasets, single-column datasets, single-cell datasets, 100% duplicate datasets, and 0-variance constant columns.
  - **Missing Value Patterns:** Columns with 0%, partial, and 100% missing values across numeric and categorical types.
  - **JSON Serialization Integrity (Issue #19):** Special value sanitization converting `inf`, `-inf`, and `NaN` into JSON-compliant representations without runtime exceptions.
  - **Cross-User Preview Isolation:** Verification that unauthorized preview requests return 404/403.
  - *Isolated Unit Tests (31 tests):*
    - Descriptive statistics: mean, median, standard deviation, variance, min, max, quartile computation.
    - Categorical distributions: unique counts, mode calculation, frequency maps.
    - Extreme edge cases: 1-row, 1-column, single-cell datasets, 100% duplicate rows, zero-variance constant columns.
    - Missing value edge patterns: 0%, partial, and 100% missing values across numeric and string series.
    - JSON serialization sanitization (`clean_for_json`) converting `inf`, `-inf`, and `NaN` into compliant payloads.
  - *Component / API Tests (6 tests):* Authenticated preview GET endpoint, permission checks, cross-user isolation 403/404 response.

### 2.4. Data Preprocessing & Feature Pipeline (`tests/test_preprocessing.py`)
- **Unit Test Count:** 10 tests
### 3.4. Data Preprocessing & Feature Pipeline (`tests/test_preprocessing.py`)
- **Total Tests:** 10 tests (8 pure transformer unit tests, 2 client/view component tests)
- **Component Under Test:** `datasets/preprocessing.py`
- **Scope & Verified Behaviors:**
  - **Duplicate Removal:** Deduplication of repeated rows without index corruption.
  - **Imputation Strategies:** Mean, median, and mode imputation applied specifically to missing cells without modifying observed values.
  - **Categorical Encoding:** One-Hot Encoding and Ordinal Label Encoding transformation fidelity.
  - **Feature Scaling:** `StandardScaler` (zero mean, unit variance) and `MinMaxScaler` (bounded [0, 1]) mathematical scaling accuracy.
  - **Data Leakage Defense:** Separate fitting on training splits and transformation on validation/test splits.
  - **Feature Selection:** Column subset extraction and target array partitioning.
  - *Isolated Unit Tests (8 tests):*
    - In-memory DataFrame deduplication without row index corruption.
    - Imputation algorithms: mean, median, mode applied strictly to missing cells.
    - Categorical transformers: One-Hot Encoding and Ordinal Label Encoding.
    - Feature scalers: `StandardScaler` (zero mean, unit variance) and `MinMaxScaler` ([0, 1] range).
    - Leakage prevention: separate fit on training split and transform on test split.
    - Feature selection and target array partitioning.
  - *Component / API Tests (2 tests):* Preprocessing API endpoint and web form submission handling.

### 2.5. Machine Learning Engine & Evaluation Metrics (`tests/test_model_training_and_evaluation.py`)
- **Unit Test Count:** 21 tests
### 3.5. Machine Learning Engine & Evaluation Metrics (`tests/test_model_training_and_evaluation.py`)
- **Total Tests:** 21 tests (17 pure ML engine unit tests, 4 client/view component tests)
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
  - *Isolated Unit Tests (17 tests):*
    - Model instantiation and fitting across all 11 supported algorithms (6 classification, 5 regression).
    - Mathematical metric calculations: Accuracy, Precision, Recall, F1, Confusion Matrix, ROC-AUC; MAE, MSE, RMSE, R².
    - Whitelisted hyperparameter override validation and prevention of invalid parameter injections.
    - Metric explanations generator producing contextual textual insights.
  - *Component / API Tests (4 tests):* Experiment training view dispatch, asynchronous status reporting, comparative table endpoint, and CSV/JSON export downloads.

---

## 3. Unit Test Execution Summary Table
## 4. Conclusion & Academic Readiness

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

The test suite combines **140 pure isolated unit tests** exercising low-level algorithms and boundary constraints with **47 component-level tests** verifying API integration, ORM transactions, and security barriers. Together with the **1 end-to-end system integration test** (totaling 188 automated tests), the software testing strategy achieves comprehensive verification across every architectural tier.
