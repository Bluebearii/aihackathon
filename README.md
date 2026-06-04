# CareFlow

A Streamlit dashboard that walks a patient through healthcare from **sign-in to follow-up care**, using [Synthea](https://github.com/synthetichealth/synthea) synthetic patient data. Plain-language labels, AI-style automation for sign-in, insurance, and scheduling, plus deal and incentive engines when insurance underpays or engagement drops.

## Features

| Step | What it does |
|------|----------------|
| **Sign in** | One-tap or name + birthday — minimal friction |
| **Insurance** | Auto-verify coverage and estimated out-of-pocket |
| **Care history** | Past visits and who paid (insurance vs patient) |
| **Book visit** | AI-ranked appointment slots |
| **Day of care** | Timeline, checklist, priority check-in |
| **Billing & deals** | Savings offers when insurance pays too little |
| **Stay on track** | Incentive feed ranked like a social feed |

**Deal logic:** when insurance covers less than ~70% of recent bills, the app recommends bundles (cash-pay, payment plans, lab swaps, etc.) scored for both **patient savings** and **provider margin**.

**Incentives:** streaks, reminders, and welcome-back offers ranked by predicted impact on show-up rate.

## Requirements

- Python 3.11+ (3.12 recommended)
- Java 11+ (only if you generate your own Synthea data)
- ~700 MB disk for full `output/csv/` dataset (not stored in Git)

## Quick start

```bash
git clone <your-repo-url>
cd aihackathon

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Minimal deps for the dashboard:
pip install streamlit pandas plotly pyarrow python-dateutil

# Or full project stack:
pip install -r requirements.txt
```

### Patient data

CareFlow reads CSVs from `output/csv/`. That folder is **not in Git** (too large). Either:

1. Use data you already generated locally, or  
2. Generate it with Synthea — see **[DATA.md](DATA.md)** for details.

Required files:

- `patients.csv`
- `encounters.csv`
- `payer_transitions.csv`
- `payers.csv`
- `providers.csv`

### Run the app

```bash
streamlit run streamlit_app.py
```

Or:

```bash
python main.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`).

## Project layout

```text
aihackathon/
├── careflow/              # App logic
│   ├── dashboard.py       # Streamlit UI
│   ├── orchestrator.py    # Journey flow
│   ├── signin.py          # Automated sign-in
│   ├── insurance.py       # Coverage verification
│   ├── scheduling.py      # Appointment ranking
│   ├── deals.py           # Savings / margin deals
│   ├── incentives.py      # Retention feed
│   ├── data_loader.py     # Synthea CSV → friendly column names
│   └── labels.py          # Human-readable field mappings
├── streamlit_app.py       # Entry point
├── main.py                # Launches Streamlit
├── DATA.md                # How to generate / share data
├── requirements.txt       # Full dependencies
└── output/csv/            # Generated locally (gitignored)
```

## Sharing with others

**Via GitHub (code only)**  
Push the repo; teammates clone, install Python deps, and generate or receive `output/csv/` separately. See [DATA.md](DATA.md).

**Via zip**  
- `CareFlow-app.zip` — repo without `output/`, `synthea/`, `venv/`  
- `CareFlow-data.zip` — only `output/csv/` (share on Drive / USB)

**Live demo**  
Run locally and screen-share, or deploy to [Streamlit Community Cloud](https://share.streamlit.io) (you’ll need data on the host or a small committed sample).

## Git: what not to commit

These are in `.gitignore` because of size:

- `output/` — Synthea CSV exports  
- `synthea/` — Synthea source tree  
- `synthea-with-dependencies.jar`  
- `venv/`, `*.egg-info/`

## Data column names

Synthea fields are renamed for clarity (e.g. `PAYER_COVERAGE` → `insurance_paid_amount`, `FIRST` → `first_name`). Mappings live in `careflow/labels.py`.

## License / attribution

Synthetic patients from [Synthea](https://github.com/synthetichealth/synthea). This project is for education and hackathon prototyping—not for production clinical use without proper validation and compliance review.
