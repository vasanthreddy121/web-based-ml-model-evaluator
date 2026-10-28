# Automated Test Execution Report

**Date of Execution:** October 28, 2026  
**Platform:** Linux (Ubuntu x86_64), Python 3.12.3  
**Frameworks:** Django 5.1.15, pytest 8.4.2, pytest-django 4.14.0, pytest-cov 5.0.0  
**Overall Result:** **PASSED (48 of 48 tests passed, 0 failures, 0 errors, 0 skipped, 0 warnings)**  
**Overall Coverage:** **85%** across core application modules  

---

## 1. Test Suite Summary

| Test File | Target Scope / Issue Mapping | Tests Run | Passed | Failed | Execution Time |
|---|---|:---:|:---:|:---:|:---:|
| [`tests/test_dataset_upload.py`](../tests/test_dataset_upload.py) | **Issue #1:** CSV Upload, Validation, Security (`TC-DATA-01`, `TC-DATA-02`, `TC-SEC-04`) | 12 | 12 | 0 | 1.59s |
| [`tests/test_dataset_preview.py`](../tests/test_dataset_preview.py) | **Issue #2:** Dataset Preview, Profiling, Stats, Access Control (`TC-DATA-03`, `TC-SEC-01`) | 5 | 5 | 0 | 1.84s |
| [`tests/test_preprocessing.py`](../tests/test_preprocessing.py) | **Issue #3:** Cleaning, Imputation, Encoding, Scaling, Leakage Prevention (`TC-DATA-04`, `TC-DATA-05`, `TC-DATA-06`) | 10 | 10 | 0 | 2.65s |
| [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **Issue #4 & #5:** 11 ML Models, Metrics, Comparison, Export, Web UI (`TC-ML-01` to `04`, `TC-TRAIN-01` to `03`, `TC-EVAL-01`/`02`, `TC-COMP-01`, `TC-EXP-01`) | 13 | 13 | 0 | 5.06s |
| [`tests/test_authentication.py`](../tests/test_authentication.py) | **Phase 6 Auth:** Registration, Login, Logout, Session, Hashing (`TC-AUTH-01` to `03`, `TC-SEC-03`) | 7 | 7 | 0 | 7.11s |
| [`tests/test_end_to_end_integration.py`](../tests/test_end_to_end_integration.py) | **Phase 7 Integration:** Complete end-to-end multi-user workflow across all subsystems | 1 | 1 | 0 | 1.25s |
| **Total** | | **48** | **48** | **0** | **~15.16s** |

---

## 2. Code Coverage Breakdown

```text
Name                                     Stmts   Miss  Cover
------------------------------------------------------------
accounts/__init__.py                         0      0   100%
accounts/admin.py                            1      0   100%
accounts/apps.py                             4      0   100%
accounts/migrations/__init__.py              0      0   100%
accounts/models.py                           1      0   100%
accounts/serializers.py                     41      3    93%
accounts/tests.py                            1      1     0%
accounts/urls.py                             3      0   100%
accounts/views.py                           65      5    92%
datasets/__init__.py                         0      0   100%
datasets/admin.py                            1      0   100%
datasets/apps.py                             4      0   100%
datasets/migrations/0001_initial.py          7      0   100%
datasets/migrations/__init__.py              0      0   100%
datasets/models.py                          20      0   100%
datasets/preprocessing.py                  111     19    83%
datasets/serializers.py                      7      0   100%
datasets/services.py                        74      6    92%
datasets/urls.py                             3      0   100%
datasets/validators.py                      63     13    79%
datasets/views.py                          138     28    80%
experiments/__init__.py                      0      0   100%
experiments/admin.py                         1      0   100%
experiments/apps.py                          4      0   100%
experiments/migrations/0001_initial.py       7      0   100%
experiments/migrations/__init__.py           0      0   100%
experiments/ml_engine.py                   117     13    89%
experiments/models.py                       23      1    96%
experiments/services.py                     76      8    89%
experiments/tests.py                         1      1     0%
experiments/urls.py                          3      0   100%
experiments/views.py                       152     45    70%
------------------------------------------------------------
TOTAL                                      928    143    85%
```

---

## 3. Verified STP Test Cases

- **TC-AUTH-01 (Registration):** Valid account registration grants access; duplicate usernames and mismatched passwords rejected.
- **TC-AUTH-02 (Authentication):** Valid login authenticates session; invalid credentials rejected.
- **TC-AUTH-03 (Session Logout):** Session terminated on logout; protected requests reflect unauthenticated context.
- **TC-DATA-01 (Upload):** Valid CSV accepted, metadata extracted, database record created.
- **TC-DATA-02 (Validation):** Empty files, non-CSV extensions, header-only CSVs, and malformed files rejected with HTTP 400.
- **TC-DATA-03 (Profiling):** Rows, column count, column dtypes, missing value counts, duplicate count, and descriptive statistics computed.
- **TC-DATA-04 (Missing/Duplicates):** Imputation (mean, median, mode) and duplicate removal applied without data loss.
- **TC-DATA-05 (Encoding/Scaling):** One-hot/label encoding and standard/min-max scaling executed without type errors.
- **TC-DATA-06 (Feature Selection):** Selected features and target partitioned according to test split ratio.
- **TC-ML-01 (Problem Types):** Classification and regression pipelines both supported and executable.
- **TC-ML-02 (Classification Models):** Logistic Regression, Decision Tree, Random Forest, KNN, SVM, and Naive Bayes trained and evaluated.
- **TC-ML-03 (Regression Models):** Linear Regression, Decision Tree Regressor, Random Forest Regressor, SVR, and Gradient Boosting Regressor trained and evaluated.
- **TC-ML-04 (Hyperparameters):** Whitelisted hyperparameter overrides applied and validated against parameter types.
- **TC-TRAIN-01 (Training):** Fitted model artifact generated within reasonable execution time.
- **TC-TRAIN-02 (Prediction):** Prediction count matches test set sample count.
- **TC-TRAIN-03 (Controlled Error):** Incompatible data/target combinations throw controlled validation errors rather than crashing the server.
- **TC-EVAL-01 (Classification Metrics):** Accuracy, precision, recall, F1-score, confusion matrix, and ROC-AUC verified against reference calculations.
- **TC-EVAL-02 (Regression Metrics):** MAE, MSE, RMSE, and R² verified against independent mathematical reference.
- **TC-COMP-01 (Comparison):** Multi-model comparison compiles comparative metrics; incompatible cross-type comparisons rejected.
- **TC-COMP-02 (Visualization):** Visual charts, distribution bars, and confusion matrices rendered in responsive UI.
- **TC-HIST-01 (History):** Historical experiments retrieved from database with full configurations and metrics.
- **TC-EXP-01 (Export):** Machine-readable evaluation results exported in valid CSV and JSON formats.
- **TC-SEC-01 / TC-SEC-05 (Isolation):** Object-level authorization prevents User B from accessing User A's datasets or experiments.
- **TC-SEC-03 (Password Hashing):** Passwords stored using PBKDF2 hash, never stored in plaintext.
- **TC-SEC-04 (Secure Upload):** 10 MB file ceiling enforced; path traversal characters sanitized from filenames.
- **TC-SEC-06 (No Code Execution):** Whitelisted model and parameter registry prevents arbitrary code execution.

