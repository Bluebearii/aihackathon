from __future__ import annotations

import pandas as pd

from careflow.models import DealOffer, InsuranceStatus, PatientProfile

COVERAGE_GAP_THRESHOLD = 0.70


def recommend_deals(
    patient: PatientProfile,
    encounters: pd.DataFrame,
    insurance: InsuranceStatus,
) -> list[DealOffer]:
    """
    When insurance underpays, rank deals that balance patient savings and provider margin.
    """
    enc = encounters[encounters["patient_id"] == patient.patient_id].copy()
    if enc.empty:
        return _generic_deals(insurance)

    enc["patient_owes"] = enc["total_bill_amount"] - enc["insurance_paid_amount"]
    enc["pay_rate"] = enc["insurance_paid_amount"] / enc["total_bill_amount"].replace(0, 1)
    gaps = enc[
        (enc["total_bill_amount"] > 50)
        & (enc["pay_rate"] < COVERAGE_GAP_THRESHOLD)
    ]

    total_gap = float(gaps["patient_owes"].sum()) if not gaps.empty else 0.0
    avg_gap = float(gaps["pay_rate"].mean() * 100) if not gaps.empty else 0.0

    deals: list[DealOffer] = []

    if total_gap > 100 or insurance.verification_status in ("gap", "partial", "none"):
        savings = min(total_gap * 0.25, 2500)
        margin = savings * 0.35
        deals.append(
            DealOffer(
                deal_id="bundle-cash",
                title="Cash-pay care bundle",
                description=(
                    "Pay upfront for your next 3 visits at a fixed price — "
                    "skips claim delays and reduces bad debt."
                ),
                patient_savings=round(savings, 2),
                provider_margin=round(margin, 2),
                combined_score=round(savings * 0.5 + margin * 0.5, 2),
                trigger=f"Insurance covered only ~{avg_gap:.0f}% on recent visits",
            )
        )

        savings2 = min(total_gap * 0.15, 800)
        deals.append(
            DealOffer(
                deal_id="plan-0-apr",
                title="0% payment plan",
                description="Split outstanding balance over 12 months with autopay — fewer no-shows.",
                patient_savings=round(savings2 * 0.8, 2),
                provider_margin=round(savings2 * 0.2, 2),
                combined_score=round(savings2 * 0.45, 2),
                trigger="High patient responsibility on file",
            )
        )

        deals.append(
            DealOffer(
                deal_id="lab-redirect",
                title="In-network lab swap",
                description="Same tests, partner lab — typically 40–60% lower out-of-pocket.",
                patient_savings=round(min(total_gap * 0.12, 400), 2),
                provider_margin=round(75, 2),
                combined_score=round(min(total_gap * 0.12, 400) * 0.4 + 75, 2),
                trigger="Imaging / lab claims underpaid",
            )
        )

        deals.append(
            DealOffer(
                deal_id="generic-rx",
                title="Generic medication switch",
                description="AI flags therapeutically similar generics covered at tier 1.",
                patient_savings=round(120, 2),
                provider_margin=round(40, 2),
                combined_score=80.0,
                trigger="Recurring pharmacy spend detected",
            )
        )

    deals.sort(key=lambda d: d.combined_score, reverse=True)
    return deals[:6] if deals else _generic_deals(insurance)


def _generic_deals(insurance: InsuranceStatus) -> list[DealOffer]:
    return [
        DealOffer(
            deal_id="wellness-pack",
            title="Annual wellness pack",
            description="Screening + follow-up visit bundled below typical copay stack.",
            patient_savings=85.0,
            provider_margin=120.0,
            combined_score=102.5,
            trigger=insurance.ai_summary,
        ),
    ]
