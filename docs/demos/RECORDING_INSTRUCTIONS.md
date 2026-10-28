# Demonstration Video Recording Instructions

This guide provides step-by-step instructions for recording the working product demonstration videos required for Part 2 deliverables.

---

## 1. Setup & Environment

1. **Activate Environment and Start Server:**
   ```bash
   cd /home/vasanth-reddy/Documents/se/MINI/web-based-ml-model-evaluator
   source .venv/bin/activate
   python manage.py migrate
   python manage.py runserver
   ```
2. **Open Browser:**
   - Navigate to `http://127.0.0.1:8000/` in Google Chrome or Firefox.
   - Set browser zoom to 100% or 110% for readable text.
   - Clean up browser bookmarks/tabs for a clean recording presentation.

3. **Demo Dataset Location:**
   - Use [`docs/demos/demo_dataset.csv`](demo_dataset.csv) (synthetic employee promotion dataset with 50 rows, numeric and categorical columns).

---

## 2. Recording Tool Recommendations

- **Linux Tools:**
  - **OBS Studio:** `sudo apt-get install obs-studio` (Recommended for high quality 1080p 60fps capture).
  - **SimpleScreenRecorder:** `sudo apt-get install simplescreenrecorder` (Lightweight and easy to use).
  - **GNOME Screen Recorder:** Built-in shortcut `Ctrl + Alt + Shift + R` or `Print Screen` -> Record video.
- **Settings:**
  - Resolution: 1920x1080 (1080p) or 1280x720 (720p).
  - Audio: Ensure microphone is enabled and tested for clear audio narration.

---

## 3. Recording Procedure

### Sprint 1 Video (1 Minute)
1. Read the script: [`SPRINT_1_DEMO_SCRIPT.md`](SPRINT_1_DEMO_SCRIPT.md).
2. Start at `http://127.0.0.1:8000/`.
3. Try uploading a text file (shows error handling).
4. Upload `demo_dataset.csv` (shows upload success).
5. Click **Preview & Profile** (shows row counts, data types, missing values, duplicates, and statistics).
6. Target recording time: ~55–65 seconds.
7. Save video as `docs/demos/sprint_1_demo.mp4`.

### Sprint 2 Video (2 Minutes)
1. Read the script: [`SPRINT_2_DEMO_SCRIPT.md`](SPRINT_2_DEMO_SCRIPT.md).
2. Start at `http://127.0.0.1:8000/auth/login/` (shows authentication).
3. Upload `demo_dataset.csv` and view profiling.
4. Click **Configure Preprocessing** and apply transformations (StandardScaler, One-Hot Encoding, 80/20 split).
5. Click **Train Model**, select Random Forest Classifier, and submit.
6. Review evaluation metrics (Accuracy, Precision, Recall, F1, Confusion Matrix).
7. Train a second model (Logistic Regression).
8. Go to **Experiments**, select both models, and click **Compare Selected** (shows winner badge and comparison table).
9. Click **Export JSON** and **Export CSV** (shows exported files).
10. Target recording time: ~115–125 seconds.
11. Save video as `docs/demos/sprint_2_demo.mp4`.

---

## 4. Video File Verification

Per Part 2 instructions:
- Ensure the output `.mp4` or `.webm` file is placed in `docs/demos/` or linked in `README.md`.
- Verify the video file is non-empty and playable before uploading.

