# Pull Request & Commit Manifest

This document contains the exact commit messages, pull request titles, descriptions, and verification evidence for each feature task, ready for team members to raise and the repository owner to review.

---

## PR 1: Dataset Upload and Validation (Issue #1)

- **Feature Branch:** `feature/issue-1-dataset-upload-validation`
- **Target Branch:** `main`
- **Assignee / Author:** `@vasanthreddy121`
- **Proposed Commit Message:**
  ```text
  feat(datasets): implement dataset upload and validation (closes #1)

  - Add Django project ml_evaluator and datasets app
  - Implement Dataset model with storage cleanup on deletion
  - Add robust CSV validation (MIME, size <= 10MB, tabular structure, UTF-8)
  - Add filename sanitization against path traversal (TC-SEC-04)
  - Provide REST API endpoint POST /api/datasets/upload/
  - Provide interactive upload web UI
  - Add 12 automated tests in tests/test_dataset_upload.py
  ```
- **PR Description:**
  ```markdown
  ### Summary
  Implements CSV dataset upload, storage, and validation according to SRS ML-EVAL-F-010, ML-EVAL-F-011, and ML-EVAL-SR-003.

  ### Acceptance Criteria Satisfied
  - [x] Supports CSV uploads with automatic format and extension validation.
  - [x] Enforces 10 MB maximum file size limit (`TC-SEC-04`).
  - [x] Rejects empty, whitespace-only, malformed, and header-only CSVs with clear HTTP 400 error messages (`TC-DATA-02`).
  - [x] Sanitizes filenames to eliminate directory traversal risks.
  - [x] Automatically cleans up disk storage when Dataset instances are deleted.
  - [x] Verified with 12 automated unit and integration tests.

  ### Linked Issue
  Closes #1
  ```

---

## PR 2: Dataset Preview and Profiling (Issue #2)

- **Feature Branch:** `feature/issue-2-dataset-preview-profiling`
- **Target Branch:** `main`
- **Assignee / Author:** `@vasanthreddy121`
- **Proposed Commit Message:**
  ```text
  feat(datasets): implement dataset preview and profiling (closes #2)

  - Implement profile_dataset service in datasets/services.py
  - Compute row/col counts, column dtypes, missing value counts, and duplicates
  - Calculate five-number summary statistics for numeric and categorical features
  - Add REST API endpoint GET /api/datasets/{id}/preview/
  - Add interactive dataset profiling web view
  - Enforce cross-user access isolation (TC-SEC-01)
  - Add 5 automated tests in tests/test_dataset_preview.py
  ```
- **PR Description:**
  ```markdown
  ### Summary
  Implements dataset preview and profiling capabilities per SRS ML-EVAL-F-012, ML-EVAL-NF-001, and SAD 4.3.1.

  ### Acceptance Criteria Satisfied
  - [x] Returns first 10 rows preview of tabular data.
  - [x] Reports exact row and column dimensions.
  - [x] Identifies raw and simplified column data types.
  - [x] Detects missing value counts per column and total missing count.
  - [x] Computes duplicate row counts.
  - [x] Generates descriptive statistics (mean, std, min, 25%, 50%, 75%, max, unique, top, freq).
  - [x] Enforces object-level authorization preventing unauthorized cross-user access (`TC-SEC-01`).
  - [x] Verified with 5 automated unit and integration tests.

  ### Linked Issue
  Closes #2
  ```

---

## PR 3: Data Preprocessing and Feature Selection (Issue #3)

- **Feature Branch:** `feature/issue-3-preprocessing-feature-selection`
- **Target Branch:** `main`
- **Assignee / Author:** `@Sharustd`
- **Proposed Commit Message:**
  ```text
  feat(preprocessing): implement data preprocessing and feature selection (closes #3)

  - Implement PreprocessingPipeline in datasets/preprocessing.py
  - Support missing value imputation (mean, median, mode, drop)
  - Support duplicate row removal
  - Support categorical encoding (One-Hot, Label Encoding)
  - Support feature scaling (StandardScaler, MinMaxScaler)
  - Support feature selection, target selection, and configurable train-test split
  - Enforce strict prevention of data leakage by fitting scalers only on training data
  - Add REST API endpoint POST /api/datasets/{id}/preprocess/
  - Add interactive preprocessing web form
  - Add 10 automated tests in tests/test_preprocessing.py
  ```
- **PR Description:**
  ```markdown
  ### Summary
  Implements data preprocessing, cleaning, encoding, scaling, and feature selection per SRS ML-EVAL-F-013, ML-EVAL-F-014, and ML-EVAL-F-015.

  ### Acceptance Criteria Satisfied
  - [x] Handles missing values using mean, median, mode, or row dropping (`TC-DATA-04`).
  - [x] Automatically removes duplicate records when configured (`TC-DATA-04`).
  - [x] Supports one-hot and ordinal label encoding without datatype errors (`TC-DATA-05`).
  - [x] Supports StandardScaler and MinMaxScaler normalization (`TC-DATA-05`).
  - [x] Supports custom feature subset selection and target variable specification (`TC-DATA-06`).
  - [x] Strictly eliminates data leakage by fitting transformations solely on the training split.
  - [x] Verified with 10 automated unit and integration tests.

  ### Linked Issue
  Closes #3
  ```

---

## PR 4: Machine Learning Model Training and Prediction (Issue #4)

- **Feature Branch:** `feature/issue-4-model-training-prediction`
- **Target Branch:** `main`
- **Assignee / Author:** `@vasanthreddy121`
- **Proposed Commit Message:**
  ```text
  feat(experiments): implement machine learning model training and prediction (closes #4)

  - Create experiments app and Experiment persistence model
  - Implement MODEL_REGISTRY supporting 6 Classification and 5 Regression algorithms
  - Implement sanitized hyperparameter configuration preventing arbitrary code execution
  - Add training engine with execution time tracking and predictions generation
  - Add REST API endpoint POST /api/experiments/train/
  - Add interactive model training web form
  - Verified with automated tests across all 11 model families
  ```
- **PR Description:**
  ```markdown
  ### Summary
  Implements supervised machine learning model training and prediction pipelines per SRS ML-EVAL-F-020 to ML-EVAL-F-034 and SAD ML Engine.

  ### Acceptance Criteria Satisfied
  - [x] Classification models supported: Logistic Regression, Decision Tree, Random Forest, KNN, SVM, Naive Bayes (`TC-ML-02`).
  - [x] Regression models supported: Linear Regression, Decision Tree Regressor, Random Forest Regressor, SVR, Gradient Boosting (`TC-ML-03`).
  - [x] Whitelisted hyperparameter configuration prevents arbitrary Python code execution (`TC-SEC-06`).
  - [x] Generates predictions on held-out test data (`TC-TRAIN-02`).
  - [x] Controlled error reporting for invalid configurations without application termination (`TC-TRAIN-03`).
  - [x] Verified with automated tests across all 11 algorithms.

  ### Linked Issue
  Closes #4
  ```

---

## PR 5: Model Evaluation Metrics, Comparison, History and Export (Issue #5)

- **Feature Branch:** `feature/issue-5-evaluation-metrics-visualization`
- **Target Branch:** `main`
- **Assignee / Author:** `@munireddy8618`
- **Proposed Commit Message:**
  ```text
  feat(experiments): implement model evaluation metrics, comparison, history, and export (closes #5)

  - Compute classification metrics: Accuracy, Precision, Recall, F1, Confusion Matrix, ROC-AUC
  - Compute regression metrics: MAE, MSE, RMSE, R²
  - Implement multi-model comparison service with top-performer identification
  - Implement result export in valid CSV and JSON formats
  - Add REST API endpoints: /results/, /compare/, /export/
  - Add web UI for results inspection, experiment history, and comparison charts
  - Verified with automated tests
  ```
- **PR Description:**
  ```markdown
  ### Summary
  Implements comprehensive evaluation metrics, multi-model comparison, historical retrieval, and export per SRS ML-EVAL-F-032, F-033, F-040 to F-043.

  ### Acceptance Criteria Satisfied
  - [x] Computes full classification metrics suite (`TC-EVAL-01`).
  - [x] Computes full regression metrics suite (`TC-EVAL-02`).
  - [x] Side-by-side comparison of 2+ experiments with winner recommendation (`TC-COMP-01`).
  - [x] Historical experiment retrieval and filtering (`TC-HIST-01`).
  - [x] Downloadable result exports in JSON and CSV formats (`TC-EXP-01`).
  - [x] Verified with automated tests.

  ### Linked Issue
  Closes #5
  ```

---

## PR 6: CI Pipeline (GitHub Actions)

- **Feature Branch:** `feature/github-actions-ci`
- **Target Branch:** `main`
- **Proposed Commit Message:**
  ```text
  ci: add GitHub Actions workflow for linting, testing, and coverage

  - Configure .github/workflows/ci.yml
  - Run on pushes and PRs to main
  - Execute Django system checks, migration consistency, and pytest with coverage
  ```

