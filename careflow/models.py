from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class PatientProfile:
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    city: str
    state: str
    annual_income: float
    lifetime_medical_spending: float
    lifetime_insurance_paid: float
    display_name: str = ""

    def __post_init__(self) -> None:
        if not self.display_name:
            self.display_name = f"{self.first_name} {self.last_name}".strip()


@dataclass
class SignInResult:
    verified: bool
    method: str
    friction_score: float  # 0 = effortless, 100 = high friction
    message: str
    matched_fields: list[str] = field(default_factory=list)


@dataclass
class InsuranceStatus:
    active: bool
    insurance_name: str
    member_id: str
    coverage_start: str
    coverage_end: str | None
    verification_status: str  # verified | partial | gap | none
    avg_insurance_pay_rate: float
    patient_responsibility_estimate: float
    ai_summary: str


@dataclass
class AppointmentSlot:
    slot_id: str
    doctor_name: str
    specialty: str
    clinic_city: str
    visit_type: str
    suggested_time: datetime
    match_score: float
    reason: str


@dataclass
class DealOffer:
    deal_id: str
    title: str
    description: str
    patient_savings: float
    provider_margin: float
    combined_score: float
    trigger: str


@dataclass
class IncentiveCard:
    card_id: str
    headline: str
    body: str
    reward_type: str
    engagement_lift: float
    action_label: str


@dataclass
class JourneyState:
    current_step: str = "sign_in"
    patient: PatientProfile | None = None
    sign_in: SignInResult | None = None
    insurance: InsuranceStatus | None = None
    appointments: list[AppointmentSlot] = field(default_factory=list)
    selected_slot: AppointmentSlot | None = None
    deals: list[DealOffer] = field(default_factory=list)
    incentives: list[IncentiveCard] = field(default_factory=list)
    engagement_score: float = 0.0
    show_rate: float = 0.0
    notes: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)
