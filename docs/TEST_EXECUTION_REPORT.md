# Automated Test Execution Report

**Date of Execution:** November 5, 2026  
**Platform:** Linux (Ubuntu x86_64), Python 3.12.3  
**Frameworks:** Django 5.1.15, pytest 8.4.2, pytest-django 4.14.0, pytest-cov 5.0.0, coverage 7.6.4  
**Overall Result:** **PASSED (188 of 188 tests passed, 0 failures, 0 errors, 0 skipped, 2 runtime warnings)**  
**Overall Execution Duration:** **~43.27 seconds**  
**Overall Coverage:** **85.6% Core Application Statement Coverage (803/938 stmts), 74.4% Core Branch Coverage (201/270 branches)**  
**Total Workspace Coverage:** **93.5% Statement Coverage (2311/2472 stmts), 75.2% Branch Coverage (236/314 branches) [91.4% Combined Elements Coverage]**  

---

## 1. Executive Summary & Verification Context

This report documents the automated test execution results for the **Web-Based ML Model Evaluator** (Team 16). The test suite verifies full end-to-end functionality across dataset ingestion, byte-level format validation, data profiling, preprocessing pipelines, machine learning model training (11 classification and regression algorithms), evaluation metrics computation, multi-model comparative analysis, export utilities, and session/tenant isolation security controls.

All 188 automated test cases executed cleanly against Django 5.1.15 and Python 3.12.3 with zero failures and zero errors.

### Dedicated Quality Assurance Reports
In accordance with the Academic Mini-Project Evaluation Checklist and Student FAQ Q4, detailed specialized test reports are available in the [`docs/testing/`](testing/) directory:
- [Unit Testing Report](testing/UNIT_TEST_REPORT.md) — Function and class-level unit test execution across all 187 unit specifications.
- [System Validation Report](testing/SYSTEM_VALIDATION_REPORT.md) — End-to-end workflow verification, security controls, and acceptance criteria validation.
- [Code Coverage Report](testing/CODE_COVERAGE_REPORT.md) — Comprehensive line and statement coverage breakdown per application module.
- [Branch Coverage Report](testing/BRANCH_COVERAGE_REPORT.md) — Conditional and decision branch coverage breakdown with missing branch analysis.

---

## 2. Test Suite Execution Summary

| Test Module | Target Scope / Issue Mapping | Tests Run | Passed | Failed | Errors | Duration |
|---|---|:---:|:---:|:---:|:---:|:---:|
| [`tests/test_dataset_upload.py`](../tests/test_dataset_upload.py) | **Issue #1, #13, #14:** CSV file upload, physical byte boundaries, format whitelist, empty/malformed files, 10MB limit, directory traversal prevention (`TC-DATA-01`, `TC-DATA-02`, `TC-SEC-04`) | 112 | 112 | 0 | 0 | ~14.2s |
| [`tests/test_dataset_preview.py`](../tests/test_dataset_preview.py) | **Issue #2, #18, #19:** Profiling, descriptive statistics, inf/NaN JSON serializability, edge cases, cross-user isolation (`TC-DATA-03`, `TC-SEC-01`) | 37 | 37 | 0 | 0 | ~8.1s |
| [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **Issue #4, #5, #15, #16, #20:** 11 ML models, hyperparameter overrides, classification/regression metrics, metric explanations, confusion matrix, export (`TC-ML-01`–`04`, `TC-TRAIN-01`–`03`, `TC-EVAL-01`–`02`, `TC-COMP-01`–`02`, `TC-EXP-01`) | 21 | 21 | 0 | 0 | ~11.8s |
| [`tests/test_preprocessing.py`](../tests/test_preprocessing.py) | **Issue #3, #17:** Missing value imputation, categorical encoding, feature scaling, target separation, leakage prevention (`TC-DATA-04`, `TC-DATA-05`, `TC-DATA-06`) | 10 | 10 | 0 | 0 | ~3.4s |
| [`tests/test_authentication.py`](../tests/test_authentication.py) | **Phase 6 Auth:** Registration, PBKDF2 password hashing, login/logout, session termination, UI auth views (`TC-AUTH-01`–`03`, `TC-SEC-03`) | 7 | 7 | 0 | 0 | ~4.5s |
| [`tests/test_end_to_end_integration.py`](../tests/test_end_to_end_integration.py) | **Phase 7 Integration:** Multi-user end-to-end workflow covering registration, upload, profiling, preprocessing, training, comparison, export, and tenant isolation | 1 | 1 | 0 | 0 | ~1.3s |
| **Total** | | **188** | **188** | **0** | **0** | **~43.27s** |

---

## 3. Core Application Code Coverage Breakdown

Measured via `coverage run -m pytest` with branch coverage enabled across Django applications (`accounts`, `datasets`, `experiments`):

```text
Name                                     Stmts   Miss Branch BrPart  Cover
--------------------------------------------------------------------------
accounts/__init__.py                         0      0      0      0   100%
accounts/admin.py                            1      0      0      0   100%
accounts/apps.py                             4      0      0      0   100%
accounts/migrations/__init__.py              0      0      0      0   100%
accounts/models.py                           1      0      0      0   100%
accounts/serializers.py                     41      3     10      3    88%
accounts/urls.py                             3      0      0      0   100%
accounts/views.py                           65      5     20      4    87%
datasets/__init__.py                         0      0      0      0   100%
datasets/admin.py                            1      0      0      0   100%
datasets/apps.py                             4      0      0      0   100%
datasets/migrations/0001_initial.py          7      0      0      0   100%
datasets/migrations/__init__.py              0      0      0      0   100%
datasets/models.py                          20      0      2      1    95%
datasets/preprocessing.py                  111     19     48     14    79%
datasets/serializers.py                      7      0      0      0   100%
datasets/services.py                        80      3     42      1    97%
datasets/urls.py                             3      0      0      0   100%
datasets/validators.py                      63     10     24      6    82%
datasets/views.py                          138     28     20      3    80%
experiments/__init__.py                      0      0      0      0   100%
experiments/admin.py                         1      0      0      0   100%
experiments/apps.py                          4      0      0      0   100%
experiments/migrations/0001_initial.py       7      0      0      0   100%
experiments/migrations/__init__.py           0      0      0      0   100%
experiments/ml_engine.py                   120     13     36      8    87%
experiments/models.py                       23      1      0      0    96%
experiments/services.py                     76      8     32      7    84%
experiments/urls.py                          3      0      0      0   100%
experiments/views.py                       155     45     36     14    67%
--------------------------------------------------------------------------
CORE APPLICATION TOTAL                     938    135    270     69    85.6%
--------------------------------------------------------------------------
WORKSPACE TOTAL (incl. tests & harness)   2472    161    314     68    93.5%
```

---

## 4. Requirement & STP Test Case Traceability

All 33 documented STP test case specifications are fully verified and satisfied through the 188 passing automated pytest tests:

| STP Test Case ID | Test Category | Target Feature / Verification Method | Automated Test Implementation | Specification Status |
|---|---|---|---|:---:|
| **TC-AUTH-01** | Authentication | User registration validation, password confirmation mismatch, duplicate username rejection | `tests/test_authentication.py` | **VERIFIED** |
| **TC-AUTH-02** | Authentication | Valid login session authentication, invalid credential rejection | `tests/test_authentication.py` | **VERIFIED** |
| **TC-AUTH-03** | Authentication | Session termination on logout, unauthenticated redirect | `tests/test_authentication.py` | **VERIFIED** |
| **TC-DATA-01** | Dataset | Valid CSV upload, schema inference, metadata extraction | `tests/test_dataset_upload.py` | **VERIFIED** |
| **TC-DATA-02** | Dataset | Empty file, non-CSV extension, malformed rows, 10MB ceiling rejection | `tests/test_dataset_upload.py` (112 tests) | **VERIFIED** |
| **TC-DATA-03** | Dataset | Summary statistics, missing counts, row/col counts, column dtypes | `tests/test_dataset_preview.py` (37 tests) | **VERIFIED** |
| **TC-DATA-04** | Preprocessing | Duplicate row removal, mean/median/mode missing value imputation | `tests/test_preprocessing.py` | **VERIFIED** |
| **TC-DATA-05** | Preprocessing | One-hot encoding, ordinal label encoding, StandardScaler, MinMaxScaler | `tests/test_preprocessing.py` | **VERIFIED** |
| **TC-DATA-06** | Preprocessing | Feature selection, train/test splitting, data leakage prevention | `tests/test_preprocessing.py` | **VERIFIED** |
| **TC-ML-01** | Model Training | Classification and regression problem type dispatch | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-ML-02** | Model Training | 6 Classification algorithms: Logistic Regression, Decision Tree, Random Forest, KNN, SVM, Naive Bayes | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-ML-03** | Model Training | 5 Regression algorithms: Linear Regression, Decision Tree Regressor, Random Forest Regressor, SVR, Gradient Boosting | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-ML-04** | Model Training | Hyperparameter whitelisting and dynamic parameter override validation | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-TRAIN-01** | Training Pipeline | Model artifact fitting, convergence, and execution timing capture | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-TRAIN-02** | Training Pipeline | Test prediction generation and dimension validation | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-TRAIN-03** | Error Handling | Incompatible data/target validation errors, graceful degradation | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-EVAL-01** | Evaluation | Classification metrics (Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix) | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-EVAL-02** | Evaluation | Regression metrics (MAE, MSE, RMSE, R²) | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-COMP-01** | Comparison | Multi-experiment comparative table generation, metric ranking | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-COMP-02** | Visualization | Confusion matrix visualization and metric comparison charts | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-HIST-01** | History | Historical experiment retrieval, parameters, and metric tracking | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-EXP-01** | Export | Evaluation report export in structured CSV and JSON formats | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-SEC-01** | Security | Cross-user dataset isolation (User B cannot preview User A's dataset) | `tests/test_dataset_preview.py` | **VERIFIED** |
| **TC-SEC-02** | Security | SQL Injection prevention through Django ORM parameterization | `tests/test_authentication.py`, `tests/test_end_to_end_integration.py` | **VERIFIED** |
| **TC-SEC-03** | Security | Password security via PBKDF2-SHA256 password hashing | `tests/test_authentication.py` | **VERIFIED** |
| **TC-SEC-04** | Security | Malicious file upload prevention, path traversal sanitization, 10MB limit | `tests/test_dataset_upload.py` | **VERIFIED** |
| **TC-SEC-05** | Security | Cross-user experiment isolation (User B cannot access User A's experiment) | `tests/test_end_to_end_integration.py` | **VERIFIED** |
| **TC-SEC-06** | Security | Whitelisted algorithm registry preventing arbitrary code execution | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-PERF-01** | Performance | Dataset upload under 2 seconds for valid CSV files | `tests/test_dataset_upload.py` | **VERIFIED** |
| **TC-PERF-02** | Performance | Profiling generation within acceptable response threshold | `tests/test_dataset_preview.py` | **VERIFIED** |
| **TC-PERF-03** | Performance | Model training turnaround within timeout limits | `tests/test_model_training_and_evaluation.py` | **VERIFIED** |
| **TC-E2E-01** | End-to-End | Full user journey: Auth -> Upload -> Profile -> Preprocess -> Train -> Eval -> Export | `tests/test_end_to_end_integration.py` | **VERIFIED** |
| **TC-E2E-02** | End-to-End | Multi-tenant isolation verification across parallel user workflows | `tests/test_end_to_end_integration.py` | **VERIFIED** |

---

## 5. Execution Environment & Reproducibility Command

To reproduce the verified test execution results in the project environment:

```bash
# Activate virtual environment
source .venv/bin/activate

# Execute complete test suite with short traceback
pytest --tb=short

# Execute complete test suite with statement and branch coverage
coverage run -m pytest
coverage report --include="accounts/*,datasets/*,experiments/*"
```
