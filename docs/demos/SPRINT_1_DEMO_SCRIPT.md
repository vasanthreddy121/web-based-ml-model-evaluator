# Sprint 1 Demonstration Video Script (1 Minute)

**Target Duration:** 60 seconds  
**Objective:** Demonstrate working product outcome of Sprint 1 (Dataset Upload, Validation & Profiling)  
**Deliverable per Part 2 Instructions:** 1-minute video uploaded to repository.  

---

### Timeline & Narration

| Time | On-Screen Action | Spoken Narration | Visual Elements |
|:---:|---|---|---|
| **0:00 - 0:12** | Display browser open at `http://127.0.0.1:8000/`. Introduce the Web-Based ML Model Evaluator. | "Hello everyone, this is Team 16 presenting our Sprint 1 deliverable for the Web-Based ML Model Evaluator mini-project." | Dashboard header, Upload card |
| **0:12 - 0:25** | Drag/select `invalid_file.txt` and submit. Show the error banner: *"Unsupported file format. Only CSV files (.csv) are accepted."* | "First, we demonstrate our secure file validation engine. Uploading an invalid non-CSV file immediately triggers a controlled validation error, rejecting unsafe data." | Red error alert |
| **0:25 - 0:40** | Select `demo_dataset.csv` and click **Validate & Upload Dataset**. Show green success banner. | "Next, we upload a valid CSV dataset. The application sanitizes the filename, parses tabular structure, checks encoding, and registers the dataset in our catalog." | Green success alert, table row with #1 |
| **0:40 - 0:52** | Click **Preview & Profile**. Display the preview table, column datatypes, missing values count, and summary statistics. | "Navigating to dataset profiling, the system computes row counts, column types, missingness, duplicates, and five-number summary statistics—all under three seconds." | Overview cards, Preview table, Statistics table |
| **0:52 - 1:00** | Point out the REST API endpoint and wrap up. | "Sprint 1 delivers a robust data ingestion and profiling foundation, ready for Sprint 2 preprocessing and machine learning model training. Thank you!" | Browser view of `/api/datasets/1/preview/` |

---

### Expected Video Output Checklist
- [x] Clear audio commentary.
- [x] Video shows browser running live Django application on `localhost:8000`.
- [x] Demonstrates negative test (invalid upload rejected) and positive test (valid upload accepted).
- [x] Demonstrates statistical profiling and schema analysis.

