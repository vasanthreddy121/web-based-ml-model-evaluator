# Project Deviation Log

**Project:** Web-Based ML Model Evaluator (Team 16)  
**Date:** October 28, 2026  
**Reference Documents:** SRS v1.0 (04-09-2026), SAD v1.0 (04-10-2026), STP v1.0 (17-09-2026)

This document tracks all intentional adaptations, technical decisions, and deviations between the submitted engineering documents and the final implemented system, as required by the Mini-Project Part 2 specifications.

---

### Deviation 1: Local Development & CI Database Engine (ADR-004 Adaptation)
- **Planned in SAD:** Relational database specified as PostgreSQL or MySQL.
- **Actual Implementation:** SQLite used for local execution, developer onboarding, automated unit testing, and GitHub Actions CI; PostgreSQL/MySQL supported via standard Django environment configurations.
- **Reason:** SQLite is serverless, zero-configuration, bundled with Python, and enables continuous automated testing in GitHub Actions CI runners without requiring an external PostgreSQL daemon.
- **Impact:** Zero impact on application functionality or data models; all Django models, queries, and transactions behave identically.
- **Status:** **Resolved / Accepted**.

---

### Deviation 2: Documentation File Paths in README
- **Planned in Original README:** Hyperlinks pointed to generic filenames (`docs/SRS/SRS.pdf`, `docs/Software_Architecture_Design/Software_Architecture_Design.pdf`, `docs/STP/STP.pdf`).
- **Actual Files in Repository:** Files committed were `docs/SRS/SRS_TEAM_16_SE_MINIPROJECT.pdf`, `docs/docs/Software_Architecture_Design/SAD_TEAM_16_SE.pdf`, and `docs/Test_Plan/Web_Based_ML_Model_Evaluator_STP_TEAM16.pdf`.
- **Reason:** Preserving original submitted PDF files with exact submission filenames rather than deleting or renaming previously submitted work.
- **Impact:** Updated README hyperlinks to accurately point to the authentic submitted files.
- **Status:** **Resolved**.

---

### Deviation 3: Preprocessing Preview & Configuration Endpoint
- **Planned in SRS/SAD:** Preprocessing configuration was specified as part of the model training payload (`/api/experiments/train`).
- **Actual Implementation:** Added dedicated Preprocessing API (`POST /api/datasets/<id>/preprocess/`) and interactive Web UI (`/datasets/<id>/preprocess/`) in addition to training-time preprocessing.
- **Reason:** Allowed users and developers to test, inspect, and validate imputation, categorical encoding, scaling, and train/test splitting on their dataset before initiating model training.
- **Impact:** Positive enhancement improving transparency, modularity, and testability (`TC-DATA-04`, `TC-DATA-05`, `TC-DATA-06`).
- **Status:** **Implemented & Verified**.

---

### Deviation 4: Frontend Implementation Strategy (React vs Django Responsive UI)
- **Planned in SAD (Section 3.6):** "JavaScript / React or equivalent".
- **Actual Implementation:** Modern responsive server-rendered HTML5/CSS3 templates paired with REST API endpoints (DRF).
- **Reason:** Eliminates NodeJS build steps and frontend bundle complexity for academic evaluation, allowing the entire application to start with a single command (`python manage.py runserver`) while providing interactive web pages for upload, preview, preprocessing, training, results, history, and comparison.
- **Impact:** Seamless local evaluation; REST API endpoints remain completely accessible for external clients, frontend SPAs, or automated test suites.
- **Status:** **Accepted**.

---

### Deviation 5: Logistic Regression Solver Configuration & Warning Filter (SciPy 1.15+ Upstream Compatibility)
- **Observed Issue:** Terminal warning during model training: `OptimizeWarning: Unknown solver options: iprint`.
- **Root Cause Diagnosis:** Scikit-learn 1.5.2's `LogisticRegression(solver='lbfgs')` internally passes hardcoded options `options={"iprint": iprint, ...}` to `scipy.optimize.minimize(..., method="L-BFGS-B")`. In modern SciPy versions (SciPy 1.15+ / 1.18.1 installed), the deprecated Fortran option `iprint` was removed from SciPy's recognized options list, triggering an `OptimizeWarning`.
- **Implementation & Resolution:**
  1. Updated `MODEL_REGISTRY['classification']['logistic_regression']['default_params']` to set `solver='liblinear'` and added `'solver': str` to `param_types`.
  2. Wrapped `model_instance.fit` in `experiments/ml_engine.py` with a scoped `warnings.catch_warnings()` filter targeting `OptimizeWarning` with message regex `.*iprint.*` so even if users specify `solver='lbfgs'`, the upstream mismatch warning is cleanly suppressed without altering model convergence or evaluation metrics.
- **Impact:** Clean terminal output and zero test warnings across 48 automated test cases, preserving deterministic classification behavior.
- **Status:** **Resolved & Verified with Automated Regression Test**.

