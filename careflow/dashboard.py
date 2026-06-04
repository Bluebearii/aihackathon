from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from careflow.data_loader import DEFAULT_DATA_DIR, list_patient_options, patient_encounters
from careflow.labels import JOURNEY_STEPS
from careflow.orchestrator import (
    advance_after_history,
    advance_after_visit_day,
    run_follow_up,
    run_insurance,
    run_scheduling,
    run_sign_in,
    select_appointment,
)
from careflow.store import get_journey, init_session, reset_journey, set_journey

STEP_ORDER = [s[0] for s in JOURNEY_STEPS]


def _step_index(step: str) -> int:
    try:
        return STEP_ORDER.index(step)
    except ValueError:
        return 0


def _progress_header(state_step: str) -> None:
    idx = _step_index(state_step)
    labels = [s[1] for s in JOURNEY_STEPS]
    st.progress((idx + 1) / len(STEP_ORDER), text=f"Step {idx + 1} of {len(STEP_ORDER)}: {labels[idx]}")


def _metric_row(items: list[tuple[str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def render_sign_in(tables: dict, state) -> None:
    st.subheader("1 · Sign in (automated)")
    st.caption("Pick a profile or enter 2 fields — AI loads the rest. No passwords.")

    patients = tables["patients"]
    options = list_patient_options(patients)

    c1, c2, c3 = st.columns(3)
    with c1:
        pick = st.selectbox(
            "Quick select patient",
            [""] + [o[0] for o in options],
            format_func=lambda x: "—" if not x else next(l for i, l in options if i == x),
        )
    with c2:
        fn = st.text_input("First name (optional)")
    with c3:
        ln = st.text_input("Last name (optional)")
    dob = st.text_input("Date of birth (YYYY-MM-DD, optional)")

    if st.button("Sign in with AI", type="primary", use_container_width=True):
        state = run_sign_in(
            state,
            patients,
            patient_id=pick or None,
            first_name=fn,
            last_name=ln,
            date_of_birth=dob,
        )
        set_journey(state)
        if state.sign_in and not state.sign_in.verified:
            st.warning(state.sign_in.message)
        else:
            st.success(state.sign_in.message if state.sign_in else "Signed in")
            st.rerun()

    if state.sign_in:
        st.info(
            f"**Method:** {state.sign_in.method} · "
            f"**Friction score:** {state.sign_in.friction_score:.0f}/100 (lower is easier)"
        )


def render_insurance(state) -> None:
    st.subheader("2 · Insurance verification (automated)")
    if not state.patient:
        st.warning("Sign in first.")
        return
    ins = state.insurance
    if not ins:
        st.warning("Run verification from the sidebar.")
        return

    _metric_row(
        [
            ("Plan", ins.insurance_name),
            ("Status", ins.verification_status.title()),
            ("Insurance pays", f"{ins.avg_insurance_pay_rate:.0f}%"),
            ("Est. you owe", f"${ins.patient_responsibility_estimate:,.0f}"),
        ]
    )
    st.success(ins.ai_summary)
    st.markdown(
        f"- **Member ID:** {ins.member_id or '—'}  \n"
        f"- **Coverage:** {ins.coverage_start or '—'} → {ins.coverage_end or 'ongoing'}"
    )


def render_history(tables: dict, state) -> None:
    st.subheader("3 · Your care so far")
    if not state.patient:
        return
    enc = patient_encounters(state.patient.patient_id, tables["encounters"])
    if enc.empty:
        st.info("No visits on file yet — book your first appointment next.")
        return

    show = enc.tail(12)[
        ["visit_start", "visit_type", "visit_reason", "total_bill_amount", "insurance_paid_amount"]
    ].copy()
    show.columns = [
        "Visit date",
        "Visit type",
        "Reason",
        "Total bill",
        "Insurance paid",
    ]
    st.dataframe(show, use_container_width=True, hide_index=True)

    show["You paid"] = show["Total bill"] - show["Insurance paid"]
    fig = px.bar(
        show.tail(8),
        x="Visit date",
        y=["Insurance paid", "You paid"],
        title="Who paid for recent visits",
        barmode="stack",
    )
    st.plotly_chart(fig, use_container_width=True)

    if st.button("Continue to booking", type="primary"):
        state = advance_after_history(state)
        set_journey(state)
        st.rerun()


def render_appointment(tables: dict, state) -> None:
    st.subheader("4 · Book your visit (AI scheduling)")
    if not state.patient:
        return

    if not state.appointments and st.button("Find best appointments", type="primary"):
        state = run_scheduling(state, tables)
        set_journey(state)
        st.rerun()

    for slot in state.appointments:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            c1.markdown(
                f"**{slot.doctor_name}** · {slot.specialty}  \n"
                f"{slot.visit_type} in {slot.clinic_city}  \n"
                f"📅 {slot.suggested_time.strftime('%a %b %d · %I:%M %p')}  \n"
                f"Match score **{slot.match_score}** — _{slot.reason}_"
            )
            if c2.button("Book", key=slot.slot_id):
                state = select_appointment(state, slot)
                set_journey(state)
                st.rerun()


def render_visit_day(state) -> None:
    st.subheader("5 · Day of care")
    st.caption("Everything for today’s visit in one place — check in, arrive, see your doctor, wrap up.")

    if not state.selected_slot:
        st.warning("No appointment booked yet.")
        if st.button("← Back to booking", type="primary"):
            state.current_step = "appointment"
            set_journey(state)
            st.rerun()
        return

    slot = state.selected_slot
    ins = state.insurance
    visit_when = slot.suggested_time.strftime("%A, %B %d, %Y at %I:%M %p")

    _metric_row(
        [
            ("Doctor", slot.doctor_name),
            ("Visit type", slot.visit_type),
            ("When", visit_when),
            ("Location", slot.clinic_city),
        ]
    )

    left, right = st.columns([3, 2])
    with left:
        st.markdown("#### Today’s timeline")
        phases = [
            ("🟢 Now", "Digital check-in", "Complete below — skip the front-desk line."),
            ("📍 Before arrival", "What to bring", "Photo ID · insurance already verified in app"),
            ("🏥 Arrival", "Check-in lane", "Priority lane when pre-visit checklist is done"),
            ("🩺 Visit", "With your clinician", f"{slot.specialty} · {slot.visit_type}"),
            ("💳 After visit", "Billing", "Auto-runs savings deals if insurance underpays"),
        ]
        for marker, title, detail in phases:
            with st.container(border=True):
                c1, c2 = st.columns([1, 5])
                c1.markdown(f"**{marker}**")
                c2.markdown(f"**{title}**  \n{detail}")

    with right:
        st.markdown("#### Visit summary")
        st.success(f"**{slot.doctor_name}**")
        st.write(f"Specialty: {slot.specialty}")
        st.write(f"Match score: **{slot.match_score}** — _{slot.reason}_")
        if ins:
            st.info(
                f"Insurance: **{ins.insurance_name}** ({ins.verification_status.title()})  \n"
                f"Member ID: {ins.member_id or 'on file'}"
            )

    st.divider()
    st.markdown("#### Pre-visit checklist")
    checks = {
        "checkin_done": "Digital check-in completed",
        "id_ready": "ID ready (or on phone)",
        "insurance_confirmed": "Insurance confirmed in app",
        "questionnaire_done": "3-minute health questionnaire done (priority lane)",
        "directions": "Directions / parking reviewed",
    }
    done = 0
    cols = st.columns(2)
    for i, (key, label) in enumerate(checks.items()):
        with cols[i % 2]:
            if st.checkbox(label, key=f"visit_{key}"):
                done += 1

    progress = done / len(checks)
    st.progress(progress, text=f"Ready for visit: {done}/{len(checks)} tasks")
    if progress >= 0.6:
        st.success("You’re cleared for priority check-in.")
    elif progress > 0:
        st.info("Finish the checklist to unlock the fast lane.")
    else:
        st.caption("Start with digital check-in — it’s the fastest win.")


def render_billing(state) -> None:
    st.subheader("6 · Billing & smart deals")
    if not state.deals:
        st.caption("Deals appear when insurance does not cover enough of the bill.")
        return

    st.markdown(
        "_When insurance underpays, we rank offers that save **you** money "
        "and protect **provider** revenue — like a personalized feed._"
    )
    for d in state.deals:
        with st.container(border=True):
            st.markdown(f"#### {d.title}")
            st.caption(d.trigger)
            st.write(d.description)
            c1, c2, c3 = st.columns(3)
            c1.metric("You save", f"${d.patient_savings:,.0f}")
            c2.metric("Clinic margin", f"${d.provider_margin:,.0f}")
            c3.metric("Deal score", f"{d.combined_score:,.0f}")


def render_follow_up(tables: dict, state) -> None:
    st.subheader("7 · Stay on track (incentive feed)")
    if not state.incentives and state.patient:
        state = run_follow_up(state, tables)
        set_journey(state)

    if state.patient:
        _metric_row(
            [
                ("Engagement score", f"{state.engagement_score:.0f}/100"),
                ("Show-up rate", f"{state.show_rate * 100:.0f}%"),
                ("Next goal", "Book within 14 days"),
            ]
        )

    st.markdown("_Ranked by predicted impact on keeping you coming back — similar to social feeds._")
    for card in state.incentives:
        with st.container(border=True):
            st.markdown(f"**{card.headline}** (+{card.engagement_lift:.0f}% retention lift)")
            st.write(card.body)
            st.button(card.action_label, key=f"btn-{card.card_id}", disabled=True)


def run_dashboard(data_dir: Path | None = None) -> None:
    st.set_page_config(
        page_title="CareFlow",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        # CareFlow
        **Your path from sign-in → insurance → visit → savings → next appointment**

        Plain language. AI handles sign-in, insurance checks, and scheduling.
        Deals kick in when insurance pays too little. Incentives keep you coming back.
        """
    )

    d = data_dir or DEFAULT_DATA_DIR
    tables = init_session(d)

    if not tables:
        st.error(
            f"No Synthea data found in `{d}`. "
            "Generate CSVs under `output/csv/` or set data folder in the sidebar."
        )
        custom = st.text_input("Data folder path", str(d))
        if st.button("Load data") and Path(custom).exists():
            st.cache_data.clear()
            st.session_state.careflow_tables = None
            init_session(Path(custom))
            st.rerun()
        return

    state = get_journey()

    with st.sidebar:
        st.header("Journey")
        for key, title, hint in JOURNEY_STEPS:
            marker = "●" if key == state.current_step else "○"
            st.markdown(f"{marker} **{title}** — {hint}")

        st.divider()
        if state.patient:
            st.success(f"Signed in: **{state.patient.display_name}**")

        if state.patient and not state.insurance:
            if st.button("Run insurance AI"):
                state = run_insurance(state, tables)
                set_journey(state)
                st.rerun()

        if st.button("Reset journey"):
            reset_journey()
            st.rerun()

    _progress_header(state.current_step)

    step = state.current_step
    if step == "sign_in":
        render_sign_in(tables, state)
    elif step == "insurance":
        render_insurance(state)
        if state.insurance:
            if st.button("View care history", type="primary"):
                state.current_step = "history"
                set_journey(state)
                st.rerun()
    elif step == "history":
        render_history(tables, state)
    elif step == "appointment":
        render_appointment(tables, state)
    elif step == "visit_day":
        render_visit_day(state)
        if state.selected_slot:
            st.divider()
            if st.button("Visit complete → billing & savings", type="primary", use_container_width=True):
                state = advance_after_visit_day(state, tables)
                set_journey(state)
                st.rerun()
    elif step == "billing":
        render_billing(state)
        if state.deals and st.button("Continue to stay-on-track rewards", type="primary"):
            state = run_follow_up(state, tables)
            state.current_step = "follow_up"
            set_journey(state)
            st.rerun()
        elif not state.deals and state.patient:
            if st.button("Load savings offers", type="primary"):
                state = advance_after_visit_day(state, tables)
                set_journey(state)
                st.rerun()
    elif step == "follow_up":
        render_follow_up(tables, state)

    # Auto-chain after sign-in
    if step == "insurance" and state.patient and not state.insurance:
        state = run_insurance(state, tables)
        set_journey(state)
