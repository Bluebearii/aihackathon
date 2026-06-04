from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from careflow.models import IncentiveCard, PatientProfile


def compute_engagement(
    patient: PatientProfile,
    encounters: pd.DataFrame,
) -> tuple[float, float]:
    """Engagement score (0–100) and historical show rate."""
    enc = encounters[encounters["patient_id"] == patient.patient_id]
    if enc.empty:
        return 25.0, 0.5

    enc = enc.sort_values("visit_start")
    completed = len(enc[enc["visit_end"].notna()])
    scheduled = len(enc)
    show_rate = completed / max(scheduled, 1)

    last = enc["visit_start"].max()
    days_since = 365.0
    if pd.notna(last):
        days_since = (datetime.now(timezone.utc) - last).days

    recency = max(0, 100 - days_since * 0.15)
    volume = min(30, len(enc) * 0.5)
    score = min(100, show_rate * 40 + recency * 0.35 + volume)
    return round(score, 1), round(show_rate, 2)


def rank_incentives(
    patient: PatientProfile,
    encounters: pd.DataFrame,
    engagement_score: float,
    show_rate: float,
) -> list[IncentiveCard]:
    """
    Social-style feed: rank actions by predicted retention lift.
    """
    enc = encounters[encounters["patient_id"] == patient.patient_id]
    days_since = 999
    if not enc.empty and enc["visit_start"].notna().any():
        last = enc["visit_start"].max()
        days_since = (datetime.now(timezone.utc) - last).days

    cards = [
        IncentiveCard(
            card_id="streak",
            headline="Visit streak bonus",
            body=f"Book within 14 days → earn $25 credit toward copay. ({days_since} days since last visit)",
            reward_type="copay_credit",
            engagement_lift=22.0 if days_since > 60 else 12.0,
            action_label="Book next visit",
        ),
        IncentiveCard(
            card_id="morning",
            headline="Morning slots = shorter wait",
            body="AI ranked 9–11 AM openings with 18% lower average wait in your area.",
            reward_type="priority_access",
            engagement_lift=15.0,
            action_label="See morning times",
        ),
        IncentiveCard(
            card_id="referral",
            headline="Bring a friend, both save",
            body="Refer someone to primary care — $40 account credit when they complete a visit.",
            reward_type="referral",
            engagement_lift=10.0,
            action_label="Share invite link",
        ),
        IncentiveCard(
            card_id="prep",
            headline="Pre-visit checklist done",
            body="Complete 3-min health questionnaire before arrival → priority check-in lane.",
            reward_type="friction_removal",
            engagement_lift=18.0,
            action_label="Start checklist",
        ),
    ]

    if show_rate < 0.85:
        cards.append(
            IncentiveCard(
                card_id="reminder",
                headline="Smart reminders",
                body="Text + calendar hold cut no-shows by ~31% for patients like you.",
                reward_type="retention",
                engagement_lift=28.0,
                action_label="Turn on reminders",
            )
        )

    if engagement_score < 50:
        cards.insert(
            0,
            IncentiveCard(
                card_id="welcome-back",
                headline="Welcome-back package",
                body="Free nurse line for 30 days when you schedule this week.",
                reward_type="win_back",
                engagement_lift=35.0,
                action_label="Claim offer",
            ),
        )

    cards.sort(key=lambda c: c.engagement_lift, reverse=True)
    return cards
