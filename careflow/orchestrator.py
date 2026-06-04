from __future__ import annotations

import pandas as pd

from careflow.deals import recommend_deals
from careflow.incentives import compute_engagement, rank_incentives
from careflow.insurance import verify_insurance
from careflow.models import AppointmentSlot, JourneyState, PatientProfile
from careflow.scheduling import suggest_appointments
from careflow.signin import auto_sign_in


def run_sign_in(
    state: JourneyState,
    patients: pd.DataFrame,
    *,
    patient_id: str | None = None,
    first_name: str = "",
    last_name: str = "",
    date_of_birth: str = "",
) -> JourneyState:
    profile, result = auto_sign_in(
        patients,
        patient_id=patient_id,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
    )
    state.sign_in = result
    if profile:
        state.patient = profile
        state.current_step = "insurance"
        state.notes.append(f"Signed in as {profile.display_name}")
    return state


def run_insurance(state: JourneyState, tables: dict[str, pd.DataFrame]) -> JourneyState:
    if not state.patient:
        return state
    state.insurance = verify_insurance(
        state.patient,
        tables["payer_transitions"],
        tables["payers"],
        tables["encounters"],
    )
    state.current_step = "history"
    return state


def run_scheduling(state: JourneyState, tables: dict[str, pd.DataFrame]) -> JourneyState:
    if not state.patient or not state.insurance:
        return state
    state.appointments = suggest_appointments(
        state.patient,
        tables["providers"],
        tables["encounters"],
        state.insurance,
    )
    state.current_step = "appointment"
    return state


def select_appointment(state: JourneyState, slot: AppointmentSlot) -> JourneyState:
    state.selected_slot = slot
    state.current_step = "visit_day"
    state.notes.append(f"Booked with {slot.doctor_name} on {slot.suggested_time:%Y-%m-%d %H:%M}")
    return state


def run_billing(state: JourneyState, tables: dict[str, pd.DataFrame]) -> JourneyState:
    if not state.patient or not state.insurance:
        return state
    state.deals = recommend_deals(
        state.patient,
        tables["encounters"],
        state.insurance,
    )
    state.current_step = "billing"
    return state


def run_follow_up(state: JourneyState, tables: dict[str, pd.DataFrame]) -> JourneyState:
    if not state.patient:
        return state
    score, show = compute_engagement(state.patient, tables["encounters"])
    state.engagement_score = score
    state.show_rate = show
    state.incentives = rank_incentives(
        state.patient, tables["encounters"], score, show
    )
    return state


def advance_after_history(state: JourneyState) -> JourneyState:
    state.current_step = "appointment"
    return state


def advance_after_visit_day(state: JourneyState, tables: dict[str, pd.DataFrame]) -> JourneyState:
    return run_billing(state, tables)
