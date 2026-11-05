# Branch Coverage Report

**Project:** Web-Based ML Model Evaluator (Team 16)  
**Date of Measurement:** November 5, 2026  
**Tool:** `pytest-cov 5.0.0` / `coverage 7.6.4` (Branch Coverage Mode: `branch = True`)  
**Execution Environment:** Linux Ubuntu x86_64, Python 3.12.3, Django 5.1.15  
**Core Application Branch Coverage:** **74.4% (201 / 270 conditional branches taken)**  
**Total Workspace Branch Coverage:** **75.2% (236 / 314 conditional branches taken)**  

---

## 1. Executive Summary

This report documents conditional and decision branch coverage for the **Web-Based ML Model Evaluator**. While standard statement coverage measures whether a given line was touched, branch coverage determines whether every boolean decision branch (`if`/`else`, ternary operators, `try`/`except` control flow) was traversed in both true and false directions.

Across the core applications, 201 of 270 conditional branch paths were actively taken during the 188 automated test runs, resulting in **74.4% branch coverage**. When combined with test harness validations, total branch coverage reaches **75.2%**.

### 1.1. Technical Resolution of Coverage Metrics (91.4% Combined vs. 75.2% Pure Branch)
When running `coverage report` with branch measurement enabled (`branch = True`), Python `coverage.py` outputs a single aggregate percentage in its `Cover` summary column. That figure is calculated using the official combined elements formula:
$$\text{Aggregate Elements Coverage} = \frac{\text{Statements Covered} + \text{Branches Taken}}{\text{Total Statements} + \text{Total Branches}} = \frac{2,311 + 236}{2,472 + 314} = \frac{2,547}{2,786} = 91.42\% \approx 91\%$$

In contrast, **pure standalone branch coverage** evaluates decision arcs strictly:
$$\text{Pure Branch Coverage (Total Workspace)} = \frac{\text{Branches Taken}}{\text{Total Branches}} = \frac{236}{314} = 75.16\% \approx 75.2\%$$
$$\text{Pure Branch Coverage (Core Applications)} = \frac{\text{Branches Taken}}{\text{Total Branches}} = \frac{201}{270} = 74.44\% \approx 74.4\%$$

Both figures are mathematically verified from `.coverage`: the **91%** figure represents total workspace combined statement-plus-branch coverage, while **75.2%** (workspace) and **74.4%** (core apps) represent pure decision-branch coverage.

---

## 2. Core Application Branch Coverage Breakdown

| Application Module | Total Branches | Fully Taken | Partially Taken / Untaken | Branch Coverage (%) |
|---|:---:|:---:|:---:|:---:|
| **Accounts Subsystem** | | | | |
| `accounts/serializers.py` | 10 | 7 | 3 | 70.0% |
| `accounts/views.py` | 20 | 14 | 6 | 70.0% |
| *Accounts Subtotal* | *30* | *21* | *9* | ***70.0%*** |
| **Datasets Subsystem** | | | | |
| `datasets/models.py` | 2 | 1 | 1 | 50.0% |
| `datasets/preprocessing.py` | 48 | 34 | 14 | 70.8% |
| `datasets/services.py` | 42 | 41 | 1 | 97.6% |
| `datasets/validators.py` | 24 | 18 | 6 | 75.0% |
| `datasets/views.py` | 20 | 17 | 3 | 85.0% |
| *Datasets Subtotal* | *136* | *111* | *25* | ***81.6%*** |
| **Experiments Subsystem** | | | | |
| `experiments/ml_engine.py` | 36 | 28 | 8 | 77.8% |
| `experiments/services.py` | 32 | 23 | 9 | 71.9% |
| `experiments/views.py` | 36 | 18 | 18 | 50.0% |
| *Experiments Subtotal* | *104* | *69* | *35* | ***66.3%*** |
| **Core Applications Grand Total** | **270** | **201** | **69** | ***74.4%*** |

---

## 3. Analysis of Decision Branches & Untaken Paths

The 69 partially taken or untaken branch arcs were analyzed to understand control flow behavior:

### 3.1. Datasets Preprocessing & Validation
- **`datasets/services.py` (97.6% branch coverage):** 41 of 42 branches taken. The single untaken branch corresponds to an OS-level file write failure fallback when persisting preview summary cache.
- **`datasets/validators.py` (75.0% branch coverage):** 18 of 24 branches taken. All negative validation paths (empty files, header-only CSVs, delimiters, unclosed quotes, unsupported extensions, size boundaries) are fully exercised. The remaining untaken branches handle rare character encoding fallbacks (`ISO-8859-1` when `utf-8-sig` fails).
- **`datasets/preprocessing.py` (70.8% branch coverage):** 34 of 48 branches taken. Untaken branches correspond to edge combinations of imputation strategies (e.g. `constant` fill value specified for categorical columns when `mode` is default).

### 3.2. Machine Learning Engine
- **`experiments/ml_engine.py` (77.8% branch coverage):** 28 of 36 branches taken. Core dispatch for all 11 algorithms and metric suites (classification and regression) are verified in both true and false paths. Untaken branches include hyperparameter boundary fallbacks (e.g. invalid `n_neighbors` value defaulting to 5).
- **`experiments/views.py` (50.0% branch coverage):** 18 of 36 branches taken. Views contain defensive branches for unauthenticated AJAX requests and corrupted training payloads that are preempted by Django REST Framework serializers and authentication middlewares.

---

## 4. Verification Command

```bash
# Execute test suite with branch instrumentation
coverage run --branch -m pytest

# Display branch coverage summary table
coverage report --include="accounts/*,datasets/*,experiments/*"
```

