# Personelise Gym — Smart AI Gym Dashboard

A Streamlit-based personal workout tracking dashboard. The current application entry point is **`app.py`** (not `gym_dashboard.py`).

## What the app currently includes

- **Workout:** muscle-group exercise lists, exercise checklist, multi-set entry (weight and reps), duplicate-log confirmation, and workout completion tracking.
- **Workout tools:** stopwatch, rest timer, weekly tracker, streak counter, and quick workout statistics.
- **Progress:** workout log, exercise-wise weight/reps history, muscle-group summaries, body-weight history, BMI display, and CSV exports.
- **AI Coach:** optional Groq-powered workout and fitness Q&A (Llama 3.3 70B Versatile).
- **Storage:** local JSON fallback plus optional Google Sheets integration.
- **Interface:** responsive Streamlit layout with Dark and Light theme choices.

## Repository layout

```text
Personelise-Gym/
├── app.py                         # Streamlit application (entry point)
├── requirements.txt               # Python dependencies
├── SETUP_GUIDE.md                 # Local setup, secrets and deployment guide
├── tests/
│   └── test_app_smoke.py           # Static regression/smoke tests
└── .github/
    └── workflows/
        └── python-smoke-checks.yml # GitHub Actions checks
```

## Run locally

Python 3.11 is used by the GitHub Actions workflow.

```bash
git clone https://github.com/cho1930lko-hub/Personelise-Gym.git
cd Personelise-Gym

python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The app can open without Google Sheets credentials; cloud sync and AI features remain unavailable until their optional secrets are configured. See [SETUP_GUIDE.md](SETUP_GUIDE.md) for the exact configuration.

## Run the checks

```bash
python -m compileall -q app.py tests
python -m unittest discover -s tests -v
```

GitHub Actions runs these checks on pushes and pull requests targeting `main`, and can also be started manually. These are static/smoke checks; they do **not** verify live Google Sheets access, Groq API responses, or a deployed Streamlit session.

## Important data notes

- The app now provides a **Data Backup** download in the Log & Stats tab. It exports the current workout log, available Google Sheets body-stat history, weekly tracker, checklist and settings as a JSON file. Download it regularly and store it somewhere safe.
- This JSON feature is an export-only backup. Automated import/restore is not yet implemented; keep the connected Google Sheet as the primary persistent data source and retain independent copies.
- Google Sheets writes for Settings and WeeklyTracker now update only their app-managed cell ranges instead of clearing entire worksheets. Keep those managed ranges reserved for the app.
- Multiple sets for one exercise are appended to WorkoutLog in a single batch request, reducing partial per-set writes. If a request reports an uncertain result, inspect the sheet before retrying to avoid duplicates.
- For persistent, cross-session workout and body-history records on Streamlit Cloud, configure Google Sheets. The local `gym_data.json` fallback is not a guaranteed permanent cloud backup.
- The app creates/uses these Google Sheets tabs: `WorkoutLog`, `BodyStats`, `WeeklyTracker`, and `Settings`.
- The current implementation rewrites the contents of `WeeklyTracker` and `Settings` when saving those values. Do not store unrelated/manual data in those tabs.
- BMI is currently calculated using a fixed height of **1.70 m**. Treat the BMI value as an estimate unless that matches the user's height.
- A successful local save is not proof that Google Sheets also saved. Read the in-app save warnings and verify important records in the sheet.

## Security

Never commit API keys, Google service-account JSON files, passwords, or Streamlit secrets to this repository. Store credentials in Streamlit Community Cloud **App settings → Secrets** or in a local, untracked `.streamlit/secrets.toml` file. Rotate any credential that has been exposed.

## Current scope

This repository is a workout tracking dashboard. Membership administration, admission fees, billing, invoices, payment ledger, receipts, and member management are **not currently documented as implemented features**.

For setup and deployment instructions, continue to [SETUP_GUIDE.md](SETUP_GUIDE.md).
