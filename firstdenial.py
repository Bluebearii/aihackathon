import pandas as pd
import os

csv_path = "/Users/tommynguyen/codingprojects/AIhackathon/output/csv/"

csvs = ["claims", "encounters", "patients", "conditions",
        "procedures", "medications", "payers", "payer_transitions", "providers"]

dfs = {name: pd.read_csv(os.path.join(csv_path, f"{name}.csv")) for name in csvs}

# ── 1. Base: one row per claim ────────────────────────────────────────────────
model_df = dfs["claims"].copy()

# ── 2. Encounter features ─────────────────────────────────────────────────────
enc = dfs["encounters"][[
    "Id", "ENCOUNTERCLASS", "REASONCODE", "PROVIDER",
    "BASE_ENCOUNTER_COST", "TOTAL_CLAIM_COST", "PAYER_COVERAGE"
]].rename(columns={"Id": "ENC_ID"})
model_df = model_df.merge(enc, left_on="APPOINTMENTID", right_on="ENC_ID", how="left")

# ── 3. Patient features ───────────────────────────────────────────────────────
pat = dfs["patients"][[
    "Id", "BIRTHDATE", "GENDER", "RACE", "ETHNICITY",
    "STATE", "ZIP", "INCOME", "HEALTHCARE_EXPENSES", "HEALTHCARE_COVERAGE"
]].rename(columns={"Id": "PAT_ID"})
pat["AGE"] = (pd.to_datetime("today") - pd.to_datetime(pat["BIRTHDATE"])).dt.days // 365
model_df = model_df.merge(pat, left_on="PATIENTID", right_on="PAT_ID", how="left")

# ── 4. Payer features ─────────────────────────────────────────────────────────
payer = dfs["payers"][[
    "Id", "NAME",
    "AMOUNT_COVERED", "AMOUNT_UNCOVERED",
    "COVERED_ENCOUNTERS", "UNCOVERED_ENCOUNTERS",
    "COVERED_MEDICATIONS", "UNCOVERED_MEDICATIONS",
    "COVERED_PROCEDURES", "UNCOVERED_PROCEDURES",
    "QOLS_AVG", "MEMBER_MONTHS"
]].rename(columns={"Id": "PAYER_ID", "NAME": "PAYER_NAME"})

# Payer denial rate = uncovered / (covered + uncovered) per category
payer["PAYER_ENC_DENIAL_RATE"]  = payer["UNCOVERED_ENCOUNTERS"]  / (payer["COVERED_ENCOUNTERS"]  + payer["UNCOVERED_ENCOUNTERS"]  + 1e-9)
payer["PAYER_MED_DENIAL_RATE"]  = payer["UNCOVERED_MEDICATIONS"] / (payer["COVERED_MEDICATIONS"] + payer["UNCOVERED_MEDICATIONS"] + 1e-9)
payer["PAYER_PROC_DENIAL_RATE"] = payer["UNCOVERED_PROCEDURES"]  / (payer["COVERED_PROCEDURES"]  + payer["UNCOVERED_PROCEDURES"]  + 1e-9)

model_df = model_df.merge(payer, left_on="PRIMARYPATIENTINSURANCEID", right_on="PAYER_ID", how="left")

# ── 5. Condition count per patient (comorbidity burden) ───────────────────────
cond_count = dfs["conditions"].groupby("PATIENT").size().reset_index(name="CONDITION_COUNT")
model_df = model_df.merge(cond_count, left_on="PATIENTID", right_on="PATIENT", how="left")

# ── 6. Procedure count + avg cost per encounter ───────────────────────────────
proc = dfs["procedures"].groupby("ENCOUNTER").agg(
    PROCEDURE_COUNT=("CODE", "count"),
    PROCEDURE_AVG_COST=("BASE_COST", "mean")
).reset_index()
model_df = model_df.merge(proc, left_on="APPOINTMENTID", right_on="ENCOUNTER", how="left")

# ── 7. Medication count + avg cost per patient ────────────────────────────────
med = dfs["medications"].groupby("PATIENT").agg(
    MEDICATION_COUNT=("CODE", "count"),
    MEDICATION_AVG_COST=("BASE_COST", "mean"),
    MEDICATION_TOTAL_COST=("TOTALCOST", "sum")
).reset_index()
model_df = model_df.merge(med, left_on="PATIENTID", right_on="PATIENT", how="left")

# ── 8. Payer transition count (insurance instability) ────────────────────────
pt_count = dfs["payer_transitions"].groupby("PATIENT").agg(
    PAYER_TRANSITION_COUNT=("PAYER", "count"),
    UNIQUE_PAYERS=("PAYER", "nunique")
).reset_index()
model_df = model_df.merge(pt_count, left_on="PATIENTID", right_on="PATIENT", how="left")

# ── 9. Provider features ──────────────────────────────────────────────────────
prov = dfs["providers"][[
    "Id", "SPECIALITY", "ENCOUNTERS", "PROCEDURES"
]].rename(columns={"Id": "PROV_ID", "ENCOUNTERS": "PROV_ENCOUNTER_COUNT", "PROCEDURES": "PROV_PROCEDURE_COUNT"})
model_df = model_df.merge(prov, left_on="PROVIDERID", right_on="PROV_ID", how="left")

# ── 10. Engineer target label (DENIED proxy) ──────────────────────────────────
# A claim is "denied" if there is any outstanding balance and payer covered $0
model_df["DENIED"] = (
    (model_df["OUTSTANDING1"] > 0) & (model_df["PAYER_COVERAGE"] == 0)
).astype(int)

# ── 11. Engineer extra claim-level features ───────────────────────────────────
model_df["HAS_SECONDARY_INSURANCE"] = model_df["SECONDARYPATIENTINSURANCEID"].notna().astype(int)
model_df["NUM_DIAGNOSES"] = model_df[
    ["DIAGNOSIS1","DIAGNOSIS2","DIAGNOSIS3","DIAGNOSIS4",
     "DIAGNOSIS5","DIAGNOSIS6","DIAGNOSIS7","DIAGNOSIS8"]
].notna().sum(axis=1)
model_df["DAYS_TO_SERVICE"] = (
    pd.to_datetime(model_df["SERVICEDATE"]) - pd.to_datetime(model_df["CURRENTILLNESSDATE"])
).dt.days

# ── 12. Final feature set ─────────────────────────────────────────────────────
feature_cols = [
    # claim
    "OUTSTANDING1", "OUTSTANDING2", "OUTSTANDINGP",
    "HAS_SECONDARY_INSURANCE", "NUM_DIAGNOSES", "DAYS_TO_SERVICE",
    "STATUS1", "STATUS2", "STATUSP",
    "HEALTHCARECLAIMTYPEID1", "HEALTHCARECLAIMTYPEID2",
    # encounter
    "ENCOUNTERCLASS", "REASONCODE",
    "BASE_ENCOUNTER_COST", "TOTAL_CLAIM_COST", "PAYER_COVERAGE",
    # patient
    "AGE", "GENDER", "RACE", "ETHNICITY", "STATE", "ZIP",
    "INCOME", "HEALTHCARE_EXPENSES", "HEALTHCARE_COVERAGE",
    # payer
    "PAYER_NAME",
    "PAYER_ENC_DENIAL_RATE", "PAYER_MED_DENIAL_RATE", "PAYER_PROC_DENIAL_RATE",
    "QOLS_AVG", "MEMBER_MONTHS",
    # provider
    "SPECIALITY", "PROV_ENCOUNTER_COUNT", "PROV_PROCEDURE_COUNT",
    # engineered counts
    "CONDITION_COUNT", "PROCEDURE_COUNT", "PROCEDURE_AVG_COST",
    "MEDICATION_COUNT", "MEDICATION_AVG_COST", "MEDICATION_TOTAL_COST",
    "PAYER_TRANSITION_COUNT", "UNIQUE_PAYERS",
    # target
    "DENIED"
]

feature_cols = [c for c in feature_cols if c in model_df.columns]
model_df = model_df[feature_cols].copy()

# ── 13. Fill nulls ────────────────────────────────────────────────────────────
count_cols = ["CONDITION_COUNT", "PROCEDURE_COUNT", "MEDICATION_COUNT",
              "PAYER_TRANSITION_COUNT", "UNIQUE_PAYERS"]
model_df[count_cols] = model_df[count_cols].fillna(0)

print(f"Shape: {model_df.shape}")
print(f"Denial rate: {model_df['DENIED'].mean():.2%}")
print(model_df.dtypes)
model_df.head()
