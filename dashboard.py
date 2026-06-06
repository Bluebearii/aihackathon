"""
═══════════════════════════════════════════════════════════════════════════════
  REVENUE RISK DASHBOARD — Streamlit
  Run with: streamlit run dashboard.py
  Install:  pip install streamlit plotly
═══════════════════════════════════════════════════════════════════════════════
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from math import radians, sin, cos, sqrt, atan2
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score, roc_curve
from sklearn.utils import class_weight
from xgboost import XGBClassifier

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  PAGE CONFIG                                                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title="Revenue Risk Pipeline",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    .stApp {
        font-family: 'DM Sans', sans-serif;
    }

    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #2a2a4a;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }

    .metric-label {
        font-family: 'Space Mono', monospace;
        font-size: 11px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 32px;
        font-weight: 700;
        margin-top: 4px;
    }

    .risk-low { color: #06d6a0; }
    .risk-moderate { color: #f59e0b; }
    .risk-high { color: #f97316; }
    .risk-critical { color: #ef4444; }

    .tier-badge {
        display: inline-block;
        padding: 6px 20px;
        border-radius: 100px;
        font-family: 'Space Mono', monospace;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    .pipeline-header {
        text-align: center;
        padding: 20px 0 10px;
    }

    .pipeline-header h1 {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .pipeline-header p {
        color: #94a3b8;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  PATHS                                                                   ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
SYNTHEA_PATH = "/Users/tommynguyen/codingprojects/AIhackathon/output/csv/"
CLAIMS_PATH  = "/Users/tommynguyen/codingprojects/AIhackathon/csv/"

HOSPITAL_LAT = 32.7767
HOSPITAL_LON = -96.7970


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  HELPER FUNCTIONS                                                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))


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


def calculate_revenue_risk(p_noshow, p_denial, appointment_value, claim_amount):
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
        "p_noshow": round(p_noshow, 4),
        "p_denial": round(p_denial, 4),
        "noshow_loss": round(noshow_loss, 2),
        "denial_loss": round(denial_loss, 2),
        "total_expected_loss": round(total_loss, 2),
        "risk_score": round(risk_score, 1),
        "risk_tier": tier,
    }


def predict_noshow_interactive(age, gender, marital, education, distance, prior_visits, day_of_week, encounter_type):
    p = 0.2019
    if age < 18:    p += 0.0234
    elif age < 30:  p += 0.0452
    elif age < 60:  p -= 0.0064
    else:           p -= 0.0498
    if gender == "F":   p += 0.0012
    elif gender == "M": p -= 0.0023
    if marital == "Single":     p += 0.05
    elif marital == "Divorced": p += 0.04
    elif marital == "Widowed":  p += 0.02
    elif marital == "Married":  p -= 0.03
    else:                       p += 0.01
    if distance > 50:   p += 0.12
    elif distance > 20: p += 0.07
    elif distance > 10: p += 0.03
    if education == "Low":      p += 0.06
    elif education == "Medium": p += 0.02
    elif education == "High":   p -= 0.04
    if prior_visits > 10:   p -= 0.08
    elif prior_visits > 5:  p -= 0.04
    elif prior_visits == 0: p += 0.06
    day_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
    dow = day_map.get(day_of_week, 1)
    if dow == 0:   p += 0.04
    elif dow == 4: p += 0.03
    elif dow == 2: p -= 0.02
    enc = encounter_type.lower()
    if 'wellness' in enc:    p += 0.05
    elif 'urgent' in enc:    p -= 0.10
    elif 'emergency' in enc: p -= 0.15
    return min(max(p, 0.01), 0.95)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  LOAD & TRAIN MODELS (cached so it only runs once)                       ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
@st.cache_data
def load_and_train():
    # ── NO-SHOW MODEL ──────────────────────────────────────────────────────
    patients   = pd.read_csv(os.path.join(SYNTHEA_PATH, "patients.csv"))
    encounters = pd.read_csv(os.path.join(SYNTHEA_PATH, "encounters.csv"))
    encounters = encounters.drop(columns=['BIRTHDATE'], errors='ignore')

    patient_cols = patients[['Id', 'BIRTHDATE', 'GENDER', 'MARITAL', 'INCOME', 'LAT', 'LON']]
    noshow_df = encounters.merge(patient_cols, left_on='PATIENT', right_on='Id')

    noshow_df['BIRTHDATE'] = pd.to_datetime(noshow_df['BIRTHDATE'], errors='coerce')
    noshow_df['AGE']       = ((pd.Timestamp('today') - noshow_df['BIRTHDATE']).dt.days // 365).astype(int)
    noshow_df['MARITAL']   = noshow_df['MARITAL'].fillna('U')
    noshow_df['EDUCATION'] = pd.cut(noshow_df['INCOME'], bins=3, labels=['Low', 'Medium', 'High'], duplicates='drop')
    noshow_df['DISTANCE_KM'] = noshow_df.apply(
        lambda row: haversine(row['LAT'], row['LON'], HOSPITAL_LAT, HOSPITAL_LON), axis=1
    )
    noshow_df = noshow_df.sort_values(['PATIENT', 'START'])
    noshow_df['PRIOR_VISITS']   = noshow_df.groupby('PATIENT').cumcount()
    noshow_df['START']           = pd.to_datetime(noshow_df['START'], errors='coerce')
    noshow_df['DAY_OF_WEEK']    = noshow_df['START'].dt.dayofweek
    noshow_df['MONTH']           = noshow_df['START'].dt.month
    noshow_df['ENCOUNTER_TYPE']  = noshow_df['ENCOUNTERCLASS'].astype(str)

    noshow_df['NO_SHOW_PROB'] = noshow_df.apply(no_show_prob, axis=1)
    noshow_df['NO_SHOW']      = (np.random.RandomState(42).rand(len(noshow_df)) < noshow_df['NO_SHOW_PROB']).astype(int)

    ns_features = ['AGE', 'GENDER', 'MARITAL', 'EDUCATION', 'DISTANCE_KM',
                   'PRIOR_VISITS', 'DAY_OF_WEEK', 'MONTH', 'ENCOUNTER_TYPE']
    ns_model_df = noshow_df[ns_features + ['NO_SHOW']].dropna().copy()
    for col in ['GENDER', 'MARITAL', 'EDUCATION', 'ENCOUNTER_TYPE']:
        ns_model_df[col] = LabelEncoder().fit_transform(ns_model_df[col].astype(str))

    X_ns = ns_model_df[ns_features]
    y_ns = ns_model_df['NO_SHOW']
    X_ns_train, X_ns_test, y_ns_train, y_ns_test = train_test_split(X_ns, y_ns, test_size=0.2, random_state=42)

    classes = np.array([0, 1])
    wts = class_weight.compute_class_weight('balanced', classes=classes, y=y_ns_train)
    sw = np.array([dict(zip(classes, wts))[l] for l in y_ns_train])

    ns_model = GradientBoostingClassifier(
        n_estimators=200, learning_rate=0.05, max_depth=4, subsample=0.8, random_state=42
    )
    ns_model.fit(X_ns_train, y_ns_train, sample_weight=sw)
    y_ns_proba = ns_model.predict_proba(X_ns_test)[:, 1]
    y_ns_pred  = ns_model.predict(X_ns_test)
    ns_auc = roc_auc_score(y_ns_test, y_ns_proba)
    ns_fpr, ns_tpr, _ = roc_curve(y_ns_test, y_ns_proba)
    ns_importance = pd.Series(ns_model.feature_importances_, index=ns_features).sort_values(ascending=False)

    # ── CLAIM DENIAL MODEL ─────────────────────────────────────────────────
    claims_dfs = {}
    for file in os.listdir(CLAIMS_PATH):
        if file.endswith('.csv'):
            name = file.replace('.csv', '')
            claims_dfs[name] = pd.read_csv(os.path.join(CLAIMS_PATH, file))

    claim_feature_list = [
        "payer_type", "provider_specialty", "primary_icd10_dx",
        "prior_auth_required", "prior_auth_obtained",
        "documentation_completeness", "claim_amount_usd", "cpt_code"
    ]
    string_cols = ["payer_type", "provider_specialty", "primary_icd10_dx", "cpt_code"]

    claims_dfs["claims_main"]["binary_deny_outcome"] = np.where(
        claims_dfs["claims_main"]["outcome"] == 'denied', 1, 0
    )
    claims_encoded = pd.get_dummies(claims_dfs["claims_main"], columns=string_cols)
    y_cd = claims_encoded["binary_deny_outcome"]
    X_cd = claims_encoded.select_dtypes(include=['number', 'bool']).drop(["binary_deny_outcome"], axis=1)

    X_cd_train, X_cd_test, y_cd_train, y_cd_test = train_test_split(X_cd, y_cd, test_size=0.2, random_state=42)
    cd_model = XGBClassifier(random_state=42, eval_metric='logloss')
    cd_model.fit(X_cd_train, y_cd_train)
    y_cd_proba = cd_model.predict_proba(X_cd_test)[:, 1]
    y_cd_pred  = cd_model.predict(X_cd_test)
    cd_auc = roc_auc_score(y_cd_test, y_cd_proba)
    cd_fpr, cd_tpr, _ = roc_curve(y_cd_test, y_cd_proba)

    cd_importance = pd.DataFrame({"feature": X_cd.columns, "importance": cd_model.feature_importances_})
    def get_group(fn):
        for orig in claim_feature_list:
            if fn.startswith(orig): return orig
        return fn
    cd_importance["group"] = cd_importance["feature"].apply(get_group)
    cd_grouped = cd_importance.groupby("group")["importance"].sum().sort_values(ascending=False)

    avg_denial_prob  = y_cd_proba.mean()
    avg_claim_amount = claims_dfs["claims_main"]["claim_amount_usd"].mean()

    # ── SCORE ALL TEST PATIENTS ────────────────────────────────────────────
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

    return {
        "ns_auc": ns_auc, "cd_auc": cd_auc,
        "ns_fpr": ns_fpr, "ns_tpr": ns_tpr,
        "cd_fpr": cd_fpr, "cd_tpr": cd_tpr,
        "ns_importance": ns_importance,
        "cd_grouped": cd_grouped,
        "risk_df": risk_df,
        "avg_denial_prob": avg_denial_prob,
        "avg_claim_amount": avg_claim_amount,
        "noshow_rate": noshow_df['NO_SHOW'].mean(),
        "denial_rate": claims_dfs["claims_main"]["binary_deny_outcome"].mean(),
        "total_records_ns": len(noshow_df),
        "total_records_cd": len(claims_dfs["claims_main"]),
        "y_ns_test": y_ns_test, "y_ns_pred": y_ns_pred,
        "y_cd_test": y_cd_test, "y_cd_pred": y_cd_pred,
    }


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  LOAD DATA                                                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
with st.spinner("Training models... (this only happens once)"):
    data = load_and_train()


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  SIDEBAR                                                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
with st.sidebar:
    st.markdown("## 🏥 Revenue Risk Pipeline")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["📊 Dashboard Overview", "🎯 Patient Risk Predictor", "📈 Model Performance", "🔍 Feature Analysis"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#94a3b8; font-size:12px;'>"
        "Synthea + Kaggle Calibrated<br>Dallas, TX Region</div>",
        unsafe_allow_html=True
    )


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  PAGE 1: DASHBOARD OVERVIEW                                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
if page == "📊 Dashboard Overview":
    st.markdown(
        "<div class='pipeline-header'>"
        "<h1>🏥 Revenue Risk Pipeline</h1>"
        "<p>Combining No-Show + Claim Denial prediction into one unified risk score</p>"
        "</div>",
        unsafe_allow_html=True
    )

    # ── Top metrics ────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("No-Show AUC-ROC", f"{data['ns_auc']:.4f}")
    with col2:
        st.metric("Denial AUC-ROC", f"{data['cd_auc']:.4f}")
    with col3:
        st.metric("Patients Scored", f"{len(data['risk_df']):,}")
    with col4:
        st.metric("Total Expected Loss", f"${data['risk_df']['total_expected_loss'].sum():,.0f}")

    st.markdown("---")

    # ── Pipeline diagram ───────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 📋 Pipeline Flow")
        st.markdown("""
        ```
        New Patient Appointment
            │
            ├── No-Show Model ──→ P(no_show)
            │   Revenue lost BEFORE work
            │
            ├── Claim Denial Model ──→ P(denial)
            │   Revenue lost AFTER work
            │
            └── Combined Risk Score
                Expected $ Loss + Risk Tier
                → Drives intervention strategy
        ```
        """)

        st.markdown("### 💡 Formula")
        st.latex(r"\text{Loss} = P(\text{no-show}) \times V + (1 - P(\text{no-show})) \times P(\text{denial}) \times C")
        st.caption("V = appointment value, C = claim amount")

    with col_right:
        st.markdown("### 🎯 Risk Tier Distribution")
        tier_counts = data['risk_df']['risk_tier'].value_counts()
        tier_order = ['LOW', 'MODERATE', 'HIGH', 'CRITICAL']
        tier_colors = {'LOW': '#06d6a0', 'MODERATE': '#f59e0b', 'HIGH': '#f97316', 'CRITICAL': '#ef4444'}

        fig_tier = go.Figure(data=[
            go.Bar(
                x=[tier_counts.get(t, 0) for t in tier_order],
                y=tier_order,
                orientation='h',
                marker_color=[tier_colors[t] for t in tier_order],
                text=[f"{tier_counts.get(t, 0):,} ({tier_counts.get(t, 0)/len(data['risk_df'])*100:.1f}%)" for t in tier_order],
                textposition='auto',
            )
        ])
        fig_tier.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Patients", yaxis_title="",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig_tier, use_container_width=True)

        # ── Actions table ──────────────────────────────────────────────────
        st.markdown("### 🔔 Recommended Actions")
        actions_df = pd.DataFrame({
            "Tier": tier_order,
            "Patients": [tier_counts.get(t, 0) for t in tier_order],
            "Action": [
                "Email confirmation only",
                "SMS reminder 24h before",
                "SMS + phone 48h/24h. Pre-verify docs.",
                "Phone 72h/48h/24h. Verify insurance. Flag prior auth.",
            ]
        })
        st.dataframe(actions_df, hide_index=True, use_container_width=True)

    # ── Risk score distribution ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Risk Score Distribution")
    fig_hist = px.histogram(
        data['risk_df'], x='risk_score', nbins=50,
        color_discrete_sequence=['#818cf8'],
        labels={'risk_score': 'Risk Score (0-100)', 'count': 'Patients'},
    )
    fig_hist.add_vline(x=55, line_dash="dash", line_color="#f59e0b", annotation_text="MODERATE")
    fig_hist.add_vline(x=65, line_dash="dash", line_color="#f97316", annotation_text="HIGH")
    fig_hist.add_vline(x=72, line_dash="dash", line_color="#ef4444", annotation_text="CRITICAL")
    fig_hist.update_layout(
        height=350, margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig_hist, use_container_width=True)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  PAGE 2: PATIENT RISK PREDICTOR                                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
elif page == "🎯 Patient Risk Predictor":
    st.markdown("## 🎯 Patient Risk Predictor")
    st.markdown("Enter patient details to calculate their combined revenue risk score.")
    st.markdown("---")

    col_input, col_spacer, col_result = st.columns([2, 0.3, 2])

    with col_input:
        st.markdown("### Patient Information")
        age = st.slider("Age", 0, 100, 28)
        gender = st.selectbox("Gender", ["Male", "Female"])
        marital = st.selectbox("Marital Status", ["Single", "Married", "Divorced", "Widowed", "Unknown"])
        education = st.selectbox("Education / Income Level", ["Low", "Medium", "High"])
        distance = st.slider("Distance to Hospital (km)", 1, 100, 15)
        prior_visits = st.slider("Prior Visits", 0, 30, 2)
        day_of_week = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        encounter_type = st.selectbox("Encounter Type", ["Ambulatory", "Wellness", "Outpatient", "Urgent Care", "Emergency", "Inpatient"])

        denial_override = st.slider("Claim Denial Probability (%)", 1, 95, int(data['avg_denial_prob'] * 100))

    with col_result:
        st.markdown("### Risk Assessment")

        gender_code = "M" if gender == "Male" else "F"
        p_ns = predict_noshow_interactive(age, gender_code, marital, education, distance, prior_visits, day_of_week, encounter_type.lower())
        p_dn = denial_override / 100.0
        risk = calculate_revenue_risk(p_ns, p_dn, data['avg_claim_amount'], data['avg_claim_amount'])

        tier_colors_map = {"LOW": "#06d6a0", "MODERATE": "#f59e0b", "HIGH": "#f97316", "CRITICAL": "#ef4444"}
        tier_color = tier_colors_map[risk['risk_tier']]

        # ── Gauge chart ────────────────────────────────────────────────────
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk['risk_score'],
            number={'suffix': '/100', 'font': {'size': 40, 'family': 'Space Mono'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': tier_color},
                'bgcolor': 'rgba(0,0,0,0)',
                'steps': [
                    {'range': [0, 55], 'color': 'rgba(6,214,160,0.15)'},
                    {'range': [55, 65], 'color': 'rgba(245,158,11,0.15)'},
                    {'range': [65, 72], 'color': 'rgba(249,115,24,0.15)'},
                    {'range': [72, 100], 'color': 'rgba(239,68,68,0.15)'},
                ],
                'threshold': {
                    'line': {'color': tier_color, 'width': 4},
                    'thickness': 0.8,
                    'value': risk['risk_score']
                },
            },
        ))
        fig_gauge.update_layout(
            height=250, margin=dict(l=20, r=20, t=30, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown(
            f"<div style='text-align:center;'>"
            f"<span class='tier-badge' style='background:{tier_color}22; color:{tier_color}; border:1px solid {tier_color}66;'>"
            f"{risk['risk_tier']} RISK</span></div>",
            unsafe_allow_html=True
        )

        st.markdown("---")

        # ── Risk breakdown ─────────────────────────────────────────────────
        c1, c2 = st.columns(2)
        with c1:
            st.metric("P(No-Show)", f"{risk['p_noshow']:.0%}")
            st.metric("No-Show Loss", f"${risk['noshow_loss']:,.2f}")
        with c2:
            st.metric("P(Denial)", f"{risk['p_denial']:.0%}")
            st.metric("Denial Loss", f"${risk['denial_loss']:,.2f}")

        st.metric("Total Expected Loss", f"${risk['total_expected_loss']:,.2f}")

        st.markdown("---")

        # ── Recommendation ─────────────────────────────────────────────────
        recommendations = {
            "LOW": "✅ **Low risk** — Standard email confirmation sufficient. No additional intervention needed.",
            "MODERATE": "⚠️ **Moderate risk** — Send automated SMS reminder 24h before appointment. Standard insurance verification.",
            "HIGH": "🔶 **High risk** — SMS + phone reminder 48h/24h before. Pre-verify documentation. Check prior auth status.",
            "CRITICAL": "🔴 **Critical risk** — Phone call + SMS 72h/48h/24h before. Verify insurance pre-visit. Flag for prior auth review. Consider overbooking slot.",
        }
        st.info(recommendations[risk['risk_tier']])

        # ── Factor breakdown ───────────────────────────────────────────────
        st.markdown("#### Contributing Factors")
        factors = {
            "Age": f"+{0.0452*100:.1f}%" if age < 30 else f"-{0.0498*100:.1f}%" if age >= 60 else "±0%",
            "Distance": f"+{12}%" if distance > 50 else f"+{7}%" if distance > 20 else f"+{3}%" if distance > 10 else "±0%",
            "Marital": f"+5%" if marital == "Single" else f"-3%" if marital == "Married" else "+4%" if marital == "Divorced" else "+2%",
            "Encounter": f"+5%" if "wellness" in encounter_type.lower() else f"-10%" if "urgent" in encounter_type.lower() else f"-15%" if "emergency" in encounter_type.lower() else "±0%",
            "Prior Visits": f"-8%" if prior_visits > 10 else f"-4%" if prior_visits > 5 else f"+6%" if prior_visits == 0 else "±0%",
        }
        for factor, impact in factors.items():
            is_risk = impact.startswith("+")
            color = "#ef4444" if is_risk else "#06d6a0" if impact.startswith("-") else "#94a3b8"
            st.markdown(f"<span style='color:#94a3b8;'>{factor}:</span> <span style='color:{color}; font-family:Space Mono; font-weight:700;'>{impact}</span>", unsafe_allow_html=True)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  PAGE 3: MODEL PERFORMANCE                                              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
elif page == "📈 Model Performance":
    st.markdown("## 📈 Model Performance")
    st.markdown("---")

    tab_ns, tab_cd = st.tabs(["🚫 No-Show Model", "📋 Claim Denial Model"])

    with tab_ns:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("AUC-ROC", f"{data['ns_auc']:.4f}")
        with col2:
            st.metric("No-Show Rate", f"{data['noshow_rate']:.2%}")
        with col3:
            st.metric("Total Records", f"{data['total_records_ns']:,}")

        col_roc, col_report = st.columns(2)

        with col_roc:
            st.markdown("#### ROC Curve")
            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(x=data['ns_fpr'], y=data['ns_tpr'], mode='lines',
                                          name=f"No-Show (AUC={data['ns_auc']:.4f})", line=dict(color='#06d6a0', width=2)))
            fig_roc.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', name='Random',
                                          line=dict(color='#94a3b8', dash='dash', width=1)))
            fig_roc.update_layout(
                height=350, margin=dict(l=0, r=0, t=10, b=0),
                xaxis_title="False Positive Rate", yaxis_title="True Positive Rate",
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="DM Sans"), legend=dict(x=0.5, y=0.1),
            )
            st.plotly_chart(fig_roc, use_container_width=True)

        with col_report:
            st.markdown("#### Classification Report")
            report = classification_report(data['y_ns_test'], data['y_ns_pred'],
                                            target_names=['Show', 'No-Show'], output_dict=True)
            report_df = pd.DataFrame(report).T.iloc[:2][['precision', 'recall', 'f1-score', 'support']]
            report_df = report_df.round(3)
            st.dataframe(report_df, use_container_width=True)

            st.markdown("#### Data Sources")
            st.markdown("""
            - **Training data**: Synthea synthetic patients (Texas)
            - **Labels**: Calibrated from 110K real Brazilian appointments (Kaggle)
            - **Algorithm**: Gradient Boosted Classifier, class-balanced
            """)

    with tab_cd:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("AUC-ROC", f"{data['cd_auc']:.4f}")
        with col2:
            st.metric("Denial Rate", f"{data['denial_rate']:.2%}")
        with col3:
            st.metric("Total Claims", f"{data['total_records_cd']:,}")

        col_roc, col_report = st.columns(2)

        with col_roc:
            st.markdown("#### ROC Curve")
            fig_roc2 = go.Figure()
            fig_roc2.add_trace(go.Scatter(x=data['cd_fpr'], y=data['cd_tpr'], mode='lines',
                                           name=f"Denial (AUC={data['cd_auc']:.4f})", line=dict(color='#f472b6', width=2)))
            fig_roc2.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', name='Random',
                                           line=dict(color='#94a3b8', dash='dash', width=1)))
            fig_roc2.update_layout(
                height=350, margin=dict(l=0, r=0, t=10, b=0),
                xaxis_title="False Positive Rate", yaxis_title="True Positive Rate",
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="DM Sans"), legend=dict(x=0.5, y=0.1),
            )
            st.plotly_chart(fig_roc2, use_container_width=True)

        with col_report:
            st.markdown("#### Classification Report")
            report2 = classification_report(data['y_cd_test'], data['y_cd_pred'],
                                             target_names=['Approved', 'Denied'], output_dict=True)
            report_df2 = pd.DataFrame(report2).T.iloc[:2][['precision', 'recall', 'f1-score', 'support']]
            report_df2 = report_df2.round(3)
            st.dataframe(report_df2, use_container_width=True)

            st.markdown("#### Data Sources")
            st.markdown("""
            - **Training data**: Kaggle claims dataset
            - **Labels**: Real denial outcomes
            - **Algorithm**: XGBoost Classifier
            """)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  PAGE 4: FEATURE ANALYSIS                                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
elif page == "🔍 Feature Analysis":
    st.markdown("## 🔍 Feature Analysis")
    st.markdown("---")

    col_ns, col_cd = st.columns(2)

    with col_ns:
        st.markdown("### No-Show Model Features")
        fig_ns = go.Figure(go.Bar(
            x=data['ns_importance'].values,
            y=data['ns_importance'].index,
            orientation='h',
            marker_color='#06d6a0',
            text=[f"{v:.1%}" for v in data['ns_importance'].values],
            textposition='auto',
        ))
        fig_ns.update_layout(
            height=400, margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Importance", yaxis_title="",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="DM Sans"),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_ns, use_container_width=True)

    with col_cd:
        st.markdown("### Claim Denial Features")
        fig_cd = go.Figure(go.Bar(
            x=data['cd_grouped'].values,
            y=data['cd_grouped'].index,
            orientation='h',
            marker_color='#f472b6',
            text=[f"{v:.1%}" for v in data['cd_grouped'].values],
            textposition='auto',
        ))
        fig_cd.update_layout(
            height=400, margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Importance", yaxis_title="",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="DM Sans"),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_cd, use_container_width=True)

    # ── Key Insights ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💡 Key Insights")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        #### No-Show Drivers
        **Encounter type** is the strongest predictor.
        Emergency patients almost always show.
        Wellness patients are most likely to skip.
        """)
    with c2:
        st.markdown("""
        #### Claim Denial Drivers
        **Prior authorization** and **documentation completeness**
        dominate. Administrative factors matter more than
        clinical ones for getting paid.
        """)
    with c3:
        st.markdown("""
        #### Gender ≈ Irrelevant
        Confirmed by both models and the Kaggle calibration
        data. Gender should not drive clinical or billing
        intervention decisions.
        """)

    # ── Calibration Sources ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📚 Calibration Sources")
    sources = pd.DataFrame({
        "Feature": ["Age, Gender", "Base rate (20.19%)", "Distance, Education", "Marital, Day, Encounter"],
        "Source": [
            "Kaggle Medical Appointments (110K records, Brazil)",
            "Kaggle Medical Appointments dataset",
            "Healthcare no-show literature (Dantas et al. 2018)",
            "Healthcare operations research estimates",
        ],
        "Type": ["Empirical", "Empirical", "Literature", "Literature"],
    })
    st.dataframe(sources, hide_index=True, use_container_width=True)
