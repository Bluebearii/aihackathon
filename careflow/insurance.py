from __future__ import annotations

import pandas as pd

from careflow.models import InsuranceStatus, PatientProfile


def verify_insurance(
    patient: PatientProfile,
    payer_transitions: pd.DataFrame,
    payers: pd.DataFrame,
    encounters: pd.DataFrame,
) -> InsuranceStatus:
    """Automated eligibility + pay-rate check from Synthea history."""
    pt = payer_transitions[payer_transitions["patient_id"] == patient.patient_id]
    active = pt[pt["coverage_end"].isna() | (pt["coverage_end"] > pd.Timestamp.now(tz="UTC"))]
    if active.empty and not pt.empty:
        active = pt.sort_values("coverage_start").tail(1)

    payer_id = ""
    member_id = ""
    start_s, end_s = "", None
    if not active.empty:
        row = active.iloc[-1]
        payer_id = str(row.get("insurance_company_id", ""))
        member_id = str(row.get("insurance_member_id", "") or "—")
        start_s = str(row.get("coverage_start", ""))[:10]
        end_val = row.get("coverage_end")
        end_s = None if pd.isna(end_val) else str(end_val)[:10]

    name = "No active plan on file"
    if payer_id and not payers.empty:
        hit = payers[payers["insurance_company_id"] == payer_id]
        if not hit.empty:
            name = str(hit.iloc[0]["insurance_name"])

    enc = encounters[encounters["patient_id"] == patient.patient_id]
    pay_rate = 0.0
    patient_due = 0.0
    if not enc.empty:
        bills = enc["total_bill_amount"].sum()
        paid = enc["insurance_paid_amount"].sum()
        if bills > 0:
            pay_rate = float(paid / bills)
        patient_due = float(max(0, bills - paid))

    if pay_rate >= 0.7:
        status, summary = "verified", "Coverage looks strong for upcoming visits."
    elif pay_rate >= 0.3:
        status, summary = "partial", "Insurance pays part of the bill — savings deals may help."
    elif pay_rate > 0:
        status, summary = "gap", "Large out-of-pocket gap — we'll surface money-saving options."
    else:
        status, summary = "none", "Little or no payer history — self-pay bundles recommended."

    return InsuranceStatus(
        active=bool(payer_id) or pay_rate > 0,
        insurance_name=name,
        member_id=member_id,
        coverage_start=start_s,
        coverage_end=end_s,
        verification_status=status,
        avg_insurance_pay_rate=round(pay_rate * 100, 1),
        patient_responsibility_estimate=round(patient_due, 2),
        ai_summary=summary,
    )
