# Sprint 2 Demonstration Video Script (2 Minutes)

**Target Duration:** 120 seconds  
**Objective:** Comprehensive demonstration of the complete end-to-end Web-Based ML Model Evaluator platform  
**Deliverable per Part 2 Instructions:** 2-minute video uploaded to repository.  

---

### Scene-by-Scene Shot List & Narration

#### Scene 1: Authentication & Platform Overview (0:00 - 0:20)
- **Visual:** Browser at `http://127.0.0.1:8000/auth/login/`. User signs in as `researcher`.
- **Narration:**
  > "Welcome to the final demonstration of the Web-Based ML Model Evaluator by Team 16. Our platform provides a zero-code machine learning workflow with complete transparency. We begin by logging into our secure authenticated session."

#### Scene 2: Dataset Upload & Profiling (0:20 - 0:40)
- **Visual:** Upload `demo_dataset.csv`. Click **Preview & Profile**.
- **Narration:**
  > "We upload our employee promotion dataset. The validation engine verifies the CSV structure and size limits. Opening the profile view, we immediately inspect the first ten rows, inferred column data types, missing value ratios, and distribution statistics."

#### Scene 3: Preprocessing & Feature Selection (0:40 - 1:00)
- **Visual:** Click **Configure Preprocessing**. Select `promoted` as target variable, check features `age`, `income`, `experience_years`, `education`. Choose `StandardScaler` and `One-Hot Encoding`. Click **Apply Preprocessing**.
- **Narration:**
  > "In the preprocessing module, we select our target variable, choose input features, and configure one-hot encoding and standard scaling. Transformations are fit strictly on the 80% training split, completely eliminating data leakage risks."

#### Scene 4: Model Selection & Training (1:00 - 1:25)
- **Visual:** Click **Train Model**. Select **Classification**, choose **Random Forest Classifier**, set `n_estimators = 100`, click **Fit Model & Evaluate**.
- **Narration:**
  > "Next, we select our algorithm from the validated model registry. We choose Random Forest with 100 estimators. The training engine fits the model, records execution time, and generates predictions on the test dataset without executing arbitrary external code."

#### Scene 5: Evaluation Results & Comparison (1:25 - 1:50)
- **Visual:** Results page displays Accuracy, Precision, Recall, F1 score, and Confusion Matrix. Return to history, select Random Forest and Logistic Regression, click **Compare Selected**.
- **Narration:**
  > "The evaluation engine immediately presents classification metrics—accuracy, weighted precision, recall, F1 score, and a confusion matrix. Moving to experiment comparison, we place Random Forest and Logistic Regression head-to-head, where our system highlights the top-performing model."

#### Scene 6: Result Export & Verification (1:50 - 2:00)
- **Visual:** Click **Export JSON** and **Export CSV**. Show downloaded files in browser.
- **Narration:**
  > "Finally, evaluation results and prediction samples are exported in machine-readable JSON and CSV formats. All 26 SRS requirements and 48 automated tests are fully verified. Thank you!"

