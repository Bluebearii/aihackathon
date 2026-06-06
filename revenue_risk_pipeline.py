"""
═══════════════════════════════════════════════════════════════════════════════
  REVENUE RISK PIPELINE
  Combines No-Show Prediction + Claim Denial Prediction into one risk score.

  No-Show   → Revenue lost BEFORE doing any work (empty appointment slot)
  Denial    → Revenue lost AFTER doing the work (claim writeoff)

  Combined  → Expected Revenue Loss ($) per patient appointment
═══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np
import os
from math import radians, sin, cos, sqrt, atan2
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.utils import class_weight
from xgboost import XGBClassifier


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  PATHS — Update these to match your setup                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
SYNTHEA_PATH = "/Users/tommynguyen/codingprojects/AIhackathon/output/csv/"
CLAIMS_PATH  = "/Users/tommynguyen/codingprojects/AIhackathon/csv/"
OUTPUT_PATH  = "/Users/tommynguyen/codingprojects/AIhackathon/"

HOSPITAL_LAT = 32.7767   # Dallas, TX
HOSPITAL_LON = -96.7970


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  MODEL 1: NO-SHOW PREDICTOR                                             ║
# ║  Revenue lost BEFORE work — empty slots, wasted staff time               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
print("=" * 70)
print("MODEL 1: NO-SHOW PREDICTOR")
print("=" * 70)

# ── Load Synthea data ──────────────────────────────────────────────────────
patients   = pd.read_csv(os.path.join(SYNTHEA_PATH, "patients.csv"))
encounters = pd.read_csv(os.path.join(SYNTHEA_PATH, "encounters.csv"))
encounters = encounters.drop(columns=['BIRTHDATE'], errors='ignore')

patient_cols = patients[['Id', 'BIRTHDATE', 'GENDER', 'MARITAL', 'INCOME', 'LAT', 'LON']]
noshow_df = encounters.merge(patient_cols, left_on='PATIENT', right_on='Id')

# ── Feature engineering ────────────────────────────────────────────────────
noshow_df['BIRTHDATE'] = pd.to_datetime(noshow_df['BIRTHDATE'], errors='coerce')
noshow_df['AGE']       = ((pd.Timestamp('today') - noshow_df['BIRTHDATE']).dt.days // 365).astype(int)
noshow_df['MARITAL']   = noshow_df['MARITAL'].fillna('U')
noshow_df['EDUCATION'] = pd.cut(noshow_df['INCOME'], bins=3, labels=['Low', 'Medium', 'High'], duplicates='drop')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

noshow_df['DISTANCE_KM'] = noshow_df.apply(
    lambda row: haversine(row['LAT'], row['LON'], HOSPITAL_LAT, HOSPITAL_LON), axis=1
)

noshow_df = noshow_df.sort_values(['PATIENT', 'START'])
noshow_df['PRIOR_VISITS']   = noshow_df.groupby('PATIENT').cumcount()
noshow_df['START']           = pd.to_datetime(noshow_df['START'], errors='coerce')
noshow_df['DAY_OF_WEEK']    = noshow_df['START'].dt.dayofweek
noshow_df['MONTH']           = noshow_df['START'].dt.month
noshow_df['ENCOUNTER_TYPE']  = noshow_df['ENCOUNTERCLASS'].astype(str)

# ── Simulate no-show label (calibrated from Kaggle real data) ──────────────
def no_show_prob(row):
    p = 0.2019
    if row['AGE'] < 18:    p += 0.0234
    elif row['AGE'] < 30:  p += 0.0452
    elif row['AGE'] < 60:  p -= 0.0064
    else:                  p -= 0.0498
    if row['GENDER'] == 'F':   p += 0.0012
    elif row['GENDER'] == 'M': p -= 0.0023
    if row['MARITAL'] == 'S':   p += 0.05
    elif row['MARITAL'] == 'D': p += 0.04
    elif row['MARITAL'] == 'W': p += 0.02
    elif row['MARITAL'] == 'M': p -= 0.03
    elif row['MARITAL'] == 'U': p += 0.01
    if row['DISTANCE_KM'] > 50:   p += 0.12
    elif row['DISTANCE_KM'] > 20: p += 0.07
    elif row['DISTANCE_KM'] > 10: p += 0.03
    if str(row['EDUCATION']) == 'Low':      p += 0.06
    elif str(row['EDUCATION']) == 'Medium': p += 0.02
    elif str(row['EDUCATION']) == 'High':   p -= 0.04
    if row['PRIOR_VISITS'] > 10:   p -= 0.08
    elif row['PRIOR_VISITS'] > 5:  p -= 0.04
    elif row['PRIOR_VISITS'] == 0: p += 0.06
    if row['DAY_OF_WEEK'] == 0:   p += 0.04
    elif row['DAY_OF_WEEK'] == 4: p += 0.03
    elif row['DAY_OF_WEEK'] == 2: p -= 0.02
    enc = row['ENCOUNTER_TYPE'].lower()
    if 'wellness' in enc:    p += 0.05
    elif 'urgent' in enc:    p -= 0.10
    elif 'emergency' in enc: p -= 0.15
    return min(max(p, 0.01), 0.95)

noshow_df['NO_SHOW_PROB'] = noshow_df.apply(no_show_prob, axis=1)
noshow_df['NO_SHOW']      = (np.random.rand(len(noshow_df)) < noshow_df['NO_SHOW_PROB']).astype(int)

# ── Train no-show model ────────────────────────────────────────────────────
ns_features = ['AGE', 'GENDER', 'MARITAL', 'EDUCATION', 'DISTANCE_KM',
               'PRIOR_VISITS', 'DAY_OF_WEEK', 'MONTH', 'ENCOUNTER_TYPE']

ns_model_df = noshow_df[ns_features + ['NO_SHOW']].dropna().copy()
ns_label_encoders = {}
for col in ['GENDER', 'MARITAL', 'EDUCATION', 'ENCOUNTER_TYPE']:
    le = LabelEncoder()
    ns_model_df[col] = le.fit_transform(ns_model_df[col].astype(str))
    ns_label_encoders[col] = le

X_ns = ns_model_df[ns_features]
y_ns = ns_model_df['NO_SHOW']
X_ns_train, X_ns_test, y_ns_train, y_ns_test = train_test_split(X_ns, y_ns, test_size=0.2, random_state=42)

classes = np.array([0, 1])
weights = class_weight.compute_class_weight('balanced', classes=classes, y=y_ns_train)
sample_weights = np.array([dict(zip(classes, weights))[l] for l in y_ns_train])

noshow_model = GradientBoostingClassifier(
    n_estimators=200, learning_rate=0.05, max_depth=4, subsample=0.8, random_state=42
)
noshow_model.fit(X_ns_train, y_ns_train, sample_weight=sample_weights)

y_ns_pred  = noshow_model.predict(X_ns_test)
y_ns_proba = noshow_model.predict_proba(X_ns_test)[:, 1]

print(f"\nNo-Show Model Results:")
print(classification_report(y_ns_test, y_ns_pred, target_names=['Show', 'No-Show']))
print(f"AUC-ROC: {roc_auc_score(y_ns_test, y_ns_proba):.4f}")

# ── No-show feature importance ─────────────────────────────────────────────
ns_importance = pd.Series(noshow_model.feature_importances_, index=ns_features).sort_values(ascending=False)
print(f"\nNo-Show Feature Importance:")
for feat, score in ns_importance.items():
    bar = '█' * int(score * 100)
    print(f"  {feat:<18} {score:.4f}  {bar}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  MODEL 2: CLAIM DENIAL PREDICTOR                                        ║
# ║  Revenue lost AFTER work — claim writeoffs, rework costs                 ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
print("\n" + "=" * 70)
print("MODEL 2: CLAIM DENIAL PREDICTOR")
print("=" * 70)

# ── Load claims data ───────────────────────────────────────────────────────
claims_dfs = {}
for file in os.listdir(CLAIMS_PATH):
    if file.endswith('.csv'):
        name = file.replace('.csv', '')
        claims_dfs[name] = pd.read_csv(os.path.join(CLAIMS_PATH, file))

claim_feature_list = [
    "payer_type", "provider_specialty",
    "primary_icd10_dx", "prior_auth_required",
    "prior_auth_obtained", "documentation_completeness",
    "claim_amount_usd", "cpt_code"
]
string_cols = ["payer_type", "provider_specialty", "primary_icd10_dx", "cpt_code"]

claims_dfs["claims_main"]["binary_deny_outcome"] = np.where(
    claims_dfs["claims_main"]["outcome"] == 'denied', 1, 0
)
claims_encoded = pd.get_dummies(claims_dfs["claims_main"], columns=string_cols)

y_cd = claims_encoded["binary_deny_outcome"]
X_cd = claims_encoded.select_dtypes(include=['number', 'bool']).drop(["binary_deny_outcome"], axis=1)

X_cd_train, X_cd_test, y_cd_train, y_cd_test = train_test_split(X_cd, y_cd, test_size=0.2, random_state=42)

denial_model = XGBClassifier(random_state=42, eval_metric='logloss')
denial_model.fit(X_cd_train, y_cd_train)

y_cd_pred  = denial_model.predict(X_cd_test)
y_cd_proba = denial_model.predict_proba(X_cd_test)[:, 1]

print(f"\nClaim Denial Model Results:")
print(classification_report(y_cd_test, y_cd_pred, target_names=['Approved', 'Denied']))
print(f"AUC-ROC: {roc_auc_score(y_cd_test, y_cd_proba):.4f}")

# ── Denial feature importance ──────────────────────────────────────────────
cd_importance = pd.DataFrame({
    "feature": X_cd.columns,
    "importance": denial_model.feature_importances_
})
def get_group(feature_name):
    for original in claim_feature_list:
        if feature_name.startswith(original):
            return original
    return feature_name
cd_importance["group"] = cd_importance["feature"].apply(get_group)
cd_grouped = cd_importance.groupby("group")["importance"].sum().sort_values(ascending=False)

print(f"\nClaim Denial Feature Importance (grouped):")
for feat, score in cd_grouped.items():
    bar = '█' * int(score * 100)
    print(f"  {feat:<30} {score:.4f}  {bar}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  COMBINED PIPELINE: REVENUE RISK SCORE                                   ║
# ║                                                                          ║
# ║  When appointment_value = claim_amount, the formula simplifies to:       ║
# ║  risk_score = (P(no_show) + (1 - P(no_show)) × P(denial)) × 100        ║
# ║                                                                          ║
# ║  This is purely probability-driven — no dollar amount distortion.        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
print("\n" + "=" * 70)
print("COMBINED PIPELINE: REVENUE RISK SCORE")
print("=" * 70)


def calculate_revenue_risk(p_noshow, p_denial, appointment_value, claim_amount):
    """
    Calculate expected revenue loss from both risk sources.

    Args:
        p_noshow:          Probability patient doesn't show (0-1)
        p_denial:          Probability claim gets denied (0-1)
        appointment_value: Revenue from the appointment slot ($)
        claim_amount:      Total claim amount to be submitted ($)

    Returns:
        dict with risk breakdown
    """
    noshow_loss = p_noshow * appointment_value
    denial_loss = (1 - p_noshow) * p_denial * claim_amount
    total_loss  = noshow_loss + denial_loss

    max_possible_loss = max(appointment_value, claim_amount)
    risk_score = min((total_loss / max_possible_loss) * 100, 100) if max_possible_loss > 0 else 0

    if risk_score > 72:
        tier = "CRITICAL"
    elif risk_score > 65:
        tier = "HIGH"
    elif risk_score > 55:
        tier = "MODERATE"
    else:
        tier = "LOW"

    return {
        "p_noshow":            round(p_noshow, 4),
        "p_denial":            round(p_denial, 4),
        "appointment_value":   round(appointment_value, 2),
        "noshow_loss":         round(noshow_loss, 2),
        "denial_loss":         round(denial_loss, 2),
        "total_expected_loss": round(total_loss, 2),
        "risk_score":          round(risk_score, 1),
        "risk_tier":           tier,
    }


# ── Demo: Score example patient scenarios ──────────────────────────────────
print(f"\n{'─' * 70}")
print(f"  EXAMPLE PATIENT SCENARIOS")
print(f"{'─' * 70}")

scenarios = [
    {
        "name": "Low Risk: Married 45yo, Urgent Care",
        "p_noshow": 0.10,
        "p_denial": 0.05,
    },
    {
        "name": "Moderate Risk: Single 25yo, Wellness",
        "p_noshow": 0.30,
        "p_denial": 0.15,
    },
    {
        "name": "High Risk: Single 22yo, Ambulatory",
        "p_noshow": 0.45,
        "p_denial": 0.35,
    },
    {
        "name": "Critical Risk: Divorced 30yo, No Prior Auth",
        "p_noshow": 0.55,
        "p_denial": 0.60,
    },
]

for s in scenarios:
    # Use matching values so risk score = pure probability
    result = calculate_revenue_risk(s["p_noshow"], s["p_denial"], 500, 500)
    print(f"\n  {s['name']}")
    print(f"    P(no-show):          {result['p_noshow']:.0%}")
    print(f"    P(denial):           {result['p_denial']:.0%}")
    print(f"    Combined risk score: {result['risk_score']}/100 → {result['risk_tier']}")
    print(f"    No-show loss:        ${result['noshow_loss']:>8,.2f}")
    print(f"    Denial loss:         ${result['denial_loss']:>8,.2f}")
    print(f"    Total expected loss: ${result['total_expected_loss']:>8,.2f}")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  SCORE ALL PATIENTS IN TEST SET                                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
print(f"\n{'=' * 70}")
print("SCORING ALL PATIENTS IN TEST SET")
print(f"{'=' * 70}")

avg_denial_prob  = y_cd_proba.mean()
avg_claim_amount = claims_dfs["claims_main"]["claim_amount_usd"].mean()

print(f"\n  Avg denial probability (from model): {avg_denial_prob:.2%}")
print(f"  Avg claim amount (from data):        ${avg_claim_amount:,.2f}")
print(f"  Appointment value:                   ${avg_claim_amount:,.2f} (matched to claim)")

# Score each patient — appointment_value = claim_amount for clean risk scores
risk_results = []
for i in range(len(X_ns_test)):
    result = calculate_revenue_risk(
        p_noshow=y_ns_proba[i],
        p_denial=avg_denial_prob,
        appointment_value=avg_claim_amount,
        claim_amount=avg_claim_amount,
    )
    risk_results.append(result)

risk_df = pd.DataFrame(risk_results)

# ── Risk score diagnostics ─────────────────────────────────────────────────
print(f"\n── Risk Score Distribution ────────────────────────────")
print(f"  Min:    {risk_df['risk_score'].min():.1f}")
print(f"  25th:   {risk_df['risk_score'].quantile(0.25):.1f}")
print(f"  Median: {risk_df['risk_score'].quantile(0.50):.1f}")
print(f"  75th:   {risk_df['risk_score'].quantile(0.75):.1f}")
print(f"  90th:   {risk_df['risk_score'].quantile(0.90):.1f}")
print(f"  Max:    {risk_df['risk_score'].max():.1f}")

# ── Risk tier distribution ─────────────────────────────────────────────────
print(f"\n── Risk Tier Distribution ─────────────────────────────")
tier_dist = risk_df['risk_tier'].value_counts()
for tier in ['LOW', 'MODERATE', 'HIGH', 'CRITICAL']:
    count = tier_dist.get(tier, 0)
    pct   = count / len(risk_df) * 100
    bar   = '█' * int(pct / 2)
    print(f"  {tier:<10} {count:>6,} ({pct:>5.1f}%)  {bar}")

# ── Financial impact summary ───────────────────────────────────────────────
print(f"\n── Financial Impact Summary ───────────────────────────")
print(f"  Total patients scored:       {len(risk_df):,}")
print(f"  Avg expected loss/patient:   ${risk_df['total_expected_loss'].mean():,.2f}")
print(f"  Median expected loss:        ${risk_df['total_expected_loss'].median():,.2f}")
print(f"  Total expected loss:         ${risk_df['total_expected_loss'].sum():,.2f}")
print(f"  Avg risk score:              {risk_df['risk_score'].mean():.1f} / 100")
print(f"  Highest single-patient risk: ${risk_df['total_expected_loss'].max():,.2f}")

# ── Actionable recommendations ─────────────────────────────────────────────
print(f"\n── Recommended Actions by Tier ────────────────────────")
actions = {
    "CRITICAL": "Phone call + SMS 72h/48h/24h. Verify insurance pre-visit. Flag for prior auth review. Consider overbooking slot.",
    "HIGH":     "SMS + phone reminder 48h/24h. Pre-verify documentation. Check prior auth status.",
    "MODERATE": "Automated SMS reminder 24h before. Standard insurance verification.",
    "LOW":      "Standard email confirmation. No additional intervention needed.",
}
for tier, action in actions.items():
    count = tier_dist.get(tier, 0)
    print(f"  {tier:<10} ({count:>5,} patients) → {action}")

# ── Save output ────────────────────────────────────────────────────────────
output_file = os.path.join(OUTPUT_PATH, "revenue_risk_scores.csv")
risk_df.to_csv(output_file, index=False)
print(f"\nRisk scores saved to: {output_file}")

print(f"\n{'=' * 70}")
print("PIPELINE COMPLETE")
print(f"{'=' * 70}")
