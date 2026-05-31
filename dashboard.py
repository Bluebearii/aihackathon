"""
CareFlow AI — Interactive Streamlit Dashboard
================================================
Full interactive dashboard with 29+ Plotly charts from the CMS
Medicare Physician & Other Practitioners dataset.
Each chart includes detailed analysis and problem identification.

Usage:
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from sqlalchemy import create_engine

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareFlow AI — CMS Medicare Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(42, 157, 143, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0.3rem 0 0 0;
    }

    .kpi-card {
        background: linear-gradient(145deg, #1a1f2e 0%, #151a27 100%);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        border-left: 4px solid;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    .kpi-card .kpi-label {
        color: #94a3b8;
        font-size: 0.78rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.3rem;
    }
    .kpi-card .kpi-value {
        color: #e8ecf1;
        font-size: 1.6rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .kpi-card .kpi-sub {
        color: #64748b;
        font-size: 0.75rem;
        margin-top: 0.2rem;
    }

    .section-header {
        color: #e8ecf1;
        font-size: 1.2rem;
        font-weight: 600;
        padding: 0.5rem 0;
        margin: 1rem 0 0.5rem 0;
        border-bottom: 2px solid rgba(42, 157, 143, 0.3);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #151c25 100%);
    }
    [data-testid="stSidebar"] .stMarkdown h1 {
        color: #2A9D8F;
        font-size: 1.5rem;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    hr {
        border-color: rgba(42, 157, 143, 0.2);
    }

    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
        font-weight: 700;
    }

    /* Analysis box styling */
    .analysis-box {
        background: linear-gradient(135deg, #1a2332 0%, #1a1f2e 100%);
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        border-left: 4px solid #2A9D8F;
        margin: 0.5rem 0 1.5rem 0;
        font-size: 0.9rem;
        color: #c8d0da;
        line-height: 1.6;
    }
    .analysis-box h4 {
        color: #2A9D8F;
        margin: 0 0 0.5rem 0;
        font-size: 0.95rem;
    }
    .analysis-box .problem {
        background: rgba(231, 111, 81, 0.1);
        border-left: 3px solid #E76F51;
        padding: 0.6rem 1rem;
        border-radius: 0 6px 6px 0;
        margin-top: 0.8rem;
        font-size: 0.85rem;
    }
    .analysis-box .problem strong {
        color: #E76F51;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER: ANALYSIS BOX
# ============================================================

def analysis_box(what_it_shows, problem="", key_stats=""):
    """Render a styled analysis box below a chart."""
    html = f"""<div class="analysis-box">
        <h4>📖 What This Chart Shows</h4>
        <p>{what_it_shows}</p>"""
    if key_stats:
        html += f"""<p style="margin-top: 0.5rem; color: #94a3b8;"><em>{key_stats}</em></p>"""
    if problem:
        html += f"""<div class="problem">
            <strong>⚠️ Problem Identified:</strong> {problem}
        </div>"""
    html += "</div>"
    return html


# ============================================================
# COLOR PALETTE
# ============================================================

COLORS = {
    'blue': '#3A7CA5', 'green': '#6BAA75', 'coral': '#E07A5F',
    'teal': '#2A9D8F', 'amber': '#E9C46A', 'red': '#E76F51',
    'navy': '#264653', 'purple': '#7B2D8E', 'pink': '#D1477A',
    'dark': '#1F2933', 'muted': '#667085', 'cyan': '#06B6D4',
}

PLOTLY_TEMPLATE = "plotly_dark"
CHART_BG = "rgba(0,0,0,0)"
PAPER_BG = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(255,255,255,0.06)"

def chart_layout(title="", height=450, **kwargs):
    # Merge caller's xaxis/yaxis overrides with defaults instead of conflicting
    xaxis_extra = kwargs.pop('xaxis', {})
    yaxis_extra = kwargs.pop('yaxis', {})
    base_xaxis = dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    base_yaxis = dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    base_xaxis.update(xaxis_extra)
    base_yaxis.update(yaxis_extra)
    return dict(
        title=dict(text=title, font=dict(size=16, color="#e8ecf1")),
        template=PLOTLY_TEMPLATE,
        plot_bgcolor=CHART_BG,
        paper_bgcolor=PAPER_BG,
        height=height,
        font=dict(family="Inter, sans-serif", color="#c8d0da"),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=base_xaxis,
        yaxis=base_yaxis,
        hoverlabel=dict(bgcolor="#1a1f2e", font_size=13, font_family="Inter"),
        **kwargs,
    )


# ============================================================
# DATABASE & DATA LOADING
# ============================================================

DB_CONFIG = {
    'host': 'localhost', 'port': 5433, 'database': 'careflow_ai',
    'user': 'postgres', 'password': 'postgres',
}
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"


@st.cache_data(ttl=3600, show_spinner="Loading CMS Medicare data from PostgreSQL...")
def load_data():
    engine = create_engine(DATABASE_URL, echo=False)
    df = pd.read_sql("SELECT * FROM cms_medicare_providers", engine)
    return df


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("# 🏥 CareFlow AI")
    st.markdown("---")

    pages = [
        "🏠 Overview",
        "🩺 Provider Analysis",
        "🗺️ Geographic",
        "💰 Payment Analysis",
        "📊 Revenue Gap",
        "🔬 Procedures",
        "📈 Utilization & Stats",
        "📋 Data Tables",
    ]
    page = st.radio("Navigate", pages, label_visibility="collapsed")
    st.markdown("---")

    df = load_data()

    st.markdown("### 🔍 Filters")
    all_states = sorted(df['provider_state'].dropna().unique().tolist())
    selected_states = st.multiselect("State", all_states, default=[], placeholder="All states")
    top_specialties = df['provider_specialty'].value_counts().head(30).index.tolist()
    selected_specialties = st.multiselect("Specialty", top_specialties, default=[], placeholder="All specialties")
    entity_options = {'All': None, 'Individual (I)': 'I', 'Organization (O)': 'O'}
    entity_choice = st.selectbox("Entity Type", list(entity_options.keys()))
    pos_options = {'All': None, 'Facility (F)': 'F', 'Office (O)': 'O'}
    pos_choice = st.selectbox("Place of Service", list(pos_options.keys()))

    st.markdown("---")
    st.markdown(f"**{len(df):,}** total records loaded")

# Apply filters
filtered = df.copy()
if selected_states:
    filtered = filtered[filtered['provider_state'].isin(selected_states)]
if selected_specialties:
    filtered = filtered[filtered['provider_specialty'].isin(selected_specialties)]
if entity_options[entity_choice]:
    filtered = filtered[filtered['provider_entity_type'] == entity_options[entity_choice]]
if pos_options[pos_choice]:
    filtered = filtered[filtered['place_of_service'] == pos_options[pos_choice]]

if len(filtered) < len(df):
    st.sidebar.success(f"Filtered: **{len(filtered):,}** records")


def kpi_card(label, value, sub="", color="#2A9D8F"):
    return f"""
    <div class="kpi-card" style="border-left-color: {color};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


# ============================================================
# PRECOMPUTE KEY STATS (used across pages)
# ============================================================

n = len(filtered)
n_providers = filtered['provider_npi'].nunique()
n_specialties = filtered['provider_specialty'].nunique()
n_states = filtered['provider_state'].nunique()
n_procedures = filtered['procedure_code'].nunique()
n_cities = filtered['provider_city'].nunique()
avg_charge = filtered['avg_submitted_charge'].mean()
avg_payment = filtered['avg_medicare_payment'].mean()
avg_allowed = filtered['avg_medicare_allowed_amount'].mean()
avg_std = filtered['avg_medicare_standardized_amount'].mean()
med_payment = filtered['avg_medicare_payment'].median()
med_charge = filtered['avg_submitted_charge'].median()
gap_amt = avg_charge - avg_payment
gap_pct = (1 - avg_payment / avg_charge) * 100 if avg_charge > 0 else 0
patient_cost = avg_allowed - avg_payment
write_off = avg_charge - avg_allowed


# ============================================================
# PAGE 1: OVERVIEW
# ============================================================

if page == "🏠 Overview":
    st.markdown("""
    <div class="main-header">
        <h1>🏥 CareFlow AI — CMS Medicare Dashboard</h1>
        <p>Interactive analysis of Medicare Physician & Other Practitioners data</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(analysis_box(
        f"This dashboard provides a comprehensive interactive analysis of <b>{len(df):,}</b> Medicare "
        f"provider-service records from the CMS (Centers for Medicare & Medicaid Services) public dataset. "
        f"The data covers <b>{n_providers:,}</b> unique healthcare providers across <b>{n_specialties}</b> "
        f"medical specialties in <b>{n_states}</b> states/territories, performing <b>{n_procedures:,}</b> "
        f"distinct procedures. Each row represents a unique provider-procedure combination, showing what "
        f"the provider charged, what Medicare approved, and what Medicare actually paid.",
        key_stats="Use the sidebar filters to slice data by State, Specialty, Entity Type, or Place of Service. "
                  "Every chart is interactive — hover over any element to see exact values."
    ), unsafe_allow_html=True)

    # KPI Row 1
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Total Records", f"{n:,}", f"Out of {len(df):,} total", "#2A9D8F"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Unique Providers", f"{n_providers:,}", "Distinct NPI numbers", "#3A7CA5"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Specialties", f"{n_specialties}", f"{n_procedures:,} procedures", "#6BAA75"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("States / Territories", f"{n_states}", f"{n_cities:,} cities", "#E9C46A"), unsafe_allow_html=True)

    st.markdown("")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(kpi_card("Avg Submitted Charge", f"${avg_charge:,.2f}", "Provider sticker price", "#E07A5F"), unsafe_allow_html=True)
    with c6:
        st.markdown(kpi_card("Avg Medicare Payment", f"${avg_payment:,.2f}", "What Medicare actually pays", "#2A9D8F"), unsafe_allow_html=True)
    with c7:
        st.markdown(kpi_card("Avg Allowed Amount", f"${avg_allowed:,.2f}", "Medicare-approved maximum", "#3A7CA5"), unsafe_allow_html=True)
    with c8:
        st.markdown(kpi_card("Charge-Payment Gap", f"{gap_pct:.1f}%", f"${gap_amt:,.2f} per service", "#E76F51"), unsafe_allow_html=True)

    st.markdown("---")

    # Overview charts
    col_left, col_right = st.columns(2)

    with col_left:
        top_spec = filtered['provider_specialty'].value_counts().head(10)
        fig = px.bar(x=top_spec.values, y=top_spec.index, orientation='h',
                     color=top_spec.values, color_continuous_scale='Teal',
                     labels={'x': 'Records', 'y': 'Specialty'})
        fig.update_layout(**chart_layout("Top 10 Specialties", height=400,
                         yaxis={'categoryorder': 'total ascending'}), coloraxis_showscale=False)
        fig.update_traces(hovertemplate='<b>%{y}</b><br>Records: %{x:,}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(analysis_box(
            f"This chart ranks the 10 most common medical specialties by record count. "
            f"The top specialty is <b>\"{top_spec.index[0]}\"</b> with <b>{top_spec.values[0]:,}</b> records "
            f"({top_spec.values[0]/n*100:.1f}% of filtered data). The top 5 specialties account for "
            f"<b>{top_spec.head(5).sum()/n*100:.1f}%</b> of all records.",
            problem="Heavy concentration in a few specialties means prior authorization rules and denial patterns "
                    "differ dramatically by specialty. CareFlow AI must build specialty-specific models rather "
                    "than one-size-fits-all approaches. Rare specialties with few records will lack sufficient "
                    "training data for accurate prediction."
        ), unsafe_allow_html=True)

    with col_right:
        top_states = filtered['provider_state'].value_counts().head(10)
        fig = px.bar(x=top_states.index, y=top_states.values,
                     color=top_states.values, color_continuous_scale='Teal',
                     labels={'x': 'State', 'y': 'Records'})
        fig.update_layout(**chart_layout("Top 10 States by Records", height=400), coloraxis_showscale=False)
        fig.update_traces(hovertemplate='<b>%{x}</b><br>Records: %{y:,}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(analysis_box(
            f"This chart ranks states by total number of Medicare provider-service records. "
            f"The top 5 states (<b>{', '.join(top_states.head(5).index)}</b>) account for "
            f"<b>{top_states.head(5).sum()/n*100:.1f}%</b> of all records. Population-heavy states dominate.",
            problem="Extreme geographic concentration suggests potential Medicare access disparities. "
                    "Patients in rural states have fewer providers to choose from, leading to longer wait times, "
                    "higher no-show rates, and delayed care. CareFlow AI should flag patients in underserved areas "
                    "for proactive scheduling support and recommend telehealth alternatives."
        ), unsafe_allow_html=True)

    # Gender & Entity pies
    col_l2, col_r2 = st.columns(2)

    with col_l2:
        gender = filtered['provider_gender'].dropna().value_counts()
        gender_labels = {'M': 'Male', 'F': 'Female'}
        fig = px.pie(values=gender.values, names=[gender_labels.get(k, k) for k in gender.index],
                     color_discrete_sequence=[COLORS['blue'], COLORS['coral']], hole=0.45)
        fig.update_layout(**chart_layout("Provider Gender Distribution", height=350))
        fig.update_traces(textposition='inside', textinfo='percent+label',
                         hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

        male_pct = gender.get('M', 0) / gender.sum() * 100 if gender.sum() > 0 else 0
        st.markdown(analysis_box(
            f"Gender distribution of individual providers (organizations have no gender). "
            f"Male providers account for <b>{male_pct:.1f}%</b> of records.",
            key_stats="Gender is blank/null for organizational providers (hospitals, clinics, labs)."
        ), unsafe_allow_html=True)

    with col_r2:
        entity = filtered['provider_entity_type'].dropna().value_counts()
        entity_labels = {'I': 'Individual', 'O': 'Organization'}
        fig = px.pie(values=entity.values, names=[entity_labels.get(k, k) for k in entity.index],
                     color_discrete_sequence=[COLORS['green'], COLORS['amber']], hole=0.45)
        fig.update_layout(**chart_layout("Entity Type Distribution", height=350))
        fig.update_traces(textposition='inside', textinfo='percent+label',
                         hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

        indiv_pct = entity.get('I', 0) / entity.sum() * 100 if entity.sum() > 0 else 0
        st.markdown(analysis_box(
            f"Split between individual providers (physicians, NPs, PAs) and organizations "
            f"(hospitals, clinics, labs). Individuals make up <b>{indiv_pct:.1f}%</b> of records.",
            problem="Organizations typically perform higher-cost procedures and have different billing patterns. "
                    "They also face different prior authorization rules and may submit facility fees on top of "
                    "professional fees. CareFlow AI must distinguish between individual and organizational billing."
        ), unsafe_allow_html=True)

    # Who Pays What
    st.markdown('<div class="section-header">💰 Who Pays What? (Average per Service)</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(name='🏛️ Medicare Pays', x=['Payment Breakdown'], y=[avg_payment],
                         marker_color=COLORS['teal'], text=f'${avg_payment:,.2f}', textposition='inside',
                         hovertemplate='Medicare Payment: $%{y:,.2f}<extra></extra>'))
    fig.add_trace(go.Bar(name='👤 Patient Pays (est.)', x=['Payment Breakdown'], y=[patient_cost],
                         marker_color=COLORS['amber'], text=f'${patient_cost:,.2f}', textposition='inside',
                         hovertemplate='Patient Coinsurance: $%{y:,.2f}<extra></extra>'))
    fig.add_trace(go.Bar(name='❌ Write-Off (lost)', x=['Payment Breakdown'], y=[write_off],
                         marker_color=COLORS['coral'], text=f'${write_off:,.2f}', textposition='inside',
                         hovertemplate='Write-Off: $%{y:,.2f}<extra></extra>'))
    fig.update_layout(**chart_layout(f"Who Pays What? (Total Charge: ${avg_charge:,.2f})", height=400),
                     barmode='stack', legend=dict(orientation='h', yanchor='bottom', y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        f"This stacked bar shows the average payment breakdown per service. "
        f"The provider charges <b>${avg_charge:,.2f}</b> (sticker price), but Medicare approves "
        f"only <b>${avg_allowed:,.2f}</b> (the allowed amount). Of that, Medicare pays "
        f"<b>${avg_payment:,.2f}</b> (~80% of allowed) directly to the provider. The patient pays an estimated "
        f"<b>${patient_cost:,.2f}</b> in coinsurance (~20% of allowed). The remaining "
        f"<b>${write_off:,.2f}</b> is written off — the provider billed it but nobody pays it.",
        key_stats=f"Flow: Provider charges ${avg_charge:,.0f} → Medicare approves ${avg_allowed:,.0f} → "
                  f"Medicare pays ${avg_payment:,.0f} (80%) → Patient pays ${patient_cost:,.0f} (20%) → "
                  f"Write-off ${write_off:,.0f}",
        problem=f"The gap represents {gap_pct:.1f}% revenue loss. Providers who set charges without "
                f"understanding Medicare fee schedules face significant revenue shortfalls. "
                f"The write-off is NOT what the patient pays — it's unrealized revenue that nobody collects."
    ), unsafe_allow_html=True)


# ============================================================
# PAGE 2: PROVIDER ANALYSIS
# ============================================================

elif page == "🩺 Provider Analysis":
    st.markdown("""
    <div class="main-header">
        <h1>🩺 Provider Analysis</h1>
        <p>Specialty distribution, credentials, and demographic breakdowns</p>
    </div>
    """, unsafe_allow_html=True)

    # Top 20 Specialties
    top_spec = filtered['provider_specialty'].value_counts().head(20)
    fig = px.bar(x=top_spec.values, y=top_spec.index, orientation='h',
                 color=top_spec.values, color_continuous_scale='Teal',
                 labels={'x': 'Number of Records', 'y': 'Specialty'})
    fig.update_layout(**chart_layout("Top 20 Provider Specialties", height=600,
                     yaxis={'categoryorder': 'total ascending'}), coloraxis_showscale=False)
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Records: %{x:,}<br>Share: %{customdata:.1f}%<extra></extra>',
        customdata=top_spec.values / n * 100,
    )
    st.plotly_chart(fig, use_container_width=True)

    top5_spec = top_spec.head(5)
    st.markdown(analysis_box(
        f"This horizontal bar chart ranks the 20 most common medical specialties in the dataset by number "
        f"of records. The top specialty is <b>\"{top5_spec.index[0]}\"</b> with <b>{top5_spec.values[0]:,}</b> "
        f"records ({top5_spec.values[0]/n*100:.1f}% of all records). The top 5 specialties account for "
        f"<b>{top5_spec.sum()/n*100:.1f}%</b> of the dataset, while there are {n_specialties} total "
        f"specialties — meaning most specialties have very few records.",
        problem="The extreme concentration in a few specialties creates two problems: (1) Prior authorization "
                "rules and denial patterns differ dramatically by specialty, so a one-size-fits-all AI model will "
                "fail. CareFlow AI must build specialty-specific models. (2) Rare specialties with few records "
                "will lack sufficient training data, creating prediction blind spots."
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Credentials
    creds = filtered['provider_credentials'].dropna().value_counts().head(15)
    fig = px.bar(x=creds.index, y=creds.values, color=creds.values, color_continuous_scale='Teal',
                 labels={'x': 'Credential', 'y': 'Records'})
    fig.update_layout(**chart_layout("Top 15 Provider Credentials", height=400), coloraxis_showscale=False)
    fig.update_traces(hovertemplate='<b>%{x}</b><br>Records: %{y:,}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        f"This chart shows the distribution of professional credentials among providers. "
        f"The most common credential is <b>\"{creds.index[0]}\"</b> ({creds.values[0]:,} records), "
        f"followed by \"{creds.index[1]}\" and \"{creds.index[2]}\". M.D. = Doctor of Medicine, "
        f"D.O. = Doctor of Osteopathic Medicine, NP = Nurse Practitioner, PA = Physician Assistant, "
        f"CRNA = Certified Registered Nurse Anesthetist.",
        problem="Different credential types have different scope-of-practice rules and prior authorization "
                "requirements. Nurse practitioners and physician assistants may face additional authorization "
                "hurdles for procedures that physicians can perform without prior auth. CareFlow AI must factor "
                "in credential type when predicting authorization requirements."
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Gender and Entity pies
    col1, col2 = st.columns(2)

    with col1:
        gender = filtered['provider_gender'].dropna().value_counts()
        gender_labels = {'M': 'Male', 'F': 'Female'}
        fig = px.pie(values=gender.values, names=[gender_labels.get(k, k) for k in gender.index],
                     color_discrete_sequence=[COLORS['blue'], COLORS['coral']], hole=0.45)
        fig.update_layout(**chart_layout("Provider Gender Distribution", height=380))
        fig.update_traces(textposition='inside', textinfo='percent+label',
                         hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        entity = filtered['provider_entity_type'].dropna().value_counts()
        entity_labels = {'I': 'Individual', 'O': 'Organization'}
        fig = px.pie(values=entity.values, names=[entity_labels.get(k, k) for k in entity.index],
                     color_discrete_sequence=[COLORS['green'], COLORS['amber']], hole=0.45)
        fig.update_layout(**chart_layout("Individual vs Organization", height=380))
        fig.update_traces(textposition='inside', textinfo='percent+label',
                         hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        f"<b>Left:</b> Gender distribution of individual providers (organizations have no gender). "
        f"<b>Right:</b> Split between individual providers (physicians, NPs, PAs) and organizations "
        f"(hospitals, clinics, labs, imaging centers).",
        problem="The gender payment gap likely reflects uneven specialty distribution — male providers are "
                "overrepresented in higher-paying surgical specialties, while female providers are more "
                "concentrated in primary care. CareFlow AI should control for specialty when analyzing payment equity."
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Payment by Gender & Entity
    col3, col4 = st.columns(2)

    with col3:
        gender_pay = filtered.groupby('provider_gender')['avg_medicare_payment'].agg(['mean', 'median']).reset_index()
        gender_pay.columns = ['Gender', 'Mean Payment', 'Median Payment']
        gender_pay['Gender'] = gender_pay['Gender'].map({'M': 'Male', 'F': 'Female'})
        gender_pay = gender_pay.dropna(subset=['Gender'])
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Mean', x=gender_pay['Gender'], y=gender_pay['Mean Payment'],
                             marker_color=COLORS['blue'], hovertemplate='<b>%{x}</b><br>Mean: $%{y:,.2f}<extra></extra>'))
        fig.add_trace(go.Bar(name='Median', x=gender_pay['Gender'], y=gender_pay['Median Payment'],
                             marker_color=COLORS['coral'], hovertemplate='<b>%{x}</b><br>Median: $%{y:,.2f}<extra></extra>'))
        fig.update_layout(**chart_layout("Payment by Gender", height=400), barmode='group', yaxis_tickprefix='$')
        st.plotly_chart(fig, use_container_width=True)

        if len(gender_pay) >= 2:
            gp = gender_pay.set_index('Gender')
            diff = abs(gp.loc['Male', 'Mean Payment'] - gp.loc['Female', 'Mean Payment']) if 'Male' in gp.index and 'Female' in gp.index else 0
            st.markdown(analysis_box(
                f"Mean and median Medicare payments compared by provider gender. "
                f"The mean payment difference is <b>${diff:,.2f}</b>. Mean vs median comparison reveals "
                f"whether outliers skew the average — if mean >> median, a few high-value procedures drive up the average.",
            ), unsafe_allow_html=True)

    with col4:
        entity_pay = filtered.groupby('provider_entity_type')['avg_medicare_payment'].agg(['mean', 'median']).reset_index()
        entity_pay.columns = ['Entity', 'Mean Payment', 'Median Payment']
        entity_pay['Entity'] = entity_pay['Entity'].map({'I': 'Individual', 'O': 'Organization'})
        entity_pay = entity_pay.dropna(subset=['Entity'])
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Mean', x=entity_pay['Entity'], y=entity_pay['Mean Payment'],
                             marker_color=COLORS['green'], hovertemplate='<b>%{x}</b><br>Mean: $%{y:,.2f}<extra></extra>'))
        fig.add_trace(go.Bar(name='Median', x=entity_pay['Entity'], y=entity_pay['Median Payment'],
                             marker_color=COLORS['amber'], hovertemplate='<b>%{x}</b><br>Median: $%{y:,.2f}<extra></extra>'))
        fig.update_layout(**chart_layout("Payment by Entity Type", height=400), barmode='group', yaxis_tickprefix='$')
        st.plotly_chart(fig, use_container_width=True)

        if len(entity_pay) >= 2:
            st.markdown(analysis_box(
                f"Organizations (hospitals, labs, imaging centers) typically average higher payments because "
                f"they perform higher-cost procedures like surgeries, imaging, and dialysis.",
                problem="Organizations have fundamentally different billing patterns and face different prior "
                        "authorization rules. They are more likely to submit facility fees on top of professional fees."
            ), unsafe_allow_html=True)

    st.markdown("---")

    # Medicare Participation, Drug, Place of Service
    col5, col6 = st.columns(2)

    with col5:
        mp = filtered['medicare_participating'].dropna().value_counts()
        mp_labels = {'Y': 'Participating', 'N': 'Non-Participating'}
        fig = px.pie(values=mp.values, names=[mp_labels.get(k, k) for k in mp.index],
                     color_discrete_sequence=[COLORS['teal'], COLORS['coral']], hole=0.45)
        fig.update_layout(**chart_layout("Medicare Participation Rate", height=380))
        fig.update_traces(textposition='inside', textinfo='percent+label',
                         hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

        part_pct = mp.get('Y', 0) / mp.sum() * 100 if mp.sum() > 0 else 0
        st.markdown(analysis_box(
            f"<b>{part_pct:.1f}%</b> of records are from Medicare-participating providers. "
            f"Participating providers accept Medicare's approved amount as full payment. "
            f"Non-participating providers can charge up to 15% above the Medicare fee schedule (the \"limiting charge\").",
            problem="Non-participating providers create cost uncertainty for patients through 'balance billing.' "
                    "CareFlow AI should flag non-participating providers and warn patients about potential higher "
                    "out-of-pocket costs before appointments are booked."
        ), unsafe_allow_html=True)

    with col6:
        drug = filtered['is_drug_service'].dropna().value_counts()
        drug_labels = {'Y': 'Drug Services', 'N': 'Non-Drug Services'}
        fig = px.pie(values=drug.values, names=[drug_labels.get(k, k) for k in drug.index],
                     color_discrete_sequence=[COLORS['purple'], COLORS['green']], hole=0.45)
        fig.update_layout(**chart_layout("Drug vs Non-Drug Services", height=380))
        fig.update_traces(textposition='inside', textinfo='percent+label',
                         hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

        drug_pct = drug.get('Y', 0) / drug.sum() * 100 if drug.sum() > 0 else 0
        st.markdown(analysis_box(
            f"Drug services account for <b>{drug_pct:.1f}%</b> of records. These include administered "
            f"medications, infusions, injections, and chemotherapy drugs billed under Medicare Part B.",
            problem="Drug services have fundamentally different authorization requirements. Many high-cost "
                    "specialty drugs (biologics, chemotherapy, immunotherapy) require prior authorization with "
                    "clinical documentation. Drug prices also fluctuate more, making cost prediction harder. "
                    "CareFlow AI must maintain separate authorization workflows for drug vs non-drug services."
        ), unsafe_allow_html=True)

    col7, col8 = st.columns(2)

    with col7:
        pos = filtered['place_of_service'].dropna().value_counts()
        pos_labels = {'F': 'Facility', 'O': 'Office'}
        fig = px.pie(values=pos.values, names=[pos_labels.get(k, k) for k in pos.index],
                     color_discrete_sequence=[COLORS['navy'], COLORS['teal']], hole=0.45)
        fig.update_layout(**chart_layout("Place of Service", height=380))
        fig.update_traces(textposition='inside', textinfo='percent+label',
                         hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>%{percent}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

    with col8:
        place_pay = filtered.groupby('place_of_service')['avg_medicare_payment'].agg(['mean', 'median']).reset_index()
        place_pay.columns = ['Place', 'Mean Payment', 'Median Payment']
        place_pay['Place'] = place_pay['Place'].map({'F': 'Facility', 'O': 'Office'})
        place_pay = place_pay.dropna(subset=['Place'])
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Mean', x=place_pay['Place'], y=place_pay['Mean Payment'],
                             marker_color=COLORS['navy'], hovertemplate='<b>%{x}</b><br>Mean: $%{y:,.2f}<extra></extra>'))
        fig.add_trace(go.Bar(name='Median', x=place_pay['Place'], y=place_pay['Median Payment'],
                             marker_color=COLORS['teal'], hovertemplate='<b>%{x}</b><br>Median: $%{y:,.2f}<extra></extra>'))
        fig.update_layout(**chart_layout("Payment: Facility vs Office", height=380), barmode='group', yaxis_tickprefix='$')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        f"<b>Left:</b> Distribution of services between Facility (hospital, surgery center, SNF) and "
        f"Office (provider's private office/clinic) settings. <b>Right:</b> Average payment comparison. "
        f"The same procedure performed in a facility vs office can result in dramatically different reimbursement — "
        f"facility fees add significant cost.",
        problem="Patients are often unaware that the same procedure costs much more at a hospital than in a "
                "doctor's office. CareFlow AI should flag place-of-service as a key variable in cost estimates "
                "and recommend office-based alternatives when clinically appropriate to reduce patient costs."
    ), unsafe_allow_html=True)


# ============================================================
# PAGE 3: GEOGRAPHIC
# ============================================================

elif page == "🗺️ Geographic":
    st.markdown("""
    <div class="main-header">
        <h1>🗺️ Geographic Analysis</h1>
        <p>State-level distribution, interactive maps, and city breakdowns</p>
    </div>
    """, unsafe_allow_html=True)

    # Choropleth — Records
    state_data = filtered.groupby('provider_state').agg(
        records=('provider_npi', 'count'), providers=('provider_npi', 'nunique'),
        avg_payment=('avg_medicare_payment', 'mean'), avg_charge=('avg_submitted_charge', 'mean'),
    ).reset_index()
    state_data['gap'] = state_data['avg_charge'] - state_data['avg_payment']

    fig = px.choropleth(
        state_data, locations='provider_state', locationmode='USA-states',
        color='records', scope='usa', color_continuous_scale='Teal',
        hover_name='provider_state',
        hover_data={'provider_state': False, 'records': ':,', 'providers': ':,',
                    'avg_payment': ':$.2f', 'avg_charge': ':$.2f', 'gap': ':$.2f'},
        labels={'records': 'Records', 'providers': 'Unique Providers',
                'avg_payment': 'Avg Medicare Payment', 'avg_charge': 'Avg Submitted Charge',
                'gap': 'Charge-Payment Gap'},
    )
    fig.update_layout(**chart_layout("Medicare Provider Records by State (Hover for Details)", height=500))
    fig.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        "This interactive choropleth map shows Medicare provider record density by state. "
        "<b>Hover over any state</b> to see exact record count, unique provider count, average payment, "
        "average charge, and charge-payment gap. Darker colors indicate more records. "
        "Population-dense states (CA, FL, TX, NY) dominate due to their large Medicare populations.",
        problem="Geographic concentration creates severe access disparities. While urban areas have an "
                "abundance of providers, rural states and small towns face critical shortages. Patients in "
                "underserved areas experience longer wait times, fewer specialist options, and must travel "
                "further for care. CareFlow AI should flag patients in underserved ZIP codes for proactive "
                "scheduling support and recommend telehealth alternatives."
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Choropleth — Payment
    fig2 = px.choropleth(
        state_data, locations='provider_state', locationmode='USA-states',
        color='avg_payment', scope='usa', color_continuous_scale='YlGnBu',
        hover_name='provider_state',
        hover_data={'provider_state': False, 'records': ':,', 'avg_payment': ':$.2f', 'avg_charge': ':$.2f'},
        labels={'avg_payment': 'Avg Medicare Payment', 'records': 'Records', 'avg_charge': 'Avg Charge'},
    )
    fig2.update_layout(**chart_layout("Average Medicare Payment by State", height=500))
    fig2.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(analysis_box(
        "This map visualizes average Medicare payment by state. Higher payments in certain states reflect "
        "higher cost of living, Geographic Practice Cost Indices (GPCI), and specialty mix. States with "
        "expensive real estate and higher wages naturally have higher Medicare fee schedules.",
        problem="State-level payment variation means a provider performing the same procedure in two different "
                "states will receive different reimbursement. CareFlow AI must use location-adjusted predictions "
                "rather than national averages when estimating expected payments."
    ), unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        top_st = filtered['provider_state'].value_counts().head(20)
        fig = px.bar(x=top_st.index, y=top_st.values, color=top_st.values, color_continuous_scale='Teal',
                     labels={'x': 'State', 'y': 'Records'})
        fig.update_layout(**chart_layout("Top 20 States by Records", height=420), coloraxis_showscale=False)
        fig.update_traces(hovertemplate='<b>%{x}</b><br>Records: %{y:,}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        provs_state = filtered.groupby('provider_state')['provider_npi'].nunique().sort_values(ascending=False).head(20).reset_index()
        provs_state.columns = ['State', 'Unique Providers']
        fig = px.bar(provs_state, x='State', y='Unique Providers', color='Unique Providers', color_continuous_scale='Viridis')
        fig.update_layout(**chart_layout("Top 20 States by Unique Providers (NPI)", height=420), coloraxis_showscale=False)
        fig.update_traces(hovertemplate='<b>%{x}</b><br>Providers: %{y:,}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

    top5_provs = provs_state.head(5)['Unique Providers'].sum()
    total_provs = filtered['provider_npi'].nunique()
    st.markdown(analysis_box(
        f"<b>Left:</b> Total record count per state (billing volume). <b>Right:</b> Unique provider count "
        f"per state (how many distinct healthcare professionals). The top 5 states hold "
        f"<b>{top5_provs:,}</b> of <b>{total_provs:,}</b> unique providers (<b>{top5_provs/total_provs*100:.1f}%</b>). "
        f"This confirms geographic concentration is real — not just billing volume, but actual provider count.",
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Top Cities
    cities = filtered.groupby(['provider_city', 'provider_state']).size().reset_index(name='count')
    cities['label'] = cities['provider_city'] + ', ' + cities['provider_state']
    cities = cities.sort_values('count', ascending=False).head(20)

    fig = px.bar(cities, x='count', y='label', orientation='h',
                 color='count', color_continuous_scale='Teal', labels={'count': 'Records', 'label': 'City'})
    fig.update_layout(**chart_layout("Top 20 Cities by Provider Records", height=550,
                     yaxis={'categoryorder': 'total ascending'}), coloraxis_showscale=False)
    fig.update_traces(hovertemplate='<b>%{y}</b><br>Records: %{x:,}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        "City-level drilldown showing where Medicare providers are most concentrated. Major metropolitan "
        "areas (New York, Houston, Chicago, Los Angeles, Philadelphia) dominate, reflecting urban "
        "concentration of healthcare providers.",
        problem="Rural communities and small cities are underrepresented, meaning patients in these areas have "
                "fewer provider choices, potentially longer travel times for specialist care, and fewer "
                "scheduling options."
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Avg Payment by State
    state_pay = filtered.groupby('provider_state')['avg_medicare_payment'].mean().sort_values(ascending=False).head(20).reset_index()
    state_pay.columns = ['State', 'Avg Payment']
    fig = px.bar(state_pay, x='State', y='Avg Payment', color='Avg Payment', color_continuous_scale='Teal')
    fig.update_layout(**chart_layout("Top 20 States by Average Medicare Payment", height=420),
                     coloraxis_showscale=False, yaxis_tickprefix='$')
    fig.update_traces(hovertemplate='<b>%{x}</b><br>Avg Payment: $%{y:,.2f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        f"Average Medicare payment per service by state. Higher payments in certain states reflect the "
        f"Geographic Practice Cost Index (GPCI), which adjusts Medicare fee schedules based on local cost "
        f"of living, practice expenses, and malpractice insurance costs.",
        key_stats="The GPCI has three components: Work, Practice Expense, and Malpractice — all varying by locality."
    ), unsafe_allow_html=True)


# ============================================================
# PAGE 4: PAYMENT ANALYSIS
# ============================================================

elif page == "💰 Payment Analysis":
    st.markdown("""
    <div class="main-header">
        <h1>💰 Payment Analysis</h1>
        <p>Charges vs payments, distributions, efficiency, and breakdowns</p>
    </div>
    """, unsafe_allow_html=True)

    # Charges vs Payments
    payment = filtered.groupby('provider_specialty').agg(
        avg_charge=('avg_submitted_charge', 'mean'), avg_payment=('avg_medicare_payment', 'mean'),
    ).sort_values('avg_charge', ascending=False).head(15)

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Avg Submitted Charge', y=payment.index, x=payment['avg_charge'],
                         orientation='h', marker_color=COLORS['blue'],
                         hovertemplate='<b>%{y}</b><br>Charge: $%{x:,.2f}<extra></extra>'))
    fig.add_trace(go.Bar(name='Avg Medicare Payment', y=payment.index, x=payment['avg_payment'],
                         orientation='h', marker_color=COLORS['green'],
                         hovertemplate='<b>%{y}</b><br>Payment: $%{x:,.2f}<extra></extra>'))
    fig.update_layout(**chart_layout("Submitted Charges vs Medicare Payments (Top 15 Specialties)", height=550,
                     yaxis={'categoryorder': 'total ascending'}), barmode='group', xaxis_tickprefix='$')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        f"This grouped bar chart compares what providers charge (blue) versus what Medicare pays (green) "
        f"for the top 15 most expensive specialties. On average, providers submit <b>${avg_charge:,.2f}</b> but "
        f"receive only <b>${avg_payment:,.2f}</b> — a <b>{gap_pct:.1f}%</b> reduction. The visible gap between "
        f"the blue and green bars represents revenue that is never collected.",
        key_stats=f"Avg Charge: ${avg_charge:,.2f} | Avg Allowed: ${avg_allowed:,.2f} | "
                  f"Avg Payment: ${avg_payment:,.2f} | Standardized: ${avg_std:,.2f}",
        problem="The massive gap between submitted charges and actual payments is the #1 revenue cycle problem. "
                "Providers who set charges based on internal cost structures receive far less than expected. "
                "This creates cash flow unpredictability, inflated patient bills, and administrative burden. "
                "CareFlow AI must provide real-time expected payment estimates so billing staff can set "
                "realistic revenue expectations before claims are submitted."
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Distributions
    col1, col2 = st.columns(2)

    with col1:
        payments_series = filtered['avg_medicare_payment'].dropna()
        q99 = payments_series.quantile(0.99)
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=payments_series[payments_series <= q99], nbinsx=80,
                                   marker_color=COLORS['teal'], opacity=0.85,
                                   hovertemplate='Range: $%{x}<br>Count: %{y:,}<extra></extra>'))
        fig.add_vline(x=payments_series.median(), line_dash="dash", line_color=COLORS['coral'],
                     annotation_text=f"Median: ${payments_series.median():,.2f}")
        fig.add_vline(x=payments_series.mean(), line_dash="dash", line_color=COLORS['green'],
                     annotation_text=f"Mean: ${payments_series.mean():,.2f}")
        fig.update_layout(**chart_layout("Medicare Payment Distribution (99th pctl)", height=420),
                         xaxis_title='Avg Medicare Payment ($)', yaxis_title='Frequency')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(analysis_box(
            f"Distribution of Medicare payments across all {n:,} records. The dashed lines show "
            f"median (<b>${med_payment:,.2f}</b>) and mean (<b>${avg_payment:,.2f}</b>). The distribution is "
            f"heavily right-skewed — most services receive low payments while a small tail of high-cost "
            f"procedures pulls the mean above the median. Max payment: ${payments_series.max():,.2f}.",
        ), unsafe_allow_html=True)

    with col2:
        charges_series = filtered['avg_submitted_charge'].dropna()
        q99_c = charges_series.quantile(0.99)
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=charges_series[charges_series <= q99_c], nbinsx=80,
                                   marker_color=COLORS['navy'], opacity=0.85,
                                   hovertemplate='Range: $%{x}<br>Count: %{y:,}<extra></extra>'))
        fig.add_vline(x=charges_series.median(), line_dash="dash", line_color=COLORS['coral'],
                     annotation_text=f"Median: ${charges_series.median():,.2f}")
        fig.add_vline(x=charges_series.mean(), line_dash="dash", line_color=COLORS['green'],
                     annotation_text=f"Mean: ${charges_series.mean():,.2f}")
        fig.update_layout(**chart_layout("Submitted Charge Distribution (99th pctl)", height=420),
                         xaxis_title='Avg Submitted Charge ($)', yaxis_title='Frequency')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(analysis_box(
            f"Distribution of submitted charges (provider sticker prices). Even more skewed than payments — "
            f"median ${med_charge:,.2f} vs mean ${avg_charge:,.2f}.",
            problem="The skewed distributions mean most services are low-value routine care, but a small number "
                    "of high-value claims drive disproportionate revenue. If even a few high-value claims are denied, "
                    "the financial impact is severe. CareFlow AI should implement a priority queue that gives extra "
                    "scrutiny to high-dollar claims before submission."
        ), unsafe_allow_html=True)

    st.markdown("---")

    # Payment Efficiency
    efficiency = filtered.groupby('provider_specialty').agg(
        avg_charge=('avg_submitted_charge', 'mean'), avg_payment=('avg_medicare_payment', 'mean'))
    efficiency['efficiency_pct'] = (efficiency['avg_payment'] / efficiency['avg_charge'] * 100).round(1)
    bottom20 = efficiency.sort_values('efficiency_pct').head(20).reset_index()

    fig = px.bar(bottom20, x='efficiency_pct', y='provider_specialty', orientation='h',
                 color='efficiency_pct', color_continuous_scale='RdYlGn', range_color=[0, 60],
                 labels={'efficiency_pct': 'Efficiency (%)', 'provider_specialty': 'Specialty'})
    fig.add_vline(x=50, line_dash="dash", line_color=COLORS['muted'], annotation_text="50%")
    fig.update_layout(**chart_layout("Bottom 20 Specialties by Payment Efficiency", height=600,
                     yaxis={'categoryorder': 'total ascending'}), coloraxis_showscale=False)
    fig.update_traces(hovertemplate='<b>%{y}</b><br>Efficiency: %{x:.1f}%<extra></extra>')
    st.plotly_chart(fig, use_container_width=True)

    worst_eff = bottom20.head(3)
    st.markdown(analysis_box(
        f"Payment efficiency = (Medicare Payment / Submitted Charge) × 100%. This chart shows the 20 "
        f"specialties with the <b>lowest</b> efficiency — where Medicare pays the smallest percentage of "
        f"what providers charge. The worst is <b>{worst_eff['provider_specialty'].iloc[0]}</b> at only "
        f"<b>{worst_eff['efficiency_pct'].iloc[0]:.1f}%</b>.",
        problem="Specialties below 30% efficiency face the most severe revenue shortfalls. Providers may not "
                "realize how little Medicare will reimburse until after services are rendered. CareFlow AI should "
                "provide specialty-specific fee schedule lookups and warn providers when their charges significantly "
                "exceed expected reimbursement, preventing surprise revenue shortfalls."
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Boxplot
    top8 = filtered['provider_specialty'].value_counts().head(8).index.tolist()
    box_df = filtered[filtered['provider_specialty'].isin(top8)][['provider_specialty', 'avg_medicare_payment']].dropna()
    q95 = box_df['avg_medicare_payment'].quantile(0.95)
    box_df = box_df[box_df['avg_medicare_payment'] <= q95]

    fig = px.box(box_df, x='provider_specialty', y='avg_medicare_payment', color='provider_specialty',
                 labels={'provider_specialty': 'Specialty', 'avg_medicare_payment': 'Avg Payment ($)'})
    fig.update_layout(**chart_layout("Payment Distribution by Top 8 Specialties (95th pctl)", height=500),
                     showlegend=False, xaxis_tickangle=-25)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        "Box plots show the payment distribution <b>within</b> each specialty. The box represents the "
        "interquartile range (25th-75th percentile), the line inside is the median, and whiskers extend to "
        "1.5× the IQR. This reveals how predictable or variable payments are per specialty.",
        problem="Specialties with wide boxes and long whiskers have unpredictable reimbursement — revenue "
                "forecasting is difficult. Specialties with narrow boxes have more predictable payments. "
                "CareFlow AI should factor in specialty-level payment variance when generating revenue "
                "forecasts and confidence intervals."
    ), unsafe_allow_html=True)


# ============================================================
# PAGE 5: REVENUE GAP
# ============================================================

elif page == "📊 Revenue Gap":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Revenue Gap Analysis</h1>
        <p>Charge-to-payment gaps, write-off analysis, and who-pays-what breakdowns</p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("🏥 Provider Charges", f"${avg_charge:,.2f}", "Avg submitted charge", COLORS['blue']), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("🏛️ Medicare Pays", f"${avg_payment:,.2f}", "Actual payment to provider", COLORS['teal']), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("👤 Patient Pays (est)", f"${patient_cost:,.2f}", "20% coinsurance", COLORS['amber']), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("❌ Write-Off", f"${write_off:,.2f}", f"Gap: ${gap_amt:,.2f} ({gap_pct:.1f}%)", COLORS['coral']), unsafe_allow_html=True)

    st.markdown("")

    # Payment definitions
    st.markdown("""
    <div class="analysis-box">
        <h4>📋 Payment Field Definitions — Who Pays What?</h4>
        <table style="width:100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 6px;"><b>Avg Submitted Charge</b></td>
                <td style="padding: 6px;">🏥 <b>Provider</b> (billed amount)</td>
                <td style="padding: 6px;">The provider's "sticker price." Medicare almost never pays this full amount.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 6px;"><b>Avg Medicare Allowed</b></td>
                <td style="padding: 6px;">🏛️ <b>Medicare</b> (approved max)</td>
                <td style="padding: 6px;">Maximum Medicare approves for this service. This is the payment ceiling.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 6px;"><b>Avg Medicare Payment</b></td>
                <td style="padding: 6px;">🏛️ <b>Medicare</b> (actual)</td>
                <td style="padding: 6px;">What Medicare actually pays — typically 80% of Allowed. This is <b>real revenue</b>.</td>
            </tr>
            <tr>
                <td style="padding: 6px;"><b>Avg Standardized Amt</b></td>
                <td style="padding: 6px;">🏛️ <b>Medicare</b> (geo-adjusted)</td>
                <td style="padding: 6px;">Geography-adjusted payment for fair state-to-state comparisons.</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Who Pays What stacked
    fig = go.Figure()
    fig.add_trace(go.Bar(name='🏛️ Medicare Pays', x=['Payment Breakdown'], y=[avg_payment],
                         marker_color=COLORS['teal'], text=f'${avg_payment:,.2f}', textposition='inside',
                         hovertemplate='Medicare: $%{y:,.2f}<extra></extra>'))
    fig.add_trace(go.Bar(name='👤 Patient Pays', x=['Payment Breakdown'], y=[patient_cost],
                         marker_color=COLORS['amber'], text=f'${patient_cost:,.2f}', textposition='inside',
                         hovertemplate='Patient: $%{y:,.2f}<extra></extra>'))
    fig.add_trace(go.Bar(name='❌ Write-Off', x=['Payment Breakdown'], y=[write_off],
                         marker_color=COLORS['coral'], text=f'${write_off:,.2f}', textposition='inside',
                         hovertemplate='Write-Off: $%{y:,.2f}<extra></extra>'))
    fig.update_layout(**chart_layout(f"Who Pays What? (Total Charge: ${avg_charge:,.2f})", height=420),
                     barmode='stack', legend=dict(orientation='h', yanchor='bottom', y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        f"Provider charges <b>${avg_charge:,.2f}</b> → Medicare approves <b>${avg_allowed:,.2f}</b> → "
        f"Medicare pays <b>${avg_payment:,.2f}</b> (80% of allowed) → Patient pays <b>${patient_cost:,.2f}</b> "
        f"(20% coinsurance) → Provider writes off <b>${write_off:,.2f}</b> (charge minus allowed = lost revenue). "
        f"The write-off is NOT what the patient pays — it's unrealized revenue that nobody collects.",
        key_stats=f"Provider keeps: ${avg_payment:,.2f} ({avg_payment/avg_charge*100:.1f}% of charge) | "
                  f"Patient pays: ${patient_cost:,.2f} ({patient_cost/avg_charge*100:.1f}%) | "
                  f"Written off: ${write_off:,.2f} ({write_off/avg_charge*100:.1f}%)"
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Who pays by specialty
    sp = filtered.groupby('provider_specialty').agg(
        charge=('avg_submitted_charge', 'mean'), allowed=('avg_medicare_allowed_amount', 'mean'),
        payment=('avg_medicare_payment', 'mean'),
    ).sort_values('charge', ascending=False).head(12)
    sp['patient'] = sp['allowed'] - sp['payment']
    sp['writeoff'] = sp['charge'] - sp['allowed']

    fig = go.Figure()
    fig.add_trace(go.Bar(name='🏛️ Medicare Pays', y=sp.index, x=sp['payment'],
                         orientation='h', marker_color=COLORS['teal'],
                         hovertemplate='<b>%{y}</b><br>Medicare: $%{x:,.2f}<extra></extra>'))
    fig.add_trace(go.Bar(name='👤 Patient Pays', y=sp.index, x=sp['patient'],
                         orientation='h', marker_color=COLORS['amber'],
                         hovertemplate='<b>%{y}</b><br>Patient: $%{x:,.2f}<extra></extra>'))
    fig.add_trace(go.Bar(name='❌ Write-Off', y=sp.index, x=sp['writeoff'],
                         orientation='h', marker_color=COLORS['coral'],
                         hovertemplate='<b>%{y}</b><br>Write-Off: $%{x:,.2f}<extra></extra>'))
    fig.update_layout(**chart_layout("Who Pays What by Specialty (Top 12 Most Expensive)", height=550,
                     yaxis=dict(autorange='reversed')),
                     barmode='stack', xaxis_tickprefix='$',
                     legend=dict(orientation='h', yanchor='bottom', y=-0.15))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        "Each bar shows how the total charge for a specialty is divided: teal (Medicare pays), "
        "yellow (patient pays), and coral (write-off/lost). The wider the coral section, the more "
        "revenue that specialty loses between billing and collection.",
        problem="Specialties with large write-offs (wide coral bars) face the most severe disconnect between "
                "what they charge and what they receive. CareFlow AI should provide specialty-specific dashboards "
                "showing expected reimbursement rates and recommend charge adjustments to minimize write-offs."
    ), unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        g = filtered.groupby('provider_state').agg(
            charge=('avg_submitted_charge', 'mean'), payment=('avg_medicare_payment', 'mean'))
        g['gap'] = g['charge'] - g['payment']
        g = g.sort_values('gap', ascending=False).head(20).reset_index()

        fig = px.bar(g, x='gap', y='provider_state', orientation='h',
                     color='gap', color_continuous_scale='OrRd',
                     labels={'gap': 'Gap ($)', 'provider_state': 'State'})
        fig.update_layout(**chart_layout("Top 20 States by Charge-Payment Gap", height=550,
                         yaxis={'categoryorder': 'total ascending'}), coloraxis_showscale=False, xaxis_tickprefix='$')
        fig.update_traces(hovertemplate='<b>%{y}</b><br>Gap: $%{x:,.2f}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(analysis_box(
            f"States ranked by average dollar gap between submitted charges and Medicare payments. "
            f"The largest gap is in <b>{g['provider_state'].iloc[0]}</b> at <b>${g['gap'].iloc[0]:,.2f}</b>.",
            problem="Providers in high-gap states are likely setting charges based on commercial insurance rates, "
                    "which are much higher than Medicare fee schedules. This leads to large write-offs and A/R buildup."
        ), unsafe_allow_html=True)

    with col2:
        gap_spec = filtered.groupby('provider_specialty').agg(
            charge=('avg_submitted_charge', 'mean'), payment=('avg_medicare_payment', 'mean'))
        gap_spec['gap'] = gap_spec['charge'] - gap_spec['payment']
        gap_spec = gap_spec.sort_values('gap', ascending=False).head(20).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Avg Charge', y=gap_spec['provider_specialty'], x=gap_spec['charge'],
                             orientation='h', marker_color=COLORS['blue'], opacity=0.8,
                             hovertemplate='<b>%{y}</b><br>Charge: $%{x:,.2f}<extra></extra>'))
        fig.add_trace(go.Bar(name='Avg Payment', y=gap_spec['provider_specialty'], x=gap_spec['payment'],
                             orientation='h', marker_color=COLORS['green'], opacity=0.8,
                             hovertemplate='<b>%{y}</b><br>Payment: $%{x:,.2f}<extra></extra>'))
        fig.update_layout(**chart_layout("Revenue Gap by Specialty (Top 20)", height=550,
                         yaxis={'categoryorder': 'total ascending'}), barmode='overlay', xaxis_tickprefix='$')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(analysis_box(
            "Overlay chart comparing average charges (blue) vs payments (green) per specialty. "
            "The visible gap between bars is unrealized revenue. Wider gaps = more write-off.",
        ), unsafe_allow_html=True)


# ============================================================
# PAGE 6: PROCEDURES
# ============================================================

elif page == "🔬 Procedures":
    st.markdown("""
    <div class="main-header">
        <h1>🔬 Procedure Analysis</h1>
        <p>Most common, highest-paying, and lowest-paying Medicare procedures</p>
    </div>
    """, unsafe_allow_html=True)

    # Top 20
    procs = filtered.groupby(['procedure_code', 'procedure_description']).agg(
        total_services=('total_services', 'sum'), avg_payment=('avg_medicare_payment', 'mean'),
    ).sort_values('total_services', ascending=False).head(20).reset_index()
    procs['label'] = procs['procedure_code'] + ' — ' + procs['procedure_description'].str[:40]

    fig = px.bar(procs, x='total_services', y='label', orientation='h',
                 color='total_services', color_continuous_scale='Teal',
                 labels={'total_services': 'Total Services', 'label': 'Procedure'})
    fig.update_layout(**chart_layout("Top 20 Most Common Medicare Procedures", height=600,
                     yaxis={'categoryorder': 'total ascending'}), coloraxis_showscale=False)
    fig.update_traces(hovertemplate='<b>%{y}</b><br>Services: %{x:,}<extra></extra>',
                     customdata=procs[['avg_payment']].values)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        f"The 20 most frequently billed HCPCS/CPT codes by total service volume. The most common is "
        f"<b>{procs['procedure_code'].iloc[0]}</b> — \"{procs['procedure_description'].iloc[0]}\" with "
        f"<b>{procs['total_services'].iloc[0]:,.0f}</b> total services. Office visits and E&M codes dominate.",
        problem="High-volume procedures are the most likely targets for payer audits, prior authorization "
                "requirements, and coding reviews. A single policy change affecting a top-20 procedure could "
                "impact thousands of claims. CareFlow AI should monitor payer policy updates for these codes "
                "and pre-populate authorization forms with commonly required documentation."
    ), unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        proc_pay = filtered.groupby(['procedure_code', 'procedure_description']).agg(
            avg_payment=('avg_medicare_payment', 'mean'), total_svc=('total_services', 'sum')).reset_index()
        proc_pay = proc_pay[proc_pay['total_svc'] >= 1000]
        top_pay = proc_pay.sort_values('avg_payment', ascending=False).head(20)
        top_pay['label'] = top_pay['procedure_code'] + ' — ' + top_pay['procedure_description'].str[:35]

        fig = px.bar(top_pay, x='avg_payment', y='label', orientation='h',
                     color='avg_payment', color_continuous_scale='Greens',
                     labels={'avg_payment': 'Avg Payment ($)', 'label': 'Procedure'})
        fig.update_layout(**chart_layout("Top 20 Highest-Paying (min 1K svc)", height=600,
                         yaxis={'categoryorder': 'total ascending'}), coloraxis_showscale=False, xaxis_tickprefix='$')
        fig.update_traces(hovertemplate='<b>%{y}</b><br>Avg Payment: $%{x:,.2f}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(analysis_box(
            "Top 20 procedures with the highest average Medicare payment (minimum 1,000 services for "
            "statistical significance). These are typically surgical procedures, complex imaging, and "
            "specialty treatments.",
            problem="High-paying procedures carry the most financial risk per denial. A single denied claim "
                    "for a procedure paying thousands of dollars has far greater impact than denying a routine "
                    "office visit. These claims need the most rigorous pre-submission review."
        ), unsafe_allow_html=True)

    with col2:
        low_pay = proc_pay.sort_values('avg_payment', ascending=True).head(20)
        low_pay['label'] = low_pay['procedure_code'] + ' — ' + low_pay['procedure_description'].str[:35]

        fig = px.bar(low_pay, x='avg_payment', y='label', orientation='h',
                     color='avg_payment', color_continuous_scale='Reds_r',
                     labels={'avg_payment': 'Avg Payment ($)', 'label': 'Procedure'})
        fig.update_layout(**chart_layout("Top 20 Lowest-Paying (min 1K svc)", height=600,
                         yaxis={'categoryorder': 'total descending'}), coloraxis_showscale=False, xaxis_tickprefix='$')
        fig.update_traces(hovertemplate='<b>%{y}</b><br>Avg Payment: $%{x:,.2f}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(analysis_box(
            "Lowest-paying procedures with at least 1,000 services. These are simple office visits, "
            "brief evaluations, and routine tests.",
            problem="While individual low-paying procedures seem harmless, their sheer volume creates cumulative "
                    "revenue risk. A batch denial of routine claims due to documentation deficiency can have "
                    "significant total impact. CareFlow AI should batch-validate high-volume claims before submission."
        ), unsafe_allow_html=True)

    st.markdown("---")

    # Services per Patient
    svc = filtered.dropna(subset=['total_patients', 'total_services'])
    svc = svc[svc['total_patients'] > 0].copy()
    svc['svc_per_patient'] = svc['total_services'] / svc['total_patients']
    ratio = svc.groupby('provider_specialty')['svc_per_patient'].mean().sort_values(ascending=False).head(20).reset_index()
    ratio.columns = ['Specialty', 'Avg Services per Patient']

    fig = px.bar(ratio, x='Avg Services per Patient', y='Specialty', orientation='h',
                 color='Avg Services per Patient', color_continuous_scale='Purples')
    fig.update_layout(**chart_layout("Top 20 Specialties by Services-per-Patient Ratio", height=600,
                     yaxis={'categoryorder': 'total ascending'}), coloraxis_showscale=False)
    fig.update_traces(hovertemplate='<b>%{y}</b><br>Svc/Patient: %{x:.1f}<extra></extra>')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        "This chart ranks specialties by how many services each patient receives on average. "
        "High ratios indicate specialties where patients need repeated treatments (dialysis, radiation, "
        "physical therapy). Low ratios indicate one-time consultations or evaluations.",
        problem="Specialties with high services-per-patient ratios generate the most recurring prior "
                "authorization requests. Initial authorization is not enough — these specialties need ongoing "
                "re-authorization. CareFlow AI should implement auto-renewal workflows for recurring treatment "
                "plans and predict when re-authorization is needed based on treatment frequency patterns."
    ), unsafe_allow_html=True)


# ============================================================
# PAGE 7: UTILIZATION & STATS
# ============================================================

elif page == "📈 Utilization & Stats":
    st.markdown("""
    <div class="main-header">
        <h1>📈 Utilization & Statistical Analysis</h1>
        <p>Scatter plots, correlation matrices, and statistical breakdowns</p>
    </div>
    """, unsafe_allow_html=True)

    # Scatter
    scatter = filtered.dropna(subset=['total_patients', 'total_services', 'avg_medicare_payment'])
    scatter = scatter[scatter['total_patients'] > 0]
    p99p = scatter['total_patients'].quantile(0.99)
    p99s = scatter['total_services'].quantile(0.99)
    scatter = scatter[(scatter['total_patients'] <= p99p) & (scatter['total_services'] <= p99s)]
    if len(scatter) > 5000:
        scatter = scatter.sample(5000, random_state=42)

    fig = px.scatter(
        scatter, x='total_patients', y='total_services',
        color='avg_medicare_payment', color_continuous_scale='YlGnBu', opacity=0.5,
        labels={'total_patients': 'Total Patients', 'total_services': 'Total Services',
                'avg_medicare_payment': 'Avg Payment ($)'},
        hover_data={'provider_specialty': True, 'avg_medicare_payment': ':$.2f',
                    'total_patients': ':,', 'total_services': ':,'},
    )
    fig.update_layout(**chart_layout("Patients vs Services (colored by Avg Payment)", height=550))
    fig.update_traces(marker=dict(size=5))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(analysis_box(
        "This scatter plot shows the relationship between the number of patients a provider sees and the "
        "total services rendered, for each provider-procedure combination. Color intensity represents "
        "average payment amount — darker dots = higher-paying services. Most providers cluster in the "
        "lower-left (few patients, few services), while a small number of high-volume providers appear "
        "in the upper-right. <b>Hover over any dot</b> to see specialty and exact values.",
        key_stats="Each dot = one provider billing one procedure. If a dot shows 100 patients and 300 services, "
                  "that means some patients received the procedure multiple times.",
        problem="High-volume providers (upper-right) face the greatest prior authorization burden. If a provider "
                "performs the same procedure on hundreds of patients, a single prior auth policy change could "
                "affect all of them simultaneously. CareFlow AI should batch similar authorization requests "
                "and proactively alert staff to policy changes affecting high-volume providers."
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Correlation
    st.markdown('<div class="section-header">🔗 Correlation Matrix</div>', unsafe_allow_html=True)
    numeric_cols = ['total_patients', 'total_services', 'total_patient_day_services',
                    'avg_submitted_charge', 'avg_medicare_allowed_amount',
                    'avg_medicare_payment', 'avg_medicare_standardized_amount']
    corr = filtered[numeric_cols].corr().round(2)
    labels = ['Patients', 'Services', 'Pt-Days', 'Charge', 'Allowed', 'Payment', 'Standardized']

    fig = ff.create_annotated_heatmap(
        z=corr.values, x=labels, y=labels,
        colorscale='RdBu_r', showscale=True, reversescale=False)
    fig.update_layout(**chart_layout("Correlation Matrix of Numeric Variables", height=550))
    st.plotly_chart(fig, use_container_width=True)

    corr_vals = corr.values
    st.markdown(analysis_box(
        "Pearson correlation between all numeric variables. Values range from -1 (perfect negative) to "
        "+1 (perfect positive). Red = positive correlation, blue = negative correlation.",
        key_stats=f"Key correlations: Charge ↔ Payment: {corr.iloc[3,5]:.2f} | "
                  f"Patients ↔ Services: {corr.iloc[0,1]:.2f} | "
                  f"Payment ↔ Allowed: {corr.iloc[4,5]:.2f}",
        problem="The imperfect correlation between charges and payments (not 1.0) means simply raising charges "
                "does NOT proportionally increase Medicare reimbursement. Many providers mistakenly believe "
                "higher charges yield higher payments. CareFlow AI should educate users that Medicare payment "
                "is based on fee schedules, not submitted charges, and that inflating charges only increases "
                "the write-off burden."
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Descriptive Stats
    st.markdown('<div class="section-header">📊 Descriptive Statistics</div>', unsafe_allow_html=True)
    desc = filtered[numeric_cols].describe().round(2)
    desc.columns = labels
    st.dataframe(desc.style.format("{:,.2f}"), use_container_width=True)

    st.markdown(analysis_box(
        "Full descriptive statistics (count, mean, std, min, 25%, 50%, 75%, max) for all numeric columns. "
        "Compare mean vs median (50%) — large differences indicate skewed distributions.",
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Missing values
    st.markdown('<div class="section-header">🔍 Data Quality — Missing Values</div>', unsafe_allow_html=True)
    missing = filtered.isnull().sum()
    missing_pct = (missing / len(filtered) * 100).round(2)
    missing_df = pd.DataFrame({'Missing Count': missing, 'Missing %': missing_pct})
    missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
    if len(missing_df) > 0:
        st.dataframe(missing_df, use_container_width=True)
        st.markdown(analysis_box(
            f"<b>{len(missing_df)}</b> columns have missing values. Columns with high missing rates may "
            f"need imputation or exclusion from analysis. Missing gender/credentials typically indicates "
            f"organizational providers (which don't have these attributes).",
        ), unsafe_allow_html=True)
    else:
        st.success("✅ No missing values! Data quality is excellent.")


# ============================================================
# PAGE 8: DATA TABLES
# ============================================================

elif page == "📋 Data Tables":
    st.markdown("""
    <div class="main-header">
        <h1>📋 Summary Data Tables</h1>
        <p>Per-specialty and per-state comprehensive statistics with CSV export</p>
    </div>
    """, unsafe_allow_html=True)

    # Payment definitions
    st.markdown("""
    <div class="analysis-box">
        <h4>📋 Payment Column Definitions</h4>
        <table style="width:100%; border-collapse: collapse; font-size: 0.85rem;">
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 6px;"><b>🏥 Provider Charges</b></td>
                <td style="padding: 6px;">What the provider bills — their "sticker price." Medicare almost never pays this full amount.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 6px;"><b>🏛️ Medicare Pays</b></td>
                <td style="padding: 6px;">What Medicare actually pays the provider — typically 80% of the Allowed Amount. This is <b>real revenue</b>.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 6px;"><b>👤 Patient Pays (est)</b></td>
                <td style="padding: 6px;">Estimated patient coinsurance — ~20% of the Allowed Amount. Calculated as: Allowed − Medicare Payment.</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 6px;"><b>❌ Write-Off</b></td>
                <td style="padding: 6px;">Provider charge minus allowed amount = unrealized revenue that nobody pays. NOT what the patient pays.</td>
            </tr>
            <tr>
                <td style="padding: 6px;"><b>Efficiency %</b></td>
                <td style="padding: 6px;">Medicare Payment / Provider Charge × 100. Lower = more revenue loss.</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # Per-Specialty
    st.markdown('<div class="section-header">🩺 Per-Specialty Summary (Top 25)</div>', unsafe_allow_html=True)
    spec_summary = filtered.groupby('provider_specialty').agg(
        Records=('provider_npi', 'count'), Providers=('provider_npi', 'nunique'),
        Provider_Charges=('avg_submitted_charge', 'mean'),
        Medicare_Pays=('avg_medicare_payment', 'mean'),
        Medicare_Median=('avg_medicare_payment', 'median'),
        Allowed=('avg_medicare_allowed_amount', 'mean'),
        Avg_Patients=('total_patients', 'mean'),
        Avg_Services=('total_services', 'mean'),
    ).sort_values('Records', ascending=False).head(25)
    spec_summary['Patient_Pays'] = spec_summary['Allowed'] - spec_summary['Medicare_Pays']
    spec_summary['Write_Off'] = spec_summary['Provider_Charges'] - spec_summary['Allowed']
    spec_summary['Efficiency'] = (spec_summary['Medicare_Pays'] / spec_summary['Provider_Charges'] * 100).round(1)
    spec_summary = spec_summary.drop(columns=['Allowed'])

    spec_display = spec_summary.copy()
    spec_display.columns = ['Records', 'Providers', '🏥 Provider Charges', '🏛️ Medicare Pays', '🏛️ Median Pay',
                            'Avg Patients', 'Avg Services', '👤 Patient Pays', '❌ Write-Off', 'Efficiency %']
    st.dataframe(spec_display.style.format({
        'Records': '{:,}', 'Providers': '{:,}', '🏥 Provider Charges': '${:,.2f}',
        '🏛️ Medicare Pays': '${:,.2f}', '🏛️ Median Pay': '${:,.2f}',
        'Avg Patients': '{:.1f}', 'Avg Services': '{:.1f}',
        '👤 Patient Pays': '${:,.2f}', '❌ Write-Off': '${:,.2f}', 'Efficiency %': '{:.1f}%',
    }), use_container_width=True, height=700)

    st.markdown(analysis_box(
        "Comprehensive per-specialty statistics. Each row shows a medical specialty's record count, unique "
        "provider count, average charges, actual Medicare payments, estimated patient coinsurance, write-off "
        "amount, and payment efficiency. Sort by any column by clicking the column header.",
        key_stats="Efficiency = Medicare Payment / Provider Charge × 100%. Lower efficiency = more revenue loss. "
                  "Specialties below 30% efficiency face the most severe shortfalls."
    ), unsafe_allow_html=True)

    st.markdown("---")

    # Per-State
    st.markdown('<div class="section-header">🗺️ Per-State Summary (All States)</div>', unsafe_allow_html=True)
    state_summary = filtered.groupby('provider_state').agg(
        Records=('provider_npi', 'count'), Providers=('provider_npi', 'nunique'),
        Specialties=('provider_specialty', 'nunique'),
        Provider_Charges=('avg_submitted_charge', 'mean'),
        Medicare_Pays=('avg_medicare_payment', 'mean'),
        Allowed=('avg_medicare_allowed_amount', 'mean'),
        Avg_Patients=('total_patients', 'mean'),
    ).sort_values('Records', ascending=False)
    state_summary['Patient_Pays'] = state_summary['Allowed'] - state_summary['Medicare_Pays']
    state_summary['Write_Off'] = state_summary['Provider_Charges'] - state_summary['Allowed']
    state_summary['Efficiency'] = (state_summary['Medicare_Pays'] / state_summary['Provider_Charges'] * 100).round(1)
    state_summary = state_summary.drop(columns=['Allowed'])

    state_display = state_summary.copy()
    state_display.columns = ['Records', 'Providers', 'Specialties', '🏥 Provider Charges', '🏛️ Medicare Pays',
                             'Avg Patients', '👤 Patient Pays', '❌ Write-Off', 'Efficiency %']
    st.dataframe(state_display.style.format({
        'Records': '{:,}', 'Providers': '{:,}', 'Specialties': '{:,}',
        '🏥 Provider Charges': '${:,.2f}', '🏛️ Medicare Pays': '${:,.2f}',
        'Avg Patients': '{:.1f}', '👤 Patient Pays': '${:,.2f}',
        '❌ Write-Off': '${:,.2f}', 'Efficiency %': '{:.1f}%',
    }), use_container_width=True, height=700)

    st.markdown(analysis_box(
        "State-level statistics showing records, providers, specialties, payment breakdown, and efficiency. "
        "States with higher charges but similar payments have larger write-offs — look for low efficiency "
        "percentages. These states may have providers setting charges based on commercial insurance rates.",
        key_stats="Compare states with similar record counts but different efficiency — this reveals geographic "
                  "pricing patterns and potential revenue optimization opportunities."
    ), unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        csv_spec = spec_summary.to_csv()
        st.download_button("📥 Download Specialty Table (CSV)", csv_spec, "specialty_summary.csv", "text/csv")
    with col2:
        csv_state = state_summary.to_csv()
        st.download_button("📥 Download State Table (CSV)", csv_state, "state_summary.csv", "text/csv")
