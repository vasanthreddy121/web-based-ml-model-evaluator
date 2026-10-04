# Web-Based ML Model Evaluator

The **Web-Based ML Model Evaluator** is a web-based machine-learning experimentation platform designed to simplify and streamline the machine-learning workflow through an easy-to-use web interface.

The system allows users to upload datasets, perform preprocessing, select and configure machine-learning models, train and evaluate models, compare experiments, visualize results, maintain experiment history, and export evaluation results without requiring extensive programming effort.

---

## Project Documentation

The following documents describe the requirements, architecture, and testing strategy of the system:

- **[Software Requirements Specification (SRS)](docs/SRS/SRS.pdf)**
- **[Software Architecture Design](docs/Software_Architecture_Design/Software_Architecture_Design.pdf)**
- **[Software Test Plan (STP)](docs/STP/STP.pdf)**

---

# 1. Software Requirements Specification (SRS)

The **Software Requirements Specification (SRS)** for the **Web-Based ML Model Evaluator** defines the requirements, scope, functionality, interfaces, security requirements, quality attributes, and acceptance criteria of the proposed system. The system is designed as a web-based machine-learning experimentation platform that allows users to perform the major stages of an ML workflow through a web interface.

The primary purpose of the system is to reduce the programming effort required for routine machine-learning experimentation while maintaining transparency in dataset processing, model configuration, training, and evaluation. The intended users include students, researchers, developers, ML practitioners, project evaluators, and academic guides.

## Major Functions Defined in the SRS

The SRS specifies the following major functions:

1. **User Authentication**
   - User registration
   - Login and authentication
   - Session management

2. **Dataset Management**
   - Upload CSV datasets
   - Validate uploaded datasets
   - Preview datasets
   - Display basic statistics and dataset information
   - Detect missing values and duplicate records

3. **Data Preprocessing**
   - Handle missing values and duplicates
   - Encode categorical variables
   - Scale numerical features
   - Select input features and target variable
   - Configure training and testing data split

4. **Machine Learning Workflow**
   - Select classification or regression
   - Select suitable machine-learning models
   - Configure model hyperparameters
   - Train selected models
   - Generate predictions using test data

5. **Model Evaluation**
   - Calculate classification metrics such as accuracy, precision, recall, F1-score and other applicable metrics
   - Calculate regression metrics such as MAE, MSE, RMSE and R²
   - Display evaluation results

6. **Model Comparison and Visualization**
   - Compare multiple trained models or experiments
   - Present evaluation results using visualizations
   - Display model performance in an understandable format

7. **Experiment Management**
   - Store experiment configurations and results
   - Maintain experiment history
   - Retrieve previous experiments
   - Export evaluation results

The SRS also defines a layered architecture consisting of the web UI, Django/REST API, data-processing pipeline, ML engine, and persistence layer.

## Non-Functional Requirements

The SRS defines requirements related to performance, security, usability, reliability, maintainability, scalability, and portability. These include providing progress feedback during long-running training operations, protecting user data, enforcing authorization, validating uploaded files, handling invalid inputs without uncontrolled application termination, and providing a readable and accessible user interface.

## Security Requirements

The SRS identifies three main security objectives:

- **Confidentiality:** Protect user accounts, datasets, experiments, and stored model artifacts.
- **Integrity:** Prevent unauthorized modification of datasets, configurations, results, and experiment records.
- **Safe Processing:** Validate uploaded files and prevent arbitrary user-supplied code from being executed.

These objectives are supported by specific security requirements covering HTTPS/TLS, password hashing, upload validation, authorization, prevention of arbitrary code execution, and sanitized error messages.

## Acceptance Criteria

The SRS defines acceptance conditions such as successful registration and authentication, valid CSV upload and preview, dataset statistics, preprocessing and feature selection, support for classification and regression models, successful model training/testing, correct evaluation metrics, model comparison, visualization, experiment history, result export, and controlled handling of invalid inputs.

---

# 2. Software Architecture Design

The **Software Architecture Design** document describes the high-level architecture and technical organization of the Web-Based ML Model Evaluator.

The architecture is designed as a layered web-based system that separates presentation, API/business logic, data processing, machine-learning operations, and persistence responsibilities.

The major architectural layers include:

1. **Web/UI Layer**
   - Provides the user interface for authentication, dataset management, preprocessing configuration, model selection, training, evaluation, visualization, and experiment history.

2. **Django/REST API Layer**
   - Handles client requests and application workflows.
   - Provides authentication, authorization, validation, and communication between the frontend and backend services.

3. **Data Processing Layer**
   - Handles dataset validation, profiling, missing-value processing, duplicate handling, encoding, scaling, feature selection, and train/test splitting.

4. **Machine Learning Engine**
   - Provides classification and regression model selection.
   - Handles model configuration, training, prediction, and evaluation.

5. **Persistence Layer**
   - Stores user information, datasets, experiment configurations, evaluation results, and related application data.

The architecture document also describes the major system components, their responsibilities, interactions, data flow, security considerations, deployment considerations, and architectural decisions.

**[View the complete Software Architecture Design](docs/Software_Architecture_Design/Software_Architecture_Design.pdf)**

---

# 3. Software Test Plan (STP)

The **Software Test Plan (STP)** defines how the requirements specified in the SRS will be verified and validated. It provides the testing strategy, test scope, test environment, test data approach, test levels, test cases, security testing, non-functional testing, defect management, traceability, and acceptance testing.

The STP treats the Web-Based ML Model Evaluator as the **System Under Test (SUT)** and covers the complete workflow from authentication and dataset upload through preprocessing, model training, evaluation, comparison, visualization, history, and export.

## Main Testing Areas

The Test Plan covers:

- **Authentication Testing** – registration, login, logout, and session handling.
- **Dataset Testing** – valid/invalid CSV files, validation, preview, profiling, missing values, duplicates, and file restrictions.
- **Preprocessing Testing** – encoding, scaling, feature selection, target selection, and train/test splitting.
- **Machine Learning Testing** – classification and regression workflow selection, model selection, hyperparameter configuration, training, and prediction.
- **Evaluation Testing** – verification of classification and regression metrics using independent reference calculations where applicable.
- **Comparison and Visualization Testing** – verification that model comparisons and graphical results correspond to the underlying evaluation data.
- **Experiment History Testing** – verification of storage, retrieval, ownership, and deletion of experiment records.
- **Export Testing** – verification that evaluation results can be exported correctly.
- **Security Testing** – authentication, authorization, HTTPS/TLS, password protection, upload security, safe processing, and error handling.
- **Performance Testing** – verification of response-time requirements and training-progress feedback.
- **Usability and Accessibility Testing** – verification of readable, responsive, and keyboard-accessible interactions.
- **Reliability Testing** – verification that invalid inputs and training failures result in controlled errors rather than application crashes.

## Test Levels

The Test Plan uses four major levels of testing:

1. **Unit Testing** – testing individual functions and components such as validation, preprocessing, metric calculations, and services.
2. **Integration Testing** – testing communication between the frontend, API, data pipeline, ML engine, database, and storage.
3. **System Testing** – testing the complete application workflow from the user's perspective.
4. **Acceptance/UAT** – verifying that the final system satisfies the requirements and acceptance criteria defined in the SRS.

## Requirements Traceability

An important relationship between the SRS and Test Plan is the **Requirements Traceability Matrix (RTM)**. Each testable SRS requirement is mapped to one or more test cases.

For example:

| **SRS Requirement** | **Function** | **Test Case** |
|---|---|---|
| ML-EVAL-F-001 | User registration | TC-AUTH-01 |
| ML-EVAL-F-010 | CSV dataset upload | TC-DATA-01 |
| ML-EVAL-F-013 | Missing values/duplicates | TC-DATA-04 |
| ML-EVAL-F-021 | Classification models | TC-ML-02 |
| ML-EVAL-F-030 | Model training | TC-TRAIN-01 |
| ML-EVAL-F-032 | Classification metrics | TC-EVAL-01 |
| ML-EVAL-F-033 | Regression metrics | TC-EVAL-02 |
| ML-EVAL-F-040 | Model comparison | TC-COMP-01 |
| ML-EVAL-F-043 | Result export | TC-EXP-01 |
| ML-EVAL-NF-001 | Response-time requirement | TC-PERF-01 |
| ML-EVAL-NF-004 | Access isolation | TC-SEC-01 |
| ML-EVAL-SR-003 | Secure file upload | TC-SEC-04 |

The RTM therefore provides a direct connection between **what the system is required to do (SRS)** and **how those requirements will be verified (Test Plan)**. The project SRS already defines this requirement-to-test-case mapping structure.

---

# 4. Relationship Between SRS, Architecture Design, and Test Plan

The SRS, Software Architecture Design, and Test Plan are closely connected project documents.

### SRS → What the system must do

The **SRS** defines the functional and non-functional requirements, system scope, security requirements, quality attributes, and acceptance criteria.

### Architecture Design → How the system is structured

The **Software Architecture Design** translates the requirements into a technical architecture by defining the system layers, components, responsibilities, interfaces, data flow, and interactions between major subsystems.

### Test Plan → How the requirements will be verified

The **Test Plan** defines the testing strategy and test cases used to verify that the implemented system satisfies the requirements specified in the SRS.

The relationship can therefore be represented as:

```text
Software Requirements Specification
                │
                ▼
     Software Architecture Design
                │
                ▼
          Implementation
                │
                ▼
       Software Test Plan
                │
                ▼
       Verification & Validation
```

For example, if the SRS requires the system to calculate regression metrics such as MAE, MSE, RMSE and R², the Architecture Design identifies the ML evaluation component responsible for performing those calculations, while the Test Plan defines a corresponding test case that uses known predictions and target values and compares the application's results against independent reference calculations.

Similarly, if the SRS requires users to access only their own datasets and experiments, the Architecture Design defines the authorization and data-isolation mechanisms, while the Test Plan includes security tests in which one user attempts to access another user's resources.

Therefore, the three documents provide a complete engineering chain:

**Requirements → Architecture → Implementation → Testing**

Together, they provide a structured basis for designing, implementing, testing, and accepting the **Web-Based ML Model Evaluator**.
