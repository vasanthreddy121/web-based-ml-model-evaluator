# Unit Testing Report

**Project:** Web-Based ML Model Evaluator (Team 16)  
**Date of Execution:** November 5, 2026  
**Test Runner:** `pytest 8.4.2` with `pytest-django 4.14.0`  
**Execution Environment:** Linux Ubuntu x86_64, Python 3.12.3, Django 5.1.15  
**Total Non-E2E Test Cases:** **187**  
**Passed:** **187 (100%)**  
**Failed / Errored:** **0**  
**Total Duration:** **~41.9 seconds**  

---

## 1. Executive Summary

This report documents the unit-level and component-level verification across the **Web-Based ML Model Evaluator**. The test suite is architected across two distinct execution tiers:

1. **Pure Isolated Unit Tests (Algorithmic & In-Memory):** Direct tests of functions, validators, data profiling mathematical routines, and scikit-learn model fitting executed strictly in memory without database persistence or HTTP middleware overhead.
2. **Component-Level Tests (API / Client / ORM Integration):** Tests verifying view logic, serializer validation, HTTP response status codes, session lifecycles, and Django ORM transactional behaviors using Django's `TestCase` and REST Framework's `APIClient` against an in-memory SQLite database.

All 187 non-E2E tests pass with zero failures and zero errors.

---

## 2. Test Architecture: Isolated Unit vs. Component-Level Tests

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
  - *Isolated Unit Test:* `test_tc_sec_03_password_hashing` performs a direct cryptographic assertion confirming passwords utilize PBKDF2 with SHA-256 (no plaintext storage).
  - *Component / API Tests (6 tests):* Registration API status 201 (`test_tc_auth_01_user_registration_api_success`), duplicate username collision 400 rejection, password confirmation mismatch handling, session login token verification (`test_tc_auth_02`), session logout invalidation (`test_tc_auth_03`), and HTML template rendering / CSRF token presence.

### 3.2. Dataset Upload & Validation Engine (`tests/test_dataset_upload.py`)
- **Total Tests:** 112 tests (83 pure validator unit tests, 29 client/ORM component tests)
- **Component Under Test:** `datasets/validators.py`, `datasets/services.py`, `datasets/models.py`
- **Scope & Verified Behaviors:**
  - *Isolated Unit Tests (83 tests):* Direct invocation of `validate_csv_file()` and `sanitize_filename()` with in-memory byte buffers:
    - Whitelist validation across 18 parameterized extensions (strict `.csv` acceptance; rejection of `.json`, `.xlsx`, `.zip`, `.exe`, etc.).
    - Empty file detection across 5 parameterized whitespace patterns (0 bytes, spaces, tabs, newlines).
    - Header-only CSV rejection (4 parameterized cases).
    - Malformed CSV tokenization detection (6 parameterized cases: delimiter-only, ragged rows, unclosed quotes).
    - Physical byte boundary validation at the 10 MB limit (10,485,760 bytes).
    - Path traversal regex sanitization stripping `../` basenames.
  - *Component / API Tests (29 tests):* Multipart form upload view POST requests, file persistence in media directory, model instance creation in `datasets_dataset`, and error response serialization.

### 3.3. Dataset Profiling & Edge Cases (`tests/test_dataset_preview.py`)
- **Total Tests:** 37 tests (31 pure algorithmic unit tests, 6 client/view component tests)
- **Component Under Test:** `datasets/services.py` (`profile_dataset`, `clean_for_json`), `datasets/views.py`
- **Scope & Verified Behaviors:**
  - *Isolated Unit Tests (31 tests):*
    - Descriptive statistics: mean, median, standard deviation, variance, min, max, quartile computation.
    - Categorical distributions: unique counts, mode calculation, frequency maps.
    - Extreme edge cases: 1-row, 1-column, single-cell datasets, 100% duplicate rows, zero-variance constant columns.
    - Missing value edge patterns: 0%, partial, and 100% missing values across numeric and string series.
    - JSON serialization sanitization (`clean_for_json`) converting `inf`, `-inf`, and `NaN` into compliant payloads.
  - *Component / API Tests (6 tests):* Authenticated preview GET endpoint, permission checks, cross-user isolation 403/404 response.

### 3.4. Data Preprocessing & Feature Pipeline (`tests/test_preprocessing.py`)
- **Total Tests:** 10 tests (8 pure transformer unit tests, 2 client/view component tests)
- **Component Under Test:** `datasets/preprocessing.py`
- **Scope & Verified Behaviors:**
  - *Isolated Unit Tests (8 tests):*
    - In-memory DataFrame deduplication without row index corruption.
    - Imputation algorithms: mean, median, mode applied strictly to missing cells.
    - Categorical transformers: One-Hot Encoding and Ordinal Label Encoding.
    - Feature scalers: `StandardScaler` (zero mean, unit variance) and `MinMaxScaler` ([0, 1] range).
    - Leakage prevention: separate fit on training split and transform on test split.
    - Feature selection and target array partitioning.
  - *Component / API Tests (2 tests):* Preprocessing API endpoint and web form submission handling.

### 3.5. Machine Learning Engine & Evaluation Metrics (`tests/test_model_training_and_evaluation.py`)
- **Total Tests:** 21 tests (17 pure ML engine unit tests, 4 client/view component tests)
- **Component Under Test:** `experiments/ml_engine.py`, `experiments/services.py`, `experiments/views.py`
- **Scope & Verified Behaviors:**
  - *Isolated Unit Tests (17 tests):*
    - Model instantiation and fitting across all 11 supported algorithms (6 classification, 5 regression).
    - Mathematical metric calculations: Accuracy, Precision, Recall, F1, Confusion Matrix, ROC-AUC; MAE, MSE, RMSE, R².
    - Whitelisted hyperparameter override validation and prevention of invalid parameter injections.
    - Metric explanations generator producing contextual textual insights.
  - *Component / API Tests (4 tests):* Experiment training view dispatch, asynchronous status reporting, comparative table endpoint, and CSV/JSON export downloads.

---

## 4. Conclusion & Academic Readiness

The test suite combines **140 pure isolated unit tests** exercising low-level algorithms and boundary constraints with **47 component-level tests** verifying API integration, ORM transactions, and security barriers. Together with the **1 end-to-end system integration test** (totaling 188 automated tests), the software testing strategy achieves comprehensive verification across every architectural tier.
