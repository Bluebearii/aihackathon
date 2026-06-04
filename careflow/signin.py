from __future__ import annotations

import re

import pandas as pd

from careflow.models import PatientProfile, SignInResult


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def auto_sign_in(
    patients: pd.DataFrame,
    *,
    patient_id: str | None = None,
    first_name: str = "",
    last_name: str = "",
    date_of_birth: str = "",
) -> tuple[PatientProfile | None, SignInResult]:
    """AI-assisted sign-in: prefer ID match, else fuzzy name + DOB."""
    matched: list[str] = []

    if patient_id:
        row = patients[patients["patient_id"] == patient_id]
        if not row.empty:
            from careflow.data_loader import row_to_patient

            p = row_to_patient(row.iloc[0])
            return p, SignInResult(
                verified=True,
                method="One-tap (selected profile)",
                friction_score=5.0,
                message="Welcome back — profile loaded automatically.",
                matched_fields=["patient_id"],
            )

    fn, ln, dob = _norm(first_name), _norm(last_name), (date_of_birth or "")[:10]
    if fn and ln:
        mask = (
            patients["first_name"].astype(str).str.lower().str.contains(fn, regex=False)
            & patients["last_name"].astype(str).str.lower().str.contains(ln, regex=False)
        )
        if dob:
            mask &= patients["date_of_birth"].astype(str).str.startswith(dob)
            matched.append("date_of_birth")
        matched.extend(["first_name", "last_name"])
        hits = patients[mask]
        if len(hits) == 1:
            from careflow.data_loader import row_to_patient

            fields = 2 + (1 if dob else 0)
            friction = max(10.0, 40.0 - fields * 10)
            return row_to_patient(hits.iloc[0]), SignInResult(
                verified=True,
                method="Smart match (name + birthday)",
                friction_score=friction,
                message="Identity confirmed — no passwords or long forms.",
                matched_fields=matched,
            )
        if len(hits) > 1:
            return None, SignInResult(
                verified=False,
                method="Smart match",
                friction_score=35.0,
                message="Several profiles match — pick yours from the list.",
                matched_fields=matched,
            )

    return None, SignInResult(
        verified=False,
        method="Not signed in",
        friction_score=80.0,
        message="Choose a profile or enter name and birthday to continue.",
        matched_fields=[],
    )
