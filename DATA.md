# Local data (not in Git)

These paths are **gitignored** because they are too large for GitHub:

| Path | Size (approx.) | Purpose |
|------|----------------|---------|
| `output/` | ~600 MB+ | Synthea CSV exports for CareFlow |
| `synthea/` | ~2 GB | Full Synthea source clone (optional) |
| `synthea-with-dependencies.jar` | ~188 MB | Synthea runner JAR |
| `data/raw/` | varies | Downloaded hospital / CMS files |
| `venv/` | varies | Python virtual environment |

## Regenerate `output/` for the dashboard

```bash
# Download JAR from https://github.com/synthetichealth/synthea/releases
java -jar synthea-with-dependencies.jar -p 1000 Texas

streamlit run streamlit_app.py
```

Required CSV files: `output/csv/patients.csv`, `encounters.csv`, `payer_transitions.csv`, `payers.csv`, `providers.csv`.
