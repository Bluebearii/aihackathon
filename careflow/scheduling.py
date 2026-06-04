from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd

from careflow.models import AppointmentSlot, InsuranceStatus, PatientProfile


def _next_weekday(base: datetime, days_ahead: int) -> datetime:
    return base + timedelta(days=days_ahead)


def suggest_appointments(
    patient: PatientProfile,
    providers: pd.DataFrame,
    encounters: pd.DataFrame,
    insurance: InsuranceStatus,
    *,
    n_slots: int = 5,
) -> list[AppointmentSlot]:
    """Rank visit slots like a recommendation feed."""
    now = datetime.now(timezone.utc)
    enc = encounters[encounters["patient_id"] == patient.patient_id]

    preferred_specialty = "GENERAL PRACTICE"
    preferred_doctor = ""
    preferred_type = "wellness"
    if not enc.empty:
        last = enc.sort_values("visit_start").iloc[-1]
        preferred_type = str(last.get("visit_type", "wellness"))
        preferred_doctor = str(last.get("doctor_id", ""))

    pool = providers.copy()
    if "state" in pool.columns and patient.state:
        same_state = pool["state"].astype(str).str.upper() == patient.state.upper()
        if same_state.any():
            pool = pool[same_state]

    if pool.empty:
        pool = providers.head(20)

    slots: list[AppointmentSlot] = []
    for i, (_, doc) in enumerate(pool.head(40).iterrows()):
        doctor_id = str(doc.get("doctor_id", ""))
        score = 50.0
        reasons: list[str] = []

        if doctor_id and doctor_id == preferred_doctor:
            score += 30
            reasons.append("your usual doctor")
        if str(doc.get("specialty", "")).upper() == preferred_specialty:
            score += 15
            reasons.append("primary care match")
        if str(doc.get("city", "")).lower() == patient.city.lower():
            score += 20
            reasons.append("near home")

        if insurance.verification_status in ("gap", "none", "partial"):
            score += 5
            reasons.append("in-network friendly billing")

        t = _next_weekday(now, 2 + (i % 5))
        t = t.replace(hour=9 + (i % 6), minute=0, second=0, microsecond=0)
        reason = ", ".join(reasons) if reasons else "available soon"
        slots.append(
            AppointmentSlot(
                slot_id=f"slot-{doctor_id}-{i}",
                doctor_name=str(doc.get("doctor_name", "Provider")),
                specialty=str(doc.get("specialty", "General")),
                clinic_city=str(doc.get("city", patient.city)),
                visit_type=preferred_type.replace("_", " ").title(),
                suggested_time=t,
                match_score=round(min(score, 99), 1),
                reason=reason,
            )
        )

    slots.sort(key=lambda s: s.match_score, reverse=True)
    return slots[:n_slots]
