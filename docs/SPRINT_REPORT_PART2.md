# Software Engineering Mini-Project Part 2 — Sprint Report

**Project:** Web-Based ML Model Evaluator  
**Team 16 Members:**
- Vasanth Kumar Reddy (PES2UG25CS829, `@vasanthreddy121`) — Team Lead / Repo Owner
- Munireddy S (PES2UG25CS813, `@munireddy8618`)
- Sharath H M (PES2UG25CS822, `@Sharustd`)
- Manoj M S (PES2UG25CS810)

**Date of Report:** October 28, 2026  
**Schedule Context:** Sprint 2 (October 26–30, 2026)

---

## 1. Backlog & Story Points Overview

Per Part 2 requirements, the project backlog was established in GitHub with 5 prioritized user stories mapped to SRS Functional Requirements, assigned to team members, and estimated at **26 total story points**:

| Issue # | User Story Title | Assignee | Story Points | Sprint | Implementation Status | Verified Automated Tests |
|:---:|---|---|:---:|:---:|:---:|:---:|
| **#1** | Implement dataset upload and validation | `@vasanthreddy121` | 5 | Sprint 1 | **Implemented & Verified** | 12 tests (`tests/test_dataset_upload.py`) |
| **#2** | Implement dataset preview and profiling | `@vasanthreddy121` | 3 | Sprint 1 | **Implemented & Verified** | 5 tests (`tests/test_dataset_preview.py`) |
| **#3** | Implement data preprocessing and feature selection | `@Sharustd` | 5 | Sprint 2 | **Implemented & Verified** | 10 tests (`tests/test_preprocessing.py`) |
| **#4** | Implement machine learning model training and prediction | `@vasanthreddy121` | 8 | Sprint 2 | **Implemented & Verified** | 12 tests (`tests/test_model_training_and_evaluation.py`) |
| **#5** | Implement model evaluation metrics and results visualization | `@munireddy8618` | 5 | Sprint 2 | **Implemented & Verified** | 13 tests (`tests/test_model_training_and_evaluation.py`) |
| **Bonus**| User Authentication & Cross-User Security | Team 16 | - | Core | **Implemented & Verified** | 7 tests (`tests/test_authentication.py`) |
| **Bonus**| End-to-End System Integration | Team 16 | - | Core | **Implemented & Verified** | 1 test (`tests/test_end_to_end_integration.py`) |

**Total Backlog Points:** 26 / 26 SP completed and verified with 48 automated tests.

---

## 2. Sprint 1 Execution Summary (October 19–23, 2026)

- **Target Goals:**
  - Initial scaffolding of Django 5.x architecture and project structure.
  - Deliver working dataset upload and validation pipeline (`Issue #1`).
  - Deliver dataset preview, statistical profiling, and schema analysis (`Issue #2`).
  - Prepare 1-minute working-product demonstration.
- **Outcomes:**
  - `Dataset` model, storage engine, and validators built with 10 MB limit and extension enforcement.
  - Interactive Web UI and REST API (`POST /api/datasets/upload/`, `GET /api/datasets/<id>/preview/`).
  - Cross-user authorization isolation established (`TC-SEC-01`).
  - 17 automated tests created and passing.
  - Sprint 1 1-minute demonstration script created at [`docs/demos/SPRINT_1_DEMO_SCRIPT.md`](demos/SPRINT_1_DEMO_SCRIPT.md).

---

## 3. Sprint 2 Execution Summary (October 26–30, 2026)

- **Target Goals:**
  - Data preprocessing pipeline with leakage prevention, imputation, encoding, scaling, and train/test split (`Issue #3`).
  - Complete ML Engine with 6 Classification and 5 Regression models, whitelisted parameter configuration, and deterministic training (`Issue #4`).
  - Evaluation Engine with full metric suites (Accuracy, Precision, Recall, F1, Confusion Matrix, ROC-AUC; MAE, MSE, RMSE, R²), multi-model comparison, and JSON/CSV export (`Issue #5`).
  - User Authentication, Registration, and Session management (`ML-EVAL-F-001` to `F-003`).
  - CI Pipeline via GitHub Actions (`.github/workflows/ci.yml`).
  - Comprehensive documentation, RTM, test reports, and 2-minute Sprint 2 demonstration script.
- **Outcomes:**
  - Preprocessing service (`PreprocessingPipeline`) implemented with zero data leakage.
  - Model registry supporting all 11 SRS-specified algorithms implemented and tested.
  - Model evaluation, multi-model comparison, and export services implemented and tested.
  - End-to-end integration test passing with 48 total tests and 85% code coverage.
  - Sprint 2 2-minute scene-by-scene demo script created at [`docs/demos/SPRINT_2_DEMO_SCRIPT.md`](demos/SPRINT_2_DEMO_SCRIPT.md).

---

## 4. GitHub Project Board Alignment

The Project Board columns should be updated as follows:
- **Backlog:** (Empty - all items implemented)
- **Ready:** (Empty)
- **In Progress:** (Empty)
- **In Review:**
  - Issue #1: `Implement dataset upload and validation` (PR description ready)
  - Issue #2: `Implement dataset preview and profiling` (PR description ready)
  - Issue #3: `Implement data preprocessing and feature selection` (PR description ready)
  - Issue #4: `Implement machine learning model training and prediction` (PR description ready)
  - Issue #5: `Implement model evaluation metrics and results visualization` (PR description ready)
  - CI Pipeline: `Add GitHub Actions CI workflow` (PR description ready)
- **Done:** (To be moved upon repository owner PR review and merge)

---

## 5. Deliverables & Demonstration Status

- **Codebase:** Fully functional web application running locally with Django, DRF, Pandas, and Scikit-learn.
- **Automated Tests:** 48 passing tests running in under 35 seconds.
- **CI Configuration:** Automated workflow ready in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).
- **Synthetic Dataset:** Reproducible demo dataset provided in [`docs/demos/demo_dataset.csv`](demos/demo_dataset.csv).
- **Video Demonstration Scripts:**
  - 1-Minute Sprint 1 Script: [`docs/demos/SPRINT_1_DEMO_SCRIPT.md`](demos/SPRINT_1_DEMO_SCRIPT.md)
  - 2-Minute Sprint 2 Shot List & Narration: [`docs/demos/SPRINT_2_DEMO_SCRIPT.md`](demos/SPRINT_2_DEMO_SCRIPT.md)
  - Screen Recording Setup Instructions: [`docs/demos/RECORDING_INSTRUCTIONS.md`](demos/RECORDING_INSTRUCTIONS.md)

