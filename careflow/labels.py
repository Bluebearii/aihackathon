"""Human-readable names for Synthea / clinical fields."""

PATIENT_COLUMNS = {
    "Id": "patient_id",
    "BIRTHDATE": "date_of_birth",
    "DEATHDATE": "date_of_death",
    "SSN": "social_security_number",
    "FIRST": "first_name",
    "MIDDLE": "middle_name",
    "LAST": "last_name",
    "GENDER": "gender",
    "RACE": "race",
    "ETHNICITY": "ethnicity",
    "MARITAL": "marital_status",
    "ADDRESS": "street_address",
    "CITY": "city",
    "STATE": "state",
    "ZIP": "zip_code",
    "LAT": "latitude",
    "LON": "longitude",
    "HEALTHCARE_EXPENSES": "lifetime_medical_spending",
    "HEALTHCARE_COVERAGE": "lifetime_insurance_paid",
    "INCOME": "annual_income",
}

ENCOUNTER_COLUMNS = {
    "Id": "visit_id",
    "START": "visit_start",
    "STOP": "visit_end",
    "PATIENT": "patient_id",
    "ORGANIZATION": "clinic_id",
    "PROVIDER": "doctor_id",
    "PAYER": "insurance_company_id",
    "ENCOUNTERCLASS": "visit_type",
    "CODE": "procedure_code",
    "DESCRIPTION": "visit_reason",
    "BASE_ENCOUNTER_COST": "base_visit_cost",
    "TOTAL_CLAIM_COST": "total_bill_amount",
    "PAYER_COVERAGE": "insurance_paid_amount",
    "REASONDESCRIPTION": "diagnosis_summary",
}

PAYER_TRANSITION_COLUMNS = {
    "PATIENT": "patient_id",
    "MEMBERID": "insurance_member_id",
    "START_DATE": "coverage_start",
    "END_DATE": "coverage_end",
    "PAYER": "insurance_company_id",
    "SECONDARY_PAYER": "backup_insurance_id",
    "OWNER_NAME": "plan_sponsor",
}

JOURNEY_STEPS = [
    ("sign_in", "Sign in", "Quick identity check — we fill the rest."),
    ("insurance", "Insurance check", "Verify coverage before you book."),
    ("history", "Your care so far", "Visits, conditions, and what's next."),
    ("appointment", "Book visit", "AI picks the best time and doctor."),
    ("visit_day", "Day of care", "Checklist so nothing gets missed."),
    ("billing", "Billing & savings", "Deals when insurance falls short."),
    ("follow_up", "Stay on track", "Rewards and your next visit."),
]
