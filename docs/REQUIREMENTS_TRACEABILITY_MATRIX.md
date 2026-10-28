# Requirements Traceability Matrix (RTM)

**Project:** Web-Based ML Model Evaluator  
**Team:** Team 16  
**Status Date:** October 28, 2026  
**Baseline Documents:** SRS v1.0, Software Architecture Design (SAD) v1.0, Software Test Plan (STP) v1.0  

Status Legend:
- `A` = Accepted / Verified with Automated Tests
- `P` = Partially Implemented
- `N` = Not Started

---

| Requirement ID | Requirement Description | SAD Module Reference | Test Plan Reference | Implementation File(s) | Test File(s) | Verified Status |
|---|---|---|---|---|---|:---:|
| **ML-EVAL-F-001** | User Registration with validation | `AuthModule` / 4.1 | `TC-AUTH-01` | [`accounts/views.py`](../accounts/views.py), [`accounts/serializers.py`](../accounts/serializers.py) | [`tests/test_authentication.py`](../tests/test_authentication.py) | **A** |
| **ML-EVAL-F-002** | User Authentication (Login / Session) | `AuthModule` / 4.1 | `TC-AUTH-02` | [`accounts/views.py`](../accounts/views.py), [`accounts/serializers.py`](../accounts/serializers.py) | [`tests/test_authentication.py`](../tests/test_authentication.py) | **A** |
| **ML-EVAL-F-003** | User Logout / Session Termination | `AuthModule` / 4.1 | `TC-AUTH-03` | [`accounts/views.py`](../accounts/views.py) | [`tests/test_authentication.py`](../tests/test_authentication.py) | **A** |
| **ML-EVAL-F-010** | CSV Dataset Upload | `DatasetModule` / 4.2 | `TC-DATA-01` | [`datasets/views.py`](../datasets/views.py), [`datasets/models.py`](../datasets/models.py) | [`tests/test_dataset_upload.py`](../tests/test_dataset_upload.py) | **A** |
| **ML-EVAL-F-011** | Dataset Validation (mime, size, table) | `DatasetModule` / 4.2 | `TC-DATA-02` | [`datasets/validators.py`](../datasets/validators.py) | [`tests/test_dataset_upload.py`](../tests/test_dataset_upload.py) | **A** |
| **ML-EVAL-F-012** | Dataset Preview & Statistical Profiling | `DataPipeline` / 4.2 | `TC-DATA-03` | [`datasets/services.py`](../datasets/services.py), [`datasets/views.py`](../datasets/views.py) | [`tests/test_dataset_preview.py`](../tests/test_dataset_preview.py) | **A** |
| **ML-EVAL-F-013** | Missing Values & Duplicate Handling | `PreprocessingModule` / 4.2 | `TC-DATA-04` | [`datasets/preprocessing.py`](../datasets/preprocessing.py) | [`tests/test_preprocessing.py`](../tests/test_preprocessing.py) | **A** |
| **ML-EVAL-F-014** | Categorical Encoding & Feature Scaling | `PreprocessingModule` / 4.2 | `TC-DATA-05` | [`datasets/preprocessing.py`](../datasets/preprocessing.py) | [`tests/test_preprocessing.py`](../tests/test_preprocessing.py) | **A** |
| **ML-EVAL-F-015** | Feature & Target Selection, Split Ratio | `PipelineConfig` / 4.2 | `TC-DATA-06` | [`datasets/preprocessing.py`](../datasets/preprocessing.py), [`datasets/views.py`](../datasets/views.py) | [`tests/test_preprocessing.py`](../tests/test_preprocessing.py) | **A** |
| **ML-EVAL-F-020** | Classification & Regression Workflows | `ModelSelector` / 4.3 | `TC-ML-01` | [`experiments/ml_engine.py`](../experiments/ml_engine.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-F-021** | Classification Models (Logistic, Tree, Forest, KNN, SVM, Naive Bayes) | `ModelRegistry` / 4.3 | `TC-ML-02` | [`experiments/ml_engine.py`](../experiments/ml_engine.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-F-022** | Regression Models (Linear, Tree, Forest, SVR, Gradient Boosting) | `ModelRegistry` / 4.3 | `TC-ML-03` | [`experiments/ml_engine.py`](../experiments/ml_engine.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-F-023** | Hyperparameter Configuration & Sanitization | `ModelConfig` / 4.3 | `TC-ML-04` | [`experiments/ml_engine.py`](../experiments/ml_engine.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-F-030** | Supervised Model Training Pipeline | `TrainingEngine` / 4.4 | `TC-TRAIN-01` | [`experiments/ml_engine.py`](../experiments/ml_engine.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-F-031** | Test Set Prediction Generation | `TestingEngine` / 4.4 | `TC-TRAIN-02` | [`experiments/ml_engine.py`](../experiments/ml_engine.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-F-032** | Classification Metrics (Acc, Prec, Rec, F1, CM, ROC-AUC) | `EvaluationEngine` / 4.4 | `TC-EVAL-01` | [`experiments/ml_engine.py`](../experiments/ml_engine.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-F-033** | Regression Metrics (MAE, MSE, RMSE, R²) | `EvaluationEngine` / 4.4 | `TC-EVAL-02` | [`experiments/ml_engine.py`](../experiments/ml_engine.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-F-034** | Controlled Error Reporting on Training Failure | `TrainingEngine` / 4.4 | `TC-TRAIN-03` | [`experiments/ml_engine.py`](../experiments/ml_engine.py), [`experiments/views.py`](../experiments/views.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-F-040** | Multi-Model Experiment Comparison | `ComparisonModule` / 4.5 | `TC-COMP-01` | [`experiments/services.py`](../experiments/services.py), [`experiments/views.py`](../experiments/views.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-F-041** | Visualization of Results (Tables & Charts) | `VisualizationModule` / 4.5 | `TC-COMP-02` | [`templates/experiments/results.html`](../templates/experiments/results.html), [`templates/experiments/compare.html`](../templates/experiments/compare.html) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-F-042** | Experiment History & Persistence | `ExperimentModule` / 4.5 | `TC-HIST-01` | [`experiments/models.py`](../experiments/models.py), [`experiments/views.py`](../experiments/views.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-F-043** | Evaluation Result Export (CSV / JSON) | `ExportModule` / 4.5 | `TC-EXP-01` | [`experiments/services.py`](../experiments/services.py), [`experiments/views.py`](../experiments/views.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |
| **ML-EVAL-NF-001** | Sub-3s Metadata & Profiling Target | `DataPipeline` / 3.1 | `TC-PERF-01` | [`datasets/services.py`](../datasets/services.py) | [`tests/test_dataset_preview.py`](../tests/test_dataset_preview.py) | **A** |
| **ML-EVAL-NF-004** | Cross-User Access Isolation | `Auth/API` / 3.9 | `TC-SEC-01`, `TC-SEC-05` | [`datasets/views.py`](../datasets/views.py), [`experiments/views.py`](../experiments/views.py) | [`tests/test_dataset_preview.py`](../tests/test_dataset_preview.py), [`tests/test_end_to_end_integration.py`](../tests/test_end_to_end_integration.py) | **A** |
| **ML-EVAL-SR-003** | Secure Upload Validation (MIME, size, clean) | `DatasetModule` / 5.1 | `TC-SEC-04` | [`datasets/validators.py`](../datasets/validators.py) | [`tests/test_dataset_upload.py`](../tests/test_dataset_upload.py) | **A** |
| **ML-EVAL-SR-005** | No Arbitrary User Code Execution | `MLEngine` / 5.1 | `TC-SEC-06` | [`experiments/ml_engine.py`](../experiments/ml_engine.py) | [`tests/test_model_training_and_evaluation.py`](../tests/test_model_training_and_evaluation.py) | **A** |

---

### Verification Summary
- **Total testable requirements identified in SRS:** 26
- **Requirements fully implemented and verified (`A`):** 26 (100%)
- **Requirements partially implemented (`P`):** 0
- **Requirements not started (`N`):** 0

