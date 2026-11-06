# Software Engineering Mini-Project Part 2 — Sprint Report

**Project:** Web-Based ML Model Evaluator  
**Team 16 Members:**
- Vasanth Kumar Reddy (PES2UG25CS829, `@vasanthreddy121`) — Team Lead / Repo Owner
- Munireddy S (PES2UG25CS813, `@munireddy8618`) — Core Developer / QA
- Sharath H M (PES2UG25CS822, `@Sharustd`) — Core Developer / UI & Security
- Manoj M S (PES2UG25CS810, `@ManuManu2007`) — Core Developer / UX & Accessibility

**Date of Initial Report:** October 28, 2026  
**Schedule Context:** Sprint 2 (October 26–30, 2026)  
**Last Updated (Final Delivery):** November 6, 2026  

---

## 1. Backlog & Story Points Overview (Sprint 2 Baseline)

Per Part 2 requirements, the initial project backlog was established in GitHub with 5 prioritized user stories mapped to SRS Functional Requirements, assigned to team members, and estimated at **26 total story points**:

| Issue # | User Story Title | Assignee | Story Points | Sprint | Implementation Status | Verified Automated Tests (Sprint Baseline) |
|:---:|---|---|:---:|:---:|:---:|:---:|
| **#1** | Implement dataset upload and validation | `@vasanthreddy121` | 5 | Sprint 1 | **Implemented & Verified** | 12 tests (`tests/test_dataset_upload.py`) |
| **#2** | Implement dataset preview and profiling | `@vasanthreddy121` | 3 | Sprint 1 | **Implemented & Verified** | 5 tests (`tests/test_dataset_preview.py`) |
| **#3** | Implement data preprocessing and feature selection | `@Sharustd` | 5 | Sprint 2 | **Implemented & Verified** | 10 tests (`tests/test_preprocessing.py`) |
| **#4** | Implement machine learning model training and prediction | `@vasanthreddy121` | 8 | Sprint 2 | **Implemented & Verified** | 12 tests (`tests/test_model_training_and_evaluation.py`) |
| **#5** | Implement model evaluation metrics and results visualization | `@munireddy8618` | 5 | Sprint 2 | **Implemented & Verified** | 13 tests (`tests/test_model_training_and_evaluation.py`) |
| **Bonus**| User Authentication & Cross-User Security | Team 16 | - | Core | **Implemented & Verified** | 7 tests (`tests/test_authentication.py`) |
| **Bonus**| End-to-End System Integration | Team 16 | - | Core | **Implemented & Verified** | 1 test (`tests/test_end_to_end_integration.py`) |

**Sprint 2 Completed Backlog Points:** 26 / 26 SP completed and verified with 48 automated tests (as of October 28, 2026).

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

## 4. GitHub Project Board Alignment (Historical Sprint 2 State)

The Project Board columns at the conclusion of Sprint 2:
- **Backlog:** (Empty - all initial items implemented)
- **Ready:** (Empty)
- **In Progress:** (Empty)
- **In Review:**
  - Issue #1: `Implement dataset upload and validation` (PR description ready)
  - Issue #2: `Implement dataset preview and profiling` (PR description ready)
  - Issue #3: `Implement data preprocessing and feature selection` (PR description ready)
  - Issue #4: `Implement machine learning model training and prediction` (PR description ready)
  - Issue #5: `Implement model evaluation metrics and results visualization` (PR description ready)
  - CI Pipeline: `Add GitHub Actions CI workflow` (PR description ready)
- **Done:** (Moved upon repository owner PR review and merge via PR #6)

---

## 5. Deliverables & Demonstration Status (Sprint Baseline vs. Current)

- **Codebase:** Fully functional web application running locally with Django, DRF, Pandas, and Scikit-learn.
- **Automated Tests:**
  - *Sprint 2 Historical Baseline (October 28, 2026):* 48 passing tests in ~15.16 seconds.
  - *Current Verified Suite (Final Delivery):* **188 passing tests** (187 unit/component tests + 1 end-to-end workflow test, 0 failures, 0 errors, 2 warnings) running in ~43.27 seconds.
- **CI Configuration:** Automated workflow in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) verifying all PRs and commits.
- **Synthetic Dataset:** Reproducible demo dataset provided in [`docs/demos/demo_dataset.csv`](demos/demo_dataset.csv).
- **Video Demonstration Scripts:**
  - 1-Minute Sprint 1 Script: [`docs/demos/SPRINT_1_DEMO_SCRIPT.md`](demos/SPRINT_1_DEMO_SCRIPT.md)
  - 2-Minute Sprint 2 Shot List & Narration: [`docs/demos/SPRINT_2_DEMO_SCRIPT.md`](demos/SPRINT_2_DEMO_SCRIPT.md)
  - Screen Recording Setup Instructions: [`docs/demos/RECORDING_INSTRUCTIONS.md`](demos/RECORDING_INSTRUCTIONS.md)

---

## 6. Post-Sprint Refinement & Full Backlog Delivery (61 Story Points, 20 Issues, 5 PRs)

Following the initial Sprint 2 milestone, Team 16 conducted a comprehensive refinement phase to address edge cases, boundary testing, frontend accessibility, UX enhancements, and evaluation metric explanations. 

The complete project backlog expanded from the initial 5 stories (26 SP) to **20 prioritized GitHub issues** totaling **61 story points**. All issues were assigned, implemented across feature branches, reviewed through Pull Requests, and merged into `main` by the repository owner (`@vasanthreddy121`).

### 6.1. Complete 20-Issue Backlog & Story Point Distribution

| Issue # | Title | Assignee | Story Points | Closing PR | Verified Implementation Scope |
|:---:|---|---|:---:|:---:|---|
| **#1** | Implement dataset upload and validation | `@vasanthreddy121` | 5 | PR #6 | CSV upload endpoint, format whitelist, 10MB size ceiling |
| **#2** | Implement dataset preview and profiling | `@vasanthreddy121` | 3 | PR #6 | Summary statistics, missing value analysis, column typing |
| **#3** | Implement data preprocessing and feature selection | `@vasanthreddy121` | 5 | PR #6 | Imputation, encoding, scaling, leakage prevention |
| **#4** | Implement ML model training and prediction | `@vasanthreddy121` | 8 | PR #6 | 11 ML models (6 classification, 5 regression), model registry |
| **#5** | Implement model evaluation metrics & visualization | `@vasanthreddy121` | 5 | PR #6 | Metric calculations, confusion matrix, JSON/CSV exports |
| **#7** | Improve dashboard layout and responsive spacing | `@ManuManu2007` | 2 | PR #25 | CSS Grid layout, responsive card padding, mobile alignment |
| **#8** | Add clear empty states to dashboard & datasets | `@ManuManu2007` | 2 | PR #25 | User guidance for zero-dataset / zero-experiment states |
| **#9** | Improve navigation consistency across pages | `@ManuManu2007` | 2 | PR #25 | Active breadcrumbs, navbar consistency, contextual links |
| **#10**| Improve form labels and inline help text | `@ManuManu2007` | 2 | PR #25 | ARIA accessibility labels, input helper text, validation hints |
| **#11**| Check and improve basic frontend accessibility | `@Sharustd` | 3 | PR #23 | Keyboard navigation, focus states, WCAG contrast compliance |
| **#12**| Add tests for unsupported dataset file formats | `@munireddy8618` | 2 | PR #22 | Parameterized tests rejecting `.json`, `.xlsx`, `.zip`, `.exe` |
| **#13**| Test empty and malformed CSV upload cases | `@munireddy8618` | 3 | PR #22 | 0-byte, whitespace-only, delimiter-only, ragged-row checks |
| **#14**| Test dataset upload size-limit boundaries | `@munireddy8618` | 2 | PR #22 | Exact 10MB byte-boundary tests (10,485,760 bytes) |
| **#15**| Add dataset profiling edge-case tests | `@munireddy8618` | 3 | PR #22 | Single-row, 100% duplicate, all-missing, constant columns |
| **#16**| Document dataset upload & validation behavior | `@Sharustd` | 2 | PR #23 | Markdown documentation of validation rules and API specs |
| **#17**| Improve evaluation metric explanations on results | `@Sharustd` | 2 | PR #23 | Contextual educational explanations for precision, recall, F1 |
| **#18**| Improve confusion matrix labels and readability | `@Sharustd` | 2 | PR #23 | True/Predicted label headers, contrast shading, matrix UI |
| **#19**| Improve prediction table readability | `@Sharustd` | 2 | PR #23 | Truncation, formatted decimals, styled prediction chips |
| **#20**| Add regression metric display tests | `@vasanthreddy121` | 3 | PR #24 | MAE, MSE, RMSE, R² UI and API display verification |
| **#21**| Verify CSV and JSON result export contents | `@vasanthreddy121` | 3 | PR #24 | Download header checks, schema fidelity, export parsing |
| **Total**| **20 Prioritized Backlog Issues** | **Team 16** | **61 SP** | **5 PRs** | **188 Automated Tests Verified in CI** |

### 6.2. Pull Request & Team Contribution Evidence

All pull requests were created on dedicated feature branches, verified by GitHub Actions CI, and formally reviewed and merged by the repository owner (`@vasanthreddy121`):

1. **PR #6 (`feature/issue-1-dataset-upload-validation`):** Core application implementation covering Issues #1–#5 (26 SP) by `@vasanthreddy121`.
2. **PR #22 (`feature/munireddy-dataset-validation-tests`):** Dataset validation edge cases, boundary testing, and profiling robustness covering Issues #12–#15 (10 SP) by `@munireddy8618`.
3. **PR #23 (`feature/sharath-results-ui-accessibility`):** Accessibility improvements, metric explanations, confusion matrix UI, and documentation covering Issues #11, #16–#19 (11 SP) by `@Sharustd`.
4. **PR #24 (`fix/regression-metric-explanations`):** Regression metric display and export verification covering Issues #20–#21 (6 SP) by `@vasanthreddy121`.
5. **PR #25 (`feature/manu-dashboard-ui-improvements`):** Dashboard UI refinements, empty state banners, and form accessibility covering Issues #7–#10 (8 SP) by `@ManuManu2007`.

*Note on PR #25 Git Attribution:* Commits in PR #25 were authored by Manoj M S using his local workstation git config alias `udaypalaksh123 <udayuday02585@gmail.com>`. The pull request was formally submitted by Manoj M S via his verified GitHub account (`@ManuManu2007`), reviewed, and merged into `main` by the repository owner.
