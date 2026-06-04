from __future__ import annotations

from pathlib import Path

import pandas as pd

from careflow.labels import ENCOUNTER_COLUMNS, PATIENT_COLUMNS, PAYER_TRANSITION_COLUMNS
from careflow.models import PatientProfile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "output" / "csv"


def _rename(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    return df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})


def data_available(data_dir: Path | None = None) -> bool:
    d = data_dir or DEFAULT_DATA_DIR
    return (d / "patients.csv").exists()


def load_patients(data_dir: Path | None = None) -> pd.DataFrame:
    d = data_dir or DEFAULT_DATA_DIR
    df = pd.read_csv(d / "patients.csv")
    return _rename(df, PATIENT_COLUMNS)


def load_encounters(data_dir: Path | None = None) -> pd.DataFrame:
    d = data_dir or DEFAULT_DATA_DIR
    df = pd.read_csv(d / "encounters.csv", low_memory=False)
    df = _rename(df, ENCOUNTER_COLUMNS)
    for col in ("visit_start", "visit_end"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    for col in ("total_bill_amount", "insurance_paid_amount", "base_visit_cost"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def load_payer_transitions(data_dir: Path | None = None) -> pd.DataFrame:
    d = data_dir or DEFAULT_DATA_DIR
    df = pd.read_csv(d / "payer_transitions.csv")
    df = _rename(df, PAYER_TRANSITION_COLUMNS)
    for col in ("coverage_start", "coverage_end"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    return df


def load_payers(data_dir: Path | None = None) -> pd.DataFrame:
    d = data_dir or DEFAULT_DATA_DIR
    df = pd.read_csv(d / "payers.csv")
    return df.rename(columns={"Id": "insurance_company_id", "NAME": "insurance_name"})


def load_providers(data_dir: Path | None = None) -> pd.DataFrame:
    d = data_dir or DEFAULT_DATA_DIR
    df = pd.read_csv(d / "providers.csv")
    return df.rename(
        columns={
            "Id": "doctor_id",
            "NAME": "doctor_name",
            "SPECIALITY": "specialty",
            "CITY": "city",
            "STATE": "state",
        }
    )


def row_to_patient(row: pd.Series) -> PatientProfile:
    return PatientProfile(
        patient_id=str(row["patient_id"]),
        first_name=str(row.get("first_name", "")),
        last_name=str(row.get("last_name", "")),
        date_of_birth=str(row.get("date_of_birth", ""))[:10],
        gender=str(row.get("gender", "")),
        city=str(row.get("city", "")),
        state=str(row.get("state", "")),
        annual_income=float(row.get("annual_income", 0) or 0),
        lifetime_medical_spending=float(row.get("lifetime_medical_spending", 0) or 0),
        lifetime_insurance_paid=float(row.get("lifetime_insurance_paid", 0) or 0),
    )


def patient_encounters(patient_id: str, encounters: pd.DataFrame) -> pd.DataFrame:
    if encounters.empty:
        return encounters
    return encounters[encounters["patient_id"] == patient_id].sort_values("visit_start")


def list_patient_options(patients: pd.DataFrame, limit: int = 200) -> list[tuple[str, str]]:
    cols = ["patient_id", "first_name", "last_name", "date_of_birth", "city"]
    subset = patients[cols].head(limit)
    out = []
    for _, r in subset.iterrows():
        label = (
            f"{r['first_name']} {r['last_name']} · {str(r['date_of_birth'])[:10]} · {r['city']}"
        )
        out.append((str(r["patient_id"]), label))
    return out
