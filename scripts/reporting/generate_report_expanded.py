"""
CareFlow AI — Expanded CMS Medicare Data Analysis Report
==========================================================
Generates an in-depth .docx report with 20+ charts and
comprehensive statistical analysis from the PostgreSQL dataset.

Usage:
    python generate_report_expanded.py

Output:
    reports/CareFlow_AI_Expanded_Analysis_Report.docx
"""

import os
import time
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sqlalchemy import create_engine, text
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

# ============================================================
# CONFIGURATION
# ============================================================

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'careflow_ai',
    'user': 'postgres',
    'password': 'postgres',
}
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

REPORTS_DIR = os.path.join(os.getcwd(), 'reports')
CHARTS_DIR = os.path.join(REPORTS_DIR, 'charts_expanded')
REPORT_FILENAME = 'CareFlow_AI_Expanded_Analysis_Report_v2.docx'

sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'sans-serif'

C = {
    'blue': '#3A7CA5', 'green': '#6BAA75', 'coral': '#E07A5F',
    'teal': '#2A9D8F', 'amber': '#E9C46A', 'red': '#E76F51',
    'navy': '#264653', 'purple': '#7B2D8E', 'pink': '#D1477A',
    'dark': '#1F2933', 'muted': '#667085',
}
PALETTE = [C['blue'], C['green'], C['coral'], C['teal'], C['amber'],
           C['red'], C['navy'], C['purple'], C['pink']]

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def save(fig, path):
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    log(f"  Chart: {os.path.basename(path)}")

def fmt_money(x, _=None):
    return f'${x:,.0f}'

def fmt_num(x, _=None):
    return f'{x:,.0f}'

def load_data(engine):
    """Load full dataset from PostgreSQL."""
    log("Loading data from PostgreSQL...")
    df = pd.read_sql("SELECT * FROM cms_medicare_providers", engine)
    log(f"Loaded {len(df):,} records")
    return df


# ============================================================
# ALL CHART FUNCTIONS
# ============================================================

def c01_specialty_bar(df, d):
    top = df['provider_specialty'].value_counts().head(20)
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(top.index[::-1], top.values[::-1], color=C['blue'], edgecolor='white')
    ax.set_xlabel('Number of Records')
    ax.set_title('Top 20 Provider Specialties', fontsize=14, fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_num))
    for i, v in enumerate(top.values[::-1]):
        ax.text(v + max(top.values)*0.01, i, f'{v:,}', va='center', fontsize=8)
    save(fig, os.path.join(d, '01_specialty_bar.png'))

def c02_state_bar(df, d):
    top = df['provider_state'].value_counts().head(20)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(top.index, top.values, color=C['teal'], edgecolor='white')
    ax.set_ylabel('Records')
    ax.set_title('Top 20 States by Provider Records', fontsize=14, fontweight='bold')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_num))
    plt.xticks(rotation=45)
    save(fig, os.path.join(d, '02_state_bar.png'))

def c03_payment_vs_charge(df, d):
    p = df.groupby('provider_specialty').agg(
        charge=('avg_submitted_charge', 'mean'),
        payment=('avg_medicare_payment', 'mean'),
    ).sort_values('charge', ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(p))
    ax.bar([i-0.175 for i in x], p['charge'], 0.35, label='Submitted Charge', color=C['blue'])
    ax.bar([i+0.175 for i in x], p['payment'], 0.35, label='Medicare Payment', color=C['green'])
    ax.set_xticks(x)
    ax.set_xticklabels(p.index, rotation=45, ha='right', fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    ax.set_title('Submitted Charges vs Medicare Payments by Specialty', fontsize=14, fontweight='bold')
    ax.legend()
    save(fig, os.path.join(d, '03_payment_vs_charge.png'))

def c04_payment_gap_state(df, d):
    g = df.groupby('provider_state').agg(
        charge=('avg_submitted_charge', 'mean'), payment=('avg_medicare_payment', 'mean'))
    g['gap'] = g['charge'] - g['payment']
    g = g.sort_values('gap', ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(g.index[::-1], g['gap'].values[::-1], color=C['coral'], edgecolor='white')
    ax.set_xlabel('Average Gap ($)')
    ax.set_title('Top 20 States by Charge-to-Payment Gap', fontsize=14, fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    save(fig, os.path.join(d, '04_payment_gap_state.png'))

def c05_payment_hist(df, d):
    pay = df['avg_medicare_payment'].dropna()
    q99 = pay.quantile(0.99)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(pay[pay <= q99], bins=80, color=C['blue'], edgecolor='white', alpha=0.85)
    ax.axvline(pay.median(), color=C['coral'], ls='--', lw=2, label=f'Median: ${pay.median():,.2f}')
    ax.axvline(pay.mean(), color=C['green'], ls='--', lw=2, label=f'Mean: ${pay.mean():,.2f}')
    ax.set_xlabel('Avg Medicare Payment ($)')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Medicare Payments (99th percentile)', fontsize=14, fontweight='bold')
    ax.legend()
    save(fig, os.path.join(d, '05_payment_hist.png'))

def c06_scatter_utilization(df, d):
    s = df.dropna(subset=['total_patients', 'total_services', 'avg_medicare_payment'])
    s = s[s['total_patients'] > 0]
    p99p = s['total_patients'].quantile(0.99)
    p99s = s['total_services'].quantile(0.99)
    s = s[(s['total_patients'] <= p99p) & (s['total_services'] <= p99s)]
    if len(s) > 3000: s = s.sample(3000, random_state=42)
    fig, ax = plt.subplots(figsize=(10, 6))
    sc = ax.scatter(s['total_patients'], s['total_services'],
                    c=s['avg_medicare_payment'], cmap='YlGnBu', alpha=0.4, s=12, edgecolors='none')
    plt.colorbar(sc, label='Avg Payment ($)', ax=ax)
    ax.set_xlabel('Total Patients')
    ax.set_ylabel('Total Services')
    ax.set_title('Patients vs Services (colored by Avg Payment)', fontsize=14, fontweight='bold')
    save(fig, os.path.join(d, '06_scatter_utilization.png'))

def c07_top_procedures(df, d):
    p = df.groupby(['procedure_code','procedure_description']).agg(
        total=('total_services','sum')).sort_values('total', ascending=False).head(20).reset_index()
    p['label'] = p['procedure_code'] + ' - ' + p['procedure_description'].str[:35]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(p['label'][::-1], p['total'][::-1], color=C['teal'], edgecolor='white')
    ax.set_xlabel('Total Services')
    ax.set_title('Top 20 Most Common Procedures', fontsize=14, fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_num))
    save(fig, os.path.join(d, '07_top_procedures.png'))

def c08_gender_pie(df, d):
    g = df['provider_gender'].dropna().value_counts()
    labels = {'M': 'Male', 'F': 'Female'}
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(g.values, labels=[labels.get(k,k) for k in g.index], autopct='%1.1f%%',
           colors=[C['blue'], C['coral']], startangle=90, textprops={'fontsize': 12})
    ax.set_title('Provider Gender Distribution', fontsize=14, fontweight='bold')
    save(fig, os.path.join(d, '08_gender_pie.png'))

def c09_entity_pie(df, d):
    e = df['provider_entity_type'].dropna().value_counts()
    labels = {'I': 'Individual', 'O': 'Organization'}
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(e.values, labels=[labels.get(k,k) for k in e.index], autopct='%1.1f%%',
           colors=[C['green'], C['amber']], startangle=90, textprops={'fontsize': 12})
    ax.set_title('Individual vs Organization Providers', fontsize=14, fontweight='bold')
    save(fig, os.path.join(d, '09_entity_pie.png'))

def c10_payment_by_gender(df, d):
    g = df.groupby('provider_gender')['avg_medicare_payment'].agg(['mean','median']).dropna()
    labels = {'M': 'Male', 'F': 'Female'}
    fig, ax = plt.subplots(figsize=(7, 5))
    x = range(len(g))
    ax.bar([i-0.15 for i in x], g['mean'], 0.3, label='Mean', color=C['blue'])
    ax.bar([i+0.15 for i in x], g['median'], 0.3, label='Median', color=C['coral'])
    ax.set_xticks(x)
    ax.set_xticklabels([labels.get(k,k) for k in g.index])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    ax.set_title('Average Medicare Payment by Provider Gender', fontsize=14, fontweight='bold')
    ax.legend()
    save(fig, os.path.join(d, '10_payment_by_gender.png'))

def c11_payment_by_entity(df, d):
    e = df.groupby('provider_entity_type')['avg_medicare_payment'].agg(['mean','median']).dropna()
    labels = {'I': 'Individual', 'O': 'Organization'}
    fig, ax = plt.subplots(figsize=(7, 5))
    x = range(len(e))
    ax.bar([i-0.15 for i in x], e['mean'], 0.3, label='Mean', color=C['green'])
    ax.bar([i+0.15 for i in x], e['median'], 0.3, label='Median', color=C['amber'])
    ax.set_xticks(x)
    ax.set_xticklabels([labels.get(k,k) for k in e.index])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    ax.set_title('Average Medicare Payment by Entity Type', fontsize=14, fontweight='bold')
    ax.legend()
    save(fig, os.path.join(d, '11_payment_by_entity.png'))

def c12_place_of_service(df, d):
    pos = df['place_of_service'].dropna().value_counts()
    labels = {'F': 'Facility', 'O': 'Office'}
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(pos.values, labels=[labels.get(k,k) for k in pos.index], autopct='%1.1f%%',
           colors=[C['navy'], C['teal']], startangle=90, textprops={'fontsize': 12})
    ax.set_title('Place of Service Distribution', fontsize=14, fontweight='bold')
    save(fig, os.path.join(d, '12_place_of_service.png'))

def c13_drug_vs_nondrug(df, d):
    dr = df['is_drug_service'].dropna().value_counts()
    labels = {'Y': 'Drug Services', 'N': 'Non-Drug Services'}
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(dr.values, labels=[labels.get(k,k) for k in dr.index], autopct='%1.1f%%',
           colors=[C['purple'], C['green']], startangle=90, textprops={'fontsize': 12})
    ax.set_title('Drug vs Non-Drug Services', fontsize=14, fontweight='bold')
    save(fig, os.path.join(d, '13_drug_vs_nondrug.png'))

def c14_payment_by_place(df, d):
    p = df.groupby('place_of_service')['avg_medicare_payment'].agg(['mean','median']).dropna()
    labels = {'F': 'Facility', 'O': 'Office'}
    fig, ax = plt.subplots(figsize=(7, 5))
    x = range(len(p))
    ax.bar([i-0.15 for i in x], p['mean'], 0.3, label='Mean', color=C['navy'])
    ax.bar([i+0.15 for i in x], p['median'], 0.3, label='Median', color=C['teal'])
    ax.set_xticks(x)
    ax.set_xticklabels([labels.get(k,k) for k in p.index])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    ax.set_title('Average Payment: Facility vs Office', fontsize=14, fontweight='bold')
    ax.legend()
    save(fig, os.path.join(d, '14_payment_by_place.png'))

def c15_top_cities(df, d):
    cities = df.groupby(['provider_city','provider_state']).size().sort_values(ascending=False).head(20)
    labels = [f"{city}, {state}" for city, state in cities.index]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(labels[::-1], cities.values[::-1], color=C['blue'], edgecolor='white')
    ax.set_xlabel('Number of Records')
    ax.set_title('Top 20 Cities by Provider Records', fontsize=14, fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_num))
    save(fig, os.path.join(d, '15_top_cities.png'))

def c16_credentials(df, d):
    creds = df['provider_credentials'].dropna().value_counts().head(15)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(creds.index, creds.values, color=C['teal'], edgecolor='white')
    ax.set_ylabel('Records')
    ax.set_title('Top 15 Provider Credentials', fontsize=14, fontweight='bold')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_num))
    plt.xticks(rotation=45, ha='right')
    save(fig, os.path.join(d, '16_credentials.png'))

def c17_highest_paying_procedures(df, d):
    p = df.groupby(['procedure_code','procedure_description']).agg(
        avg_pay=('avg_medicare_payment','mean'),
        count=('total_services','sum')
    ).reset_index()
    p = p[p['count'] >= 1000].sort_values('avg_pay', ascending=False).head(20)
    p['label'] = p['procedure_code'] + ' - ' + p['procedure_description'].str[:30]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(p['label'][::-1], p['avg_pay'][::-1], color=C['green'], edgecolor='white')
    ax.set_xlabel('Avg Medicare Payment ($)')
    ax.set_title('Top 20 Highest-Paying Procedures (min 1,000 services)', fontsize=14, fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    save(fig, os.path.join(d, '17_highest_paying_procs.png'))

def c18_lowest_paying_procedures(df, d):
    p = df.groupby(['procedure_code','procedure_description']).agg(
        avg_pay=('avg_medicare_payment','mean'),
        count=('total_services','sum')
    ).reset_index()
    p = p[p['count'] >= 1000].sort_values('avg_pay', ascending=True).head(20)
    p['label'] = p['procedure_code'] + ' - ' + p['procedure_description'].str[:30]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(p['label'][::-1], p['avg_pay'][::-1], color=C['coral'], edgecolor='white')
    ax.set_xlabel('Avg Medicare Payment ($)')
    ax.set_title('Top 20 Lowest-Paying Procedures (min 1,000 services)', fontsize=14, fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    save(fig, os.path.join(d, '18_lowest_paying_procs.png'))

def c19_boxplot_specialty_payment(df, d):
    top5 = df['provider_specialty'].value_counts().head(8).index.tolist()
    sub = df[df['provider_specialty'].isin(top5)][['provider_specialty','avg_medicare_payment']].dropna()
    q99 = sub['avg_medicare_payment'].quantile(0.95)
    sub = sub[sub['avg_medicare_payment'] <= q99]
    fig, ax = plt.subplots(figsize=(12, 5))
    sub.boxplot(by='provider_specialty', column='avg_medicare_payment', ax=ax)
    ax.set_title('Payment Distribution by Top 8 Specialties (95th pct)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Specialty')
    ax.set_ylabel('Avg Medicare Payment ($)')
    plt.suptitle('')
    plt.xticks(rotation=30, ha='right', fontsize=8)
    save(fig, os.path.join(d, '19_boxplot_specialty.png'))

def c20_payment_efficiency(df, d):
    e = df.groupby('provider_specialty').agg(
        charge=('avg_submitted_charge','mean'), payment=('avg_medicare_payment','mean'))
    e['efficiency'] = (e['payment'] / e['charge'] * 100).round(1)
    e = e.sort_values('efficiency', ascending=True).head(20)
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = [C['red'] if v < 30 else C['coral'] if v < 50 else C['amber'] for v in e['efficiency']]
    ax.barh(e.index[::-1], e['efficiency'].values[::-1], color=colors[::-1], edgecolor='white')
    ax.set_xlabel('Payment Efficiency (%)')
    ax.set_title('Bottom 20 Specialties by Payment Efficiency (Payment/Charge %)', fontsize=14, fontweight='bold')
    ax.axvline(50, color=C['muted'], ls='--', lw=1, alpha=0.5)
    for i, v in enumerate(e['efficiency'].values[::-1]):
        ax.text(v + 0.5, i, f'{v:.1f}%', va='center', fontsize=8)
    save(fig, os.path.join(d, '20_payment_efficiency.png'))

def c21_services_per_patient(df, d):
    sub = df.dropna(subset=['total_patients','total_services'])
    sub = sub[sub['total_patients'] > 0]
    sub['svc_per_patient'] = sub['total_services'] / sub['total_patients']
    by_spec = sub.groupby('provider_specialty')['svc_per_patient'].mean().sort_values(ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(by_spec.index[::-1], by_spec.values[::-1], color=C['purple'], edgecolor='white')
    ax.set_xlabel('Average Services per Patient')
    ax.set_title('Top 20 Specialties by Services-per-Patient Ratio', fontsize=14, fontweight='bold')
    for i, v in enumerate(by_spec.values[::-1]):
        ax.text(v + 0.1, i, f'{v:.1f}', va='center', fontsize=8)
    save(fig, os.path.join(d, '21_services_per_patient.png'))

def c22_correlation_heatmap(df, d):
    nums = df[['total_patients','total_services','total_patient_day_services',
               'avg_submitted_charge','avg_medicare_allowed_amount',
               'avg_medicare_payment','avg_medicare_standardized_amount']].dropna()
    corr = nums.corr()
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, ax=ax, linewidths=0.5, cbar_kws={'shrink': 0.8})
    ax.set_title('Correlation Matrix of Numeric Variables', fontsize=14, fontweight='bold', pad=15)
    plt.xticks(fontsize=7, rotation=45, ha='right')
    plt.yticks(fontsize=7)
    save(fig, os.path.join(d, '22_correlation_heatmap.png'))

def c23_medicare_participation(df, d):
    mp = df['medicare_participating'].dropna().value_counts()
    labels = {'Y': 'Participating', 'N': 'Non-Participating'}
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(mp.values, labels=[labels.get(k,k) for k in mp.index], autopct='%1.1f%%',
           colors=[C['green'], C['coral']], startangle=90, textprops={'fontsize': 12})
    ax.set_title('Medicare Participation Rate', fontsize=14, fontweight='bold')
    save(fig, os.path.join(d, '23_medicare_participation.png'))

def c24_charge_hist(df, d):
    ch = df['avg_submitted_charge'].dropna()
    q99 = ch.quantile(0.99)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(ch[ch <= q99], bins=80, color=C['navy'], edgecolor='white', alpha=0.85)
    ax.axvline(ch.median(), color=C['coral'], ls='--', lw=2, label=f'Median: ${ch.median():,.2f}')
    ax.axvline(ch.mean(), color=C['green'], ls='--', lw=2, label=f'Mean: ${ch.mean():,.2f}')
    ax.set_xlabel('Avg Submitted Charge ($)')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Submitted Charges (99th percentile)', fontsize=14, fontweight='bold')
    ax.legend()
    save(fig, os.path.join(d, '24_charge_hist.png'))

def c25_payment_by_state_avg(df, d):
    s = df.groupby('provider_state')['avg_medicare_payment'].mean().sort_values(ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(s.index, s.values, color=C['teal'], edgecolor='white')
    ax.set_ylabel('Avg Medicare Payment ($)')
    ax.set_title('Top 20 States by Average Medicare Payment', fontsize=14, fontweight='bold')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    plt.xticks(rotation=45)
    save(fig, os.path.join(d, '25_payment_by_state.png'))

def c28_who_pays_what(df, d):
    """Stacked bar showing Provider Charge = Medicare + Patient + Write-off."""
    avg_charge = df['avg_submitted_charge'].mean()
    avg_allowed = df['avg_medicare_allowed_amount'].mean()
    avg_payment = df['avg_medicare_payment'].mean()
    patient_cost = avg_allowed - avg_payment
    write_off = avg_charge - avg_allowed

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = [avg_payment, patient_cost, write_off]
    labels = [f'Medicare Pays\n${avg_payment:,.2f}',
              f'Patient Pays\n${patient_cost:,.2f}',
              f'Write-Off\n${write_off:,.2f}']
    colors = [C['teal'], C['amber'], C['coral']]
    bottom = 0
    for val, lbl, col in zip(bars, labels, colors):
        ax.bar('Average Service', val, bottom=bottom, color=col, label=lbl, edgecolor='white', width=0.5)
        ax.text(0, bottom + val/2, lbl, ha='center', va='center', fontsize=10, fontweight='bold')
        bottom += val
    ax.set_ylabel('Amount ($)')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    ax.set_title(f'Who Pays What? (Total Charge: ${avg_charge:,.2f})', fontsize=14, fontweight='bold')
    ax.set_ylim(0, avg_charge * 1.05)
    ax.legend(loc='upper right')
    save(fig, os.path.join(d, '28_who_pays_what.png'))

def c29_who_pays_by_specialty(df, d):
    """Stacked horizontal bar: Medicare + Patient + Write-off by specialty."""
    sp = df.groupby('provider_specialty').agg(
        charge=('avg_submitted_charge','mean'),
        allowed=('avg_medicare_allowed_amount','mean'),
        payment=('avg_medicare_payment','mean'),
    ).sort_values('charge', ascending=False).head(12)
    sp['patient'] = sp['allowed'] - sp['payment']
    sp['writeoff'] = sp['charge'] - sp['allowed']

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(sp.index[::-1], sp['payment'].values[::-1], color=C['teal'], label='Medicare Pays', edgecolor='white')
    ax.barh(sp.index[::-1], sp['patient'].values[::-1], left=sp['payment'].values[::-1],
            color=C['amber'], label='Patient Pays (est.)', edgecolor='white')
    ax.barh(sp.index[::-1], sp['writeoff'].values[::-1],
            left=(sp['payment'] + sp['patient']).values[::-1],
            color=C['coral'], label='Write-Off (lost)', edgecolor='white')
    ax.set_xlabel('Amount ($)')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    ax.set_title('Who Pays What by Specialty (Top 12 Most Expensive)', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    save(fig, os.path.join(d, '29_who_pays_by_specialty.png'))

def c26_revenue_gap_specialty(df, d):
    """Revenue gap by specialty — overlaid bar chart."""
    gap = df.groupby('provider_specialty').agg(
        charge=('avg_submitted_charge', 'mean'),
        payment=('avg_medicare_payment', 'mean'),
        count=('provider_npi', 'count')
    )
    gap['gap'] = gap['charge'] - gap['payment']
    gap = gap.sort_values('gap', ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(12, 8))
    y = range(len(gap))
    ax.barh([i for i in y], gap['charge'].values, 0.4, label='Avg Charge', color=C['blue'], alpha=0.8)
    ax.barh([i + 0.4 for i in y], gap['payment'].values, 0.4, label='Avg Payment', color=C['green'], alpha=0.8)
    ax.set_yticks([i + 0.2 for i in y])
    ax.set_yticklabels(gap.index, fontsize=8)
    ax.set_xlabel('Amount ($)')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_money))
    ax.set_title('Revenue Gap by Specialty: Charges vs Payments (Top 20 Gaps)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.invert_yaxis()
    save(fig, os.path.join(d, '26_revenue_gap_specialty.png'))

def c27_unique_providers_state(df, d):
    """Unique providers per state."""
    provs = df.groupby('provider_state')['provider_npi'].nunique().sort_values(ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(provs.index, provs.values, color=C['navy'], edgecolor='white')
    ax.set_ylabel('Unique Providers')
    ax.set_title('Top 20 States by Number of Unique Providers (NPI)', fontsize=14, fontweight='bold')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_num))
    plt.xticks(rotation=45)
    save(fig, os.path.join(d, '27_unique_providers_state.png'))


# ============================================================
# DOCX REPORT BUILDER
# ============================================================

def h(doc, text, level=1):
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = RGBColor(0x1F, 0x29, 0x33)

def p(doc, text, bold=False, italic=False, sz=11, align=None):
    para = doc.add_paragraph()
    run = para.add_run(text)
    run.font.size = Pt(sz)
    run.bold = bold
    run.italic = italic
    if align: para.alignment = align
    return para

def img(doc, path, w=Inches(6.0), cap=None):
    doc.add_picture(path, width=w)
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if cap:
        c = doc.add_paragraph()
        r = c.add_run(cap)
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0x66, 0x70, 0x85)
        r.italic = True
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER

def add_stats_table(doc, rows_data, headers=('Metric', 'Value')):
    t = doc.add_table(rows=1, cols=len(headers), style='Light Grid Accent 1')
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, hdr in enumerate(headers):
        t.rows[0].cells[i].text = hdr
    for row in rows_data:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
    doc.add_paragraph()


def build_report(df, cd, out):
    log("Building report document...")
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    # Key stats
    n = len(df)
    n_providers = df['provider_npi'].nunique()
    n_specialties = df['provider_specialty'].nunique()
    n_states = df['provider_state'].nunique()
    n_procedures = df['procedure_code'].nunique()
    n_cities = df['provider_city'].nunique()
    avg_charge = df['avg_submitted_charge'].mean()
    med_charge = df['avg_submitted_charge'].median()
    avg_pay = df['avg_medicare_payment'].mean()
    med_pay = df['avg_medicare_payment'].median()
    avg_allowed = df['avg_medicare_allowed_amount'].mean()
    avg_std = df['avg_medicare_standardized_amount'].mean()
    avg_gap = avg_charge - avg_pay
    gap_pct = (1 - avg_pay / avg_charge) * 100
    avg_patients = df['total_patients'].mean()
    med_patients = df['total_patients'].median()
    avg_services = df['total_services'].mean()
    med_services = df['total_services'].median()
    max_pay = df['avg_medicare_payment'].max()
    min_pay = df['avg_medicare_payment'].min()

    # ── TITLE PAGE ──
    doc.add_paragraph()
    doc.add_paragraph()
    title = doc.add_heading('CareFlow AI', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_heading('CMS Medicare Data — Expanded Analysis Report', level=1)
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    p(doc, f'Records Analyzed: {n:,}', align=WD_ALIGN_PARAGRAPH.CENTER)
    p(doc, f'Unique Providers: {n_providers:,}', align=WD_ALIGN_PARAGRAPH.CENTER)
    p(doc, f'Report Generated: {time.strftime("%B %d, %Y at %I:%M %p")}', align=WD_ALIGN_PARAGRAPH.CENTER)
    p(doc, 'Source: Centers for Medicare & Medicaid Services (CMS)', italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_page_break()

    # ── 1. EXECUTIVE SUMMARY ──
    h(doc, '1. Executive Summary')
    p(doc, f'This expanded report analyzes {n:,} Medicare provider-service records covering '
           f'{n_providers:,} unique healthcare providers across {n_specialties} medical specialties, '
           f'{n_states} states/territories, and {n_procedures:,} distinct procedures in {n_cities:,} cities.')
    p(doc, 'Key Statistics at a Glance:', bold=True)
    add_stats_table(doc, [
        ('Total Records', f'{n:,}'),
        ('Unique Providers (NPI)', f'{n_providers:,}'),
        ('Unique Specialties', f'{n_specialties}'),
        ('Unique Procedures (HCPCS)', f'{n_procedures:,}'),
        ('States/Territories', f'{n_states}'),
        ('Cities', f'{n_cities:,}'),
        ('PROVIDER: Avg Submitted Charge', f'${avg_charge:,.2f}'),
        ('PROVIDER: Median Submitted Charge', f'${med_charge:,.2f}'),
        ('MEDICARE: Avg Allowed Amount', f'${avg_allowed:,.2f}'),
        ('MEDICARE: Avg Payment to Provider', f'${avg_pay:,.2f}'),
        ('MEDICARE: Median Payment to Provider', f'${med_pay:,.2f}'),
        ('MEDICARE: Avg Standardized Amount', f'${avg_std:,.2f}'),
        ('PATIENT: Est. Avg Out-of-Pocket (20% coinsurance)', f'${avg_allowed - avg_pay:,.2f}'),
        ('WRITE-OFF: Avg Charge-to-Payment Gap', f'${avg_gap:,.2f} ({gap_pct:.1f}%)'),
        ('Max Medicare Payment', f'${max_pay:,.2f}'),
        ('Min Medicare Payment', f'${min_pay:,.2f}'),
        ('Avg Patients per Provider-Service', f'{avg_patients:,.1f}'),
        ('Median Patients per Provider-Service', f'{med_patients:,.1f}'),
        ('Avg Services per Provider-Procedure', f'{avg_services:,.1f}'),
        ('Median Services per Provider-Procedure', f'{med_services:,.1f}'),
    ])
    doc.add_page_break()

    # ── 1.5 PAYMENT FIELD DEFINITIONS ──
    h(doc, '1.5 Payment Field Definitions — Who Pays What?')
    p(doc, 'The CMS dataset contains 4 payment-related fields. Understanding who each amount belongs '
           'to is critical for interpreting every chart in this report:', bold=True)
    add_stats_table(doc, [
        ('Avg Submitted Charge', 'PROVIDER (billed amount)',
         'The price the provider charges — their "sticker price." Medicare almost never pays this full amount.'),
        ('Avg Medicare Allowed Amount', 'MEDICARE (approved max)',
         'The maximum Medicare approves for this service. This is the payment ceiling.'),
        ('Avg Medicare Payment', 'MEDICARE (actual payment)',
         'What Medicare actually pays the provider — typically 80% of the Allowed Amount. This is real revenue.'),
        ('Avg Medicare Standardized Amount', 'MEDICARE (geo-adjusted)',
         'Same as Medicare Payment but adjusted for geographic cost differences. Used for fair state comparisons.'),
    ], headers=('Field', 'Who Pays/Sets This', 'What It Means'))

    p(doc, 'Payment Flow Summary:', bold=True)
    p(doc, 'Provider charges $100 (Submitted Charge) → Medicare approves $40 (Allowed Amount) '
           '→ Medicare pays $32 to provider (80% of Allowed) → Patient pays $8 coinsurance (20% of Allowed) '
           '→ Provider writes off $60 (Charge minus Allowed = lost revenue)')

    p(doc, 'What the Patient Pays:', bold=True)
    p(doc, f'Patient cost is NOT a separate column, but can be calculated: '
           f'Patient Cost = Allowed Amount − Medicare Payment ≈ 20% of Allowed Amount. '
           f'Average estimated patient cost: ${avg_allowed - avg_pay:,.2f} per service.')

    p(doc, 'What the "Gap" or "Write-Off" Means:', bold=True)
    p(doc, f'Gap = Submitted Charge − Medicare Payment = ${avg_gap:,.2f}. '
           f'This is NOT what the patient pays. It is unrealized revenue — the provider billed it '
           f'but neither Medicare nor the patient pays it. The provider must write it off.')

    img(doc, os.path.join(cd, '28_who_pays_what.png'), cap='Figure: Who Pays What (Average per Service)')
    img(doc, os.path.join(cd, '29_who_pays_by_specialty.png'), cap='Figure: Who Pays What by Specialty')
    doc.add_page_break()

    # ── 1.6 COMPLETE DATA DICTIONARY ──
    h(doc, '1.6 Complete Data Dictionary — Every Column Explained')
    p(doc, f'The dataset contains {len(df.columns)} columns across {n:,} records. '
           f'Each row represents one provider-procedure combination — a single provider billing '
           f'a single procedure code. Below is a detailed explanation of every column.')

    h(doc, 'Provider Identification', level=2)
    add_stats_table(doc, [
        ('provider_npi', 'Integer (10 digits)',
         f'{n_providers:,} unique values',
         'National Provider Identifier — a unique 10-digit ID assigned to every healthcare '
         'provider by CMS. This is the primary key for identifying providers. '
         'One provider can appear in multiple rows (one row per procedure they bill).'),
        ('provider_entity_type', 'Character (I/O)',
         f'I = Individual, O = Organization',
         'Whether the provider is an individual person (physician, nurse, therapist) or an '
         'organization (hospital, clinic, lab, imaging center). Organizations typically have '
         'higher billing volumes and more expensive procedures.'),
        ('provider_last_name', 'Text',
         'Provider surname or organization name',
         'Last name for individual providers, or the full organization name for entity type "O". '
         'Used for provider identification and matching.'),
        ('provider_first_name', 'Text',
         'Provider first name (individuals only)',
         'First name of the individual provider. NULL/blank for organizations. '
         'Combined with last name and NPI for unique provider identification.'),
        ('provider_middle_initial', 'Character',
         'Single letter or blank',
         'Middle initial of the provider. Often blank. Used for disambiguation '
         'when multiple providers share the same first and last name.'),
        ('provider_credentials', 'Text',
         f'e.g., M.D., D.O., NP, PA, CRNA',
         'Professional credentials/degrees. M.D. = Doctor of Medicine, D.O. = Doctor of '
         'Osteopathic Medicine, NP = Nurse Practitioner, PA = Physician Assistant, '
         'CRNA = Certified Registered Nurse Anesthetist. Different credentials have '
         'different scope-of-practice rules and prior authorization requirements.'),
        ('provider_gender', 'Character (M/F)',
         'M = Male, F = Female, blank for orgs',
         'Gender of the individual provider. Blank/NULL for organizations. '
         'Used for workforce demographic analysis and payment equity studies.'),
    ], headers=('Column Name', 'Data Type', 'Values', 'Detailed Description'))

    h(doc, 'Provider Location', level=2)
    add_stats_table(doc, [
        ('provider_street_address', 'Text',
         'Street address of practice',
         'The physical street address where the provider practices. Used for geographic '
         'analysis and mapping. Some providers have multiple practice locations.'),
        ('provider_city', 'Text',
         f'{n_cities:,} unique cities',
         'City where the provider is located. Urban centers like New York, Houston, and Chicago '
         'have the most providers. Used for city-level access and concentration analysis.'),
        ('provider_state', 'Text (2-letter code)',
         f'{n_states} states/territories',
         'Two-letter state abbreviation (e.g., CA, TX, NY). Includes all 50 states, DC, '
         'Puerto Rico, and other US territories. Medicare fee schedules and Geographic Practice '
         'Cost Indices (GPCI) vary by state, directly affecting payment amounts.'),
        ('provider_zip_code', 'Text (5 or 9 digits)',
         'ZIP or ZIP+4 code',
         'Provider ZIP code. Used for geographic granularity beyond state level. '
         'CMS uses ZIP codes to determine geographic pricing adjustments (locality codes). '
         'Rural ZIP codes often indicate underserved areas with fewer provider choices.'),
        ('provider_country', 'Text (2-letter code)',
         'Mostly "US"',
         'Country code. Almost exclusively "US" for domestic providers. '
         'A small number may show non-US territories.'),
    ], headers=('Column Name', 'Data Type', 'Values', 'Detailed Description'))

    h(doc, 'Service & Procedure Information', level=2)
    add_stats_table(doc, [
        ('provider_specialty', 'Text',
         f'{n_specialties} unique specialties',
         'The provider\'s primary medical specialty as recognized by Medicare (e.g., '
         '"Internal Medicine", "Diagnostic Radiology", "Orthopedic Surgery"). This is '
         'one of the most important fields — it determines prior authorization rules, '
         'expected payment ranges, and procedure eligibility. Different specialties have '
         'dramatically different billing patterns and reimbursement rates.'),
        ('medicare_participating', 'Character (Y/N)',
         'Y = Participating, N = Non-participating',
         'Whether the provider accepts Medicare\'s approved amount as full payment. '
         'PARTICIPATING (Y): Accepts Medicare Allowed Amount as payment in full. Patient pays '
         'only the 20% coinsurance. NON-PARTICIPATING (N): May charge up to 15% above the '
         'Medicare fee schedule (the "limiting charge"). Patients may owe more out-of-pocket.'),
        ('place_of_service', 'Character (F/O)',
         'F = Facility, O = Office',
         'Where the service was performed. FACILITY (F): Hospital, ambulatory surgery center, '
         'skilled nursing facility, or similar institutional setting. Facility fees apply. '
         'OFFICE (O): Provider\'s private office or clinic. Generally lower cost. The same '
         'procedure code can have different payment rates depending on place of service.'),
        ('procedure_code', 'Text (5 characters)',
         f'{n_procedures:,} unique HCPCS/CPT codes',
         'Healthcare Common Procedure Coding System (HCPCS) code. This is the standardized '
         'code that describes the specific medical service or procedure performed. Examples: '
         '99213 = Office visit (15 min), 99214 = Office visit (25 min), 99232 = Hospital visit. '
         'Correct coding is critical — incorrect codes are the #1 cause of claim denials.'),
        ('procedure_description', 'Text',
         'Plain-English description of the HCPCS code',
         'Human-readable description of what the procedure code represents. '
         'Example: Code 99213 = "Office/outpatient visit est". These descriptions help '
         'billing staff verify that the correct code was selected.'),
        ('is_drug_service', 'Character (Y/N)',
         'Y = Drug-related, N = Non-drug',
         'Whether this service involves a drug or biologic administered by the provider. '
         'Drug services (Y) include infused medications, injections, and chemotherapy drugs '
         'billed under Medicare Part B. Non-drug services (N) include office visits, surgeries, '
         'imaging, and lab tests. Drug services have different authorization workflows.'),
    ], headers=('Column Name', 'Data Type', 'Values', 'Detailed Description'))

    h(doc, 'Utilization Metrics', level=2)
    add_stats_table(doc, [
        ('total_services', 'Integer',
         f'Mean: {avg_services:,.1f}, Median: {med_services:,.1f}',
         'Total number of times this provider performed this specific procedure. '
         'A provider who sees 100 patients for the same procedure will have total_services ≥ 100. '
         'High service counts indicate high-volume providers who are most affected by '
         'policy changes or prior authorization requirements for that procedure.'),
        ('total_patients', 'Integer',
         f'Mean: {avg_patients:,.1f}, Median: {med_patients:,.1f}',
         'Number of unique Medicare beneficiaries who received this procedure from this provider. '
         'If total_services > total_patients, it means some patients received the procedure '
         'multiple times (recurring treatments like dialysis or physical therapy).'),
        ('total_patient_day_services', 'Integer',
         'Number of distinct service dates',
         'Total number of distinct calendar days on which services were provided. '
         'This helps distinguish between a provider who sees many patients on one day '
         'vs. one who sees fewer patients across many days. Important for scheduling analysis.'),
    ], headers=('Column Name', 'Data Type', 'Values', 'Detailed Description'))

    h(doc, 'Financial Metrics (Payment Fields)', level=2)
    p(doc, 'These are the 4 core payment columns. See Section 1.5 for the "Who Pays What" breakdown.', italic=True)
    add_stats_table(doc, [
        ('avg_submitted_charge', 'Decimal ($)',
         f'Mean: ${avg_charge:,.2f}, Median: ${med_charge:,.2f}',
         'PROVIDER SETS THIS. The average amount the provider charges per service. '
         'This is the provider\'s "sticker price" or billed amount. Medicare almost never '
         'pays this full amount — it is typically 2-5x higher than what Medicare actually pays. '
         'Providers set charges based on their internal cost structure and commercial insurance '
         'rates, not Medicare fee schedules. The gap between this and actual payment is the '
         'provider\'s write-off.'),
        ('avg_medicare_allowed_amount', 'Decimal ($)',
         f'Mean: ${avg_allowed:,.2f}',
         'MEDICARE SETS THIS. The maximum amount Medicare approves for this service. '
         'This is determined by the Medicare Physician Fee Schedule (MPFS), which is updated '
         'annually. The allowed amount = (Work RVU + Practice Expense RVU + Malpractice RVU) '
         '× Geographic Practice Cost Index (GPCI) × Conversion Factor. '
         'This is the ceiling — for participating providers, total payment (Medicare + patient) '
         'cannot exceed this amount.'),
        ('avg_medicare_payment', 'Decimal ($)',
         f'Mean: ${avg_pay:,.2f}, Median: ${med_pay:,.2f}',
         'MEDICARE PAYS THIS TO THE PROVIDER. The actual dollar amount Medicare sends to the '
         'provider. Typically 80% of the Allowed Amount (Medicare covers 80%, patient covers '
         '20% coinsurance). This is the provider\'s primary revenue from Medicare patients. '
         'For CareFlow AI, this is the most important field — it represents real money the '
         'provider receives.'),
        ('avg_medicare_standardized_amount', 'Decimal ($)',
         f'Mean: ${avg_std:,.2f}',
         'MEDICARE CALCULATES THIS. Same as Medicare Payment but with geographic cost '
         'adjustments (GPCI) removed. A provider in New York and a provider in rural Alabama '
         'performing the same procedure would have different avg_medicare_payment amounts '
         '(due to cost of living), but similar standardized amounts. Used for fair cross-state '
         'comparisons and national trend analysis.'),
    ], headers=('Column Name', 'Data Type', 'Values', 'Detailed Description'))

    h(doc, 'How to Read Each Row', level=2)
    p(doc, 'Example Row Interpretation:', bold=True)
    p(doc, 'If a row shows: NPI 1234567890, Specialty "Internal Medicine", Procedure 99213 '
           '("Office/outpatient visit est"), Total Services = 500, Total Patients = 400, '
           'Avg Charge = $120, Avg Allowed = $75, Avg Payment = $60, Avg Standardized = $58')
    p(doc, 'This means:', bold=True)
    doc.add_paragraph('Provider 1234567890 is an Internal Medicine doctor', style='List Bullet')
    doc.add_paragraph('They billed procedure 99213 (a standard 15-minute office visit) 500 times', style='List Bullet')
    doc.add_paragraph('Those 500 services were for 400 unique patients (some patients had repeat visits)', style='List Bullet')
    doc.add_paragraph('They charged an average of $120 per visit (their sticker price)', style='List Bullet')
    doc.add_paragraph('Medicare approved $75 as the maximum for this service', style='List Bullet')
    doc.add_paragraph('Medicare paid $60 (80% of $75) directly to the provider', style='List Bullet')
    doc.add_paragraph('The patient owes approximately $15 in coinsurance (20% of $75)', style='List Bullet')
    doc.add_paragraph('The provider writes off $45 ($120 charged - $75 allowed = lost revenue)', style='List Bullet')
    doc.add_paragraph('The standardized amount ($58) is the geography-adjusted version for fair national comparisons', style='List Bullet')
    doc.add_page_break()

    # ── 2. PROVIDER SPECIALTY ANALYSIS ──
    h(doc, '2. Provider Specialty Analysis')
    img(doc, os.path.join(cd, '01_specialty_bar.png'), cap='Figure 1: Top 20 Provider Specialties')
    top_spec = df['provider_specialty'].value_counts().head(5)
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, f'This horizontal bar chart ranks the 20 most common medical specialties in the dataset by number of records. '
           f'The top specialty is "{top_spec.index[0]}" with {top_spec.values[0]:,} records '
           f'({top_spec.values[0]/n*100:.1f}% of all records). The top 5 specialties account for '
           f'{top_spec.sum()/n*100:.1f}% of the dataset, while there are {n_specialties} total specialties — '
           f'meaning most specialties have very few records.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, f'The extreme concentration in a few specialties creates two problems: (1) Prior authorization rules '
           f'and denial patterns differ dramatically by specialty, so a one-size-fits-all AI model will fail. '
           f'CareFlow AI must build specialty-specific models. (2) Rare specialties with few records will lack '
           f'sufficient training data for accurate prediction, creating blind spots in the system.')

    p(doc, 'Provider Credentials:', bold=True)
    img(doc, os.path.join(cd, '16_credentials.png'), cap='Figure 2: Top 15 Provider Credentials')
    creds = df['provider_credentials'].dropna().value_counts().head(3)
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, f'This chart shows the distribution of professional credentials among providers. '
           f'The most common credential is "{creds.index[0]}" ({creds.values[0]:,} records), '
           f'followed by "{creds.index[1]}" and "{creds.index[2]}". This reflects the '
           f'predominance of physicians (M.D./D.O.) in Medicare billing.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'Different credential types (M.D., D.O., NP, PA) have different scope-of-practice rules '
           'and prior authorization requirements. Nurse practitioners and physician assistants may face '
           'additional authorization hurdles for procedures that physicians can perform without prior auth. '
           'CareFlow AI must factor in credential type when predicting authorization requirements.')
    doc.add_page_break()

    # ── 3. GEOGRAPHIC DISTRIBUTION ──
    h(doc, '3. Geographic Distribution')
    img(doc, os.path.join(cd, '02_state_bar.png'), cap='Figure 3: Top 20 States by Records')
    p(doc, 'What This Chart Shows:', bold=True)
    top_st = df['provider_state'].value_counts().head(5)
    p(doc, f'This chart ranks states by total number of Medicare provider-service records. '
           f'The top 5 states ({", ".join(top_st.index)}) account for '
           f'{top_st.sum()/n*100:.1f}% of all records. Population-heavy states dominate.')

    img(doc, os.path.join(cd, '27_unique_providers_state.png'), cap='Figure 4: Top 20 States by Unique Providers')
    p(doc, 'What This Chart Shows:', bold=True)
    provs_top5 = df[df['provider_state'].isin(top_st.index)]['provider_npi'].nunique()
    provs_total = df['provider_npi'].nunique()
    p(doc, f'This chart shows unique provider count (NPI) per state. The top 5 states hold '
           f'{provs_top5:,} of {provs_total:,} unique providers ({provs_top5/provs_total*100:.1f}%). '
           f'This confirms the geographic concentration is not just about billing volume — '
           f'the actual number of healthcare professionals is heavily skewed.')

    img(doc, os.path.join(cd, '15_top_cities.png'), cap='Figure 5: Top 20 Cities')
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, 'This chart drills down to the city level. Major metropolitan areas (New York, Houston, '
           'Chicago, Los Angeles, Philadelphia) dominate, reflecting urban concentration of healthcare providers.')

    p(doc, 'Problem Identified:', bold=True)
    p(doc, f'Geographic concentration creates severe access disparities. While urban areas have an abundance of '
           f'providers, rural states and small towns face critical shortages. Patients in underserved areas '
           f'experience longer wait times, fewer specialist options, and must travel further for care. '
           f'This directly impacts no-show rates, delayed diagnoses, and patient outcomes. '
           f'CareFlow AI should flag patients in underserved ZIP codes for proactive scheduling support '
           f'and recommend telehealth alternatives when in-person access is limited.')

    img(doc, os.path.join(cd, '25_payment_by_state.png'), cap='Figure 6: Average Payment by State')
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, 'This chart shows average Medicare payment by state. Higher payments in certain states '
           'reflect higher cost of living, geographic practice cost indices (GPCI), and specialty mix. '
           'States with expensive real estate and higher wages naturally have higher Medicare fee schedules.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'State-level payment variation means a provider performing the same procedure in two different '
           'states will receive different reimbursement. CareFlow AI must use location-adjusted predictions '
           'rather than national averages when estimating expected payments.')
    doc.add_page_break()

    # ── 4. PAYMENT ANALYSIS ──
    h(doc, '4. Payment Analysis')
    h(doc, '4.1 Charges vs Payments', level=2)
    img(doc, os.path.join(cd, '03_payment_vs_charge.png'), cap='Figure 7: Charges vs Payments by Specialty')
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, f'This grouped bar chart compares what providers charge (blue) versus what Medicare pays (green) '
           f'for the top 15 most expensive specialties. On average, providers submit ${avg_charge:,.2f} but '
           f'receive only ${avg_pay:,.2f} — a {gap_pct:.1f}% reduction. The Medicare Allowed Amount averages '
           f'${avg_allowed:,.2f}, and the Standardized Amount (geography-adjusted) averages ${avg_std:,.2f}.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'The massive gap between submitted charges and actual payments is the #1 revenue cycle problem. '
           'Providers who set charges based on internal cost structures receive far less than expected. '
           'This creates cash flow unpredictability, inflated patient bills, and administrative burden '
           'from write-offs. CareFlow AI must provide real-time expected payment estimates so billing '
           'staff can set realistic revenue expectations before claims are submitted.')

    h(doc, '4.2 Revenue Gap by State', level=2)
    img(doc, os.path.join(cd, '04_payment_gap_state.png'), cap='Figure 8: Charge-to-Payment Gap by State')
    p(doc, 'What This Chart Shows:', bold=True)
    g = df.groupby('provider_state').agg(ch=('avg_submitted_charge','mean'), pa=('avg_medicare_payment','mean'))
    g['gap'] = g['ch'] - g['pa']
    worst = g.sort_values('gap', ascending=False).head(3)
    p(doc, f'This chart ranks states by the average dollar gap between submitted charges and Medicare payments. '
           f'The largest gap is in {worst.index[0]} (${worst["gap"].values[0]:,.2f}), followed by '
           f'{worst.index[1]} (${worst["gap"].values[1]:,.2f}) and {worst.index[2]} (${worst["gap"].values[2]:,.2f}).')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'States with larger gaps face greater revenue unpredictability. Providers in high-gap states '
           'are likely submitting charges based on commercial insurance rates, which are much higher than '
           'Medicare fee schedules. This leads to large write-offs, accounts receivable buildup, and '
           'potential patient balance billing. CareFlow AI should provide state-specific reimbursement '
           'benchmarks and alert billing staff when charges are significantly above expected payment.')

    h(doc, '4.3 Payment Distribution', level=2)
    img(doc, os.path.join(cd, '05_payment_hist.png'), cap='Figure 9: Medicare Payment Distribution')
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, f'This histogram shows how Medicare payments are distributed across all {n:,} records. '
           f'The dashed lines show the median (${med_pay:,.2f}) and mean (${avg_pay:,.2f}). '
           f'The distribution is heavily right-skewed — most services receive relatively low payments, '
           f'while a small tail of high-value procedures pulls the mean above the median.')

    img(doc, os.path.join(cd, '24_charge_hist.png'), cap='Figure 10: Submitted Charge Distribution')
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, f'This histogram shows submitted charges. The median charge (${med_charge:,.2f}) is much '
           f'lower than the mean (${avg_charge:,.2f}), showing even more extreme skewness than payments.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'The skewed distributions mean most services are low-value routine care, but a small number '
           'of high-value claims drive disproportionate revenue. If even a few of these high-value claims '
           'are denied, the financial impact is severe. CareFlow AI should implement a priority queue '
           'that gives extra scrutiny to high-dollar claims before submission.')

    h(doc, '4.4 Payment Efficiency', level=2)
    img(doc, os.path.join(cd, '20_payment_efficiency.png'), cap='Figure 11: Payment Efficiency by Specialty')
    p(doc, 'What This Chart Shows:', bold=True)
    eff = df.groupby('provider_specialty').agg(
        ch=('avg_submitted_charge','mean'), pa=('avg_medicare_payment','mean'))
    eff['pct'] = (eff['pa'] / eff['ch'] * 100).round(1)
    worst_eff = eff.sort_values('pct').head(3)
    p(doc, f'Payment efficiency measures what percentage of the submitted charge Medicare actually pays. '
           f'The bottom 20 specialties are shown. The worst efficiency is {worst_eff.index[0]} at '
           f'{worst_eff["pct"].values[0]:.1f}%, meaning Medicare pays less than a quarter of what is charged.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'Specialties with very low payment efficiency (below 30%) face the most severe revenue shortfalls. '
           'Providers in these specialties may not realize how little Medicare will reimburse until after '
           'services are rendered. CareFlow AI should provide specialty-specific fee schedule lookups '
           'and warn providers when their charges significantly exceed expected reimbursement, '
           'preventing surprise revenue shortfalls.')

    h(doc, '4.5 Payment by Specialty (Box Plot)', level=2)
    img(doc, os.path.join(cd, '19_boxplot_specialty.png'), cap='Figure 12: Payment Distribution by Top Specialties')
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, 'This box plot shows the payment distribution within each of the top 8 specialties. '
           'The box represents the interquartile range (25th-75th percentile), the line is the median, '
           'and whiskers extend to 1.5x the IQR. This reveals how predictable or variable payments '
           'are within each specialty.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'Specialties with wide payment spreads (tall boxes and long whiskers) have unpredictable '
           'reimbursement. Revenue forecasting is difficult for these specialties. Specialties with '
           'narrow boxes have more predictable payments, making financial planning easier. '
           'CareFlow AI should factor in specialty-level payment variance when generating '
           'revenue forecasts and confidence intervals.')
    doc.add_page_break()

    # ── 5. PAYMENT BREAKDOWNS ──
    h(doc, '5. Payment Breakdowns')
    h(doc, '5.1 By Gender', level=2)
    img(doc, os.path.join(cd, '08_gender_pie.png'), w=Inches(4), cap='Figure 13: Gender Distribution')
    img(doc, os.path.join(cd, '10_payment_by_gender.png'), cap='Figure 14: Payment by Gender')
    p(doc, 'What These Charts Show:', bold=True)
    gp = df.groupby('provider_gender')['avg_medicare_payment'].mean()
    gm = df.groupby('provider_gender')['avg_medicare_payment'].median()
    if 'M' in gp.index and 'F' in gp.index:
        diff = abs(gp['M'] - gp['F'])
        higher = 'Male' if gp['M'] > gp['F'] else 'Female'
        lower = 'Female' if higher == 'Male' else 'Male'
        p(doc, f'The pie chart shows gender distribution of providers. The bar chart compares mean and '
               f'median Medicare payments by gender. {higher} providers have a higher average payment '
               f'by ${diff:,.2f} (Male: ${gp["M"]:,.2f} vs Female: ${gp["F"]:,.2f}).')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'The gender payment gap does not necessarily indicate discrimination — it more likely '
           'reflects the uneven distribution of specialties between genders. Male providers are '
           'overrepresented in higher-paying surgical specialties, while female providers are '
           'more concentrated in primary care and pediatrics. CareFlow AI should control for '
           'specialty when analyzing payment equity to avoid misleading conclusions.')

    h(doc, '5.2 By Entity Type', level=2)
    img(doc, os.path.join(cd, '09_entity_pie.png'), w=Inches(4), cap='Figure 15: Entity Type Distribution')
    img(doc, os.path.join(cd, '11_payment_by_entity.png'), cap='Figure 16: Payment by Entity Type')
    p(doc, 'What These Charts Show:', bold=True)
    ep = df.groupby('provider_entity_type')['avg_medicare_payment'].mean()
    if 'I' in ep.index and 'O' in ep.index:
        p(doc, f'The pie chart shows individual vs organizational providers. Organizations average '
               f'${ep["O"]:,.2f} per service vs individuals at ${ep["I"]:,.2f}. '
               f'Organizations include hospitals, clinics, labs, and imaging centers.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'Organizations typically perform higher-cost procedures (surgeries, imaging, dialysis) and '
           'have different billing patterns than individual providers. They also face different prior '
           'authorization rules and are more likely to submit facility fees on top of professional fees. '
           'CareFlow AI must distinguish between individual and organizational billing patterns '
           'when predicting claim outcomes and expected payments.')

    h(doc, '5.3 By Place of Service', level=2)
    img(doc, os.path.join(cd, '12_place_of_service.png'), w=Inches(4), cap='Figure 17: Place of Service')
    img(doc, os.path.join(cd, '14_payment_by_place.png'), cap='Figure 18: Payment by Place of Service')
    p(doc, 'What These Charts Show:', bold=True)
    pp = df.groupby('place_of_service')['avg_medicare_payment'].mean()
    pos = df['place_of_service'].dropna().value_counts()
    if 'F' in pp.index and 'O' in pp.index:
        p(doc, f'The pie chart shows the split between facility and office settings. '
               f'Facility-based services average ${pp["F"]:,.2f} vs office-based at ${pp["O"]:,.2f}. '
               f'Facility services account for {pos.get("F",0)/pos.sum()*100:.1f}% of records.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'The same procedure performed in a facility vs an office can result in dramatically different '
           'reimbursement. Facility fees add significant cost. Patients are often unaware that the same '
           'procedure costs much more at a hospital than in a doctor\'s office. CareFlow AI should flag '
           'place-of-service as a key variable in cost estimates and recommend office-based alternatives '
           'when clinically appropriate to reduce patient costs.')

    h(doc, '5.4 Medicare Participation', level=2)
    img(doc, os.path.join(cd, '23_medicare_participation.png'), w=Inches(4), cap='Figure 19: Medicare Participation')
    p(doc, 'What This Chart Shows:', bold=True)
    mp = df['medicare_participating'].dropna().value_counts()
    if 'Y' in mp.index:
        pct = mp['Y'] / mp.sum() * 100
        p(doc, f'{pct:.1f}% of provider records are from Medicare-participating providers. '
               f'Participating providers accept Medicare\'s approved amount as full payment. '
               f'Non-participating providers can charge up to 15% above the Medicare fee schedule.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'Non-participating providers create cost uncertainty for patients. They may charge more '
           'than the Medicare-approved amount, leaving patients responsible for the excess ("balance billing"). '
           'CareFlow AI should flag non-participating providers in the scheduling module and warn patients '
           'about potential higher out-of-pocket costs before appointments are booked.')
    doc.add_page_break()

    # ── 6. SERVICE & UTILIZATION ──
    h(doc, '6. Service & Utilization Analysis')
    h(doc, '6.1 Drug vs Non-Drug Services', level=2)
    img(doc, os.path.join(cd, '13_drug_vs_nondrug.png'), w=Inches(4), cap='Figure 20: Drug vs Non-Drug')
    p(doc, 'What This Chart Shows:', bold=True)
    dr = df['is_drug_service'].dropna().value_counts()
    if 'Y' in dr.index:
        p(doc, f'This pie chart splits services into drug-related ({dr["Y"]/dr.sum()*100:.1f}%) and '
               f'non-drug ({dr.get("N",0)/dr.sum()*100:.1f}%) categories. Drug services include '
               f'administered medications, infusions, and injections billed under Part B.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'Drug services have fundamentally different authorization requirements than non-drug services. '
           'Many high-cost specialty drugs (biologics, chemotherapy, immunotherapy) require prior authorization '
           'with clinical documentation. Drug prices also fluctuate more than procedure fees, making cost '
           'prediction harder. CareFlow AI must maintain separate authorization workflows for drug vs '
           'non-drug services and track drug price changes in real time.')

    h(doc, '6.2 Top Procedures', level=2)
    img(doc, os.path.join(cd, '07_top_procedures.png'), cap='Figure 21: Top 20 Most Common Procedures')
    p(doc, 'What This Chart Shows:', bold=True)
    top_proc = df.groupby(['procedure_code','procedure_description']).agg(
        total=('total_services','sum')).sort_values('total', ascending=False).head(3).reset_index()
    p(doc, f'This chart ranks the 20 most frequently billed HCPCS/CPT codes by total service volume. '
           f'The most common is {top_proc["procedure_code"].iloc[0]} — '
           f'"{top_proc["procedure_description"].iloc[0]}" with {top_proc["total"].iloc[0]:,.0f} total services. '
           f'Office visits and evaluation/management (E&M) codes dominate, as expected in outpatient Medicare.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'High-volume procedures are the most likely targets for payer audits, prior authorization '
           'requirements, and coding reviews. A single policy change affecting a top-20 procedure '
           'could impact thousands of claims. CareFlow AI should monitor payer policy updates for '
           'these high-volume codes and pre-populate authorization forms with commonly required documentation.')

    h(doc, '6.3 Highest-Paying Procedures', level=2)
    img(doc, os.path.join(cd, '17_highest_paying_procs.png'), cap='Figure 22: Highest-Paying Procedures')
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, 'This chart shows the 20 procedures with the highest average Medicare payment (minimum 1,000 '
           'services to ensure statistical significance). These are typically surgical procedures, '
           'complex imaging, and specialty treatments that command premium reimbursement.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'High-paying procedures carry the most financial risk per denial. A single denied claim for '
           'a procedure that pays thousands of dollars has a far greater impact than denying a routine '
           'office visit. These claims need the most rigorous pre-submission review. CareFlow AI should '
           'flag all claims above a configurable dollar threshold for mandatory human review before filing.')

    h(doc, '6.4 Lowest-Paying Procedures', level=2)
    img(doc, os.path.join(cd, '18_lowest_paying_procs.png'), cap='Figure 23: Lowest-Paying Procedures')
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, 'This chart shows the 20 procedures with the lowest average Medicare payment (minimum 1,000 '
           'services). These are simple office visits, brief evaluations, and routine tests.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'While individual low-paying procedures seem harmless, their sheer volume creates cumulative '
           'revenue risk. If a payer denies a large batch of routine claims due to a documentation '
           'deficiency or coding error, the total financial impact can be significant. CareFlow AI '
           'should batch-validate high-volume low-value claims before submission to catch systematic errors.')

    h(doc, '6.5 Utilization: Patients vs Services', level=2)
    img(doc, os.path.join(cd, '06_scatter_utilization.png'), cap='Figure 24: Patients vs Services Scatter')
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, 'This scatter plot shows the relationship between patient count and service count per '
           'provider-procedure combination. Color intensity represents average payment amount. '
           'Most providers cluster in the lower-left (few patients, few services), while a few '
           'high-volume providers serve hundreds of patients. Darker dots indicate higher-paying services.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'High-volume providers (upper-right) face the greatest prior authorization burden. '
           'If a provider performs the same procedure on hundreds of patients, a single prior auth '
           'policy change could affect all of them simultaneously. CareFlow AI should batch similar '
           'authorization requests for high-volume providers and proactively alert staff to policy '
           'changes that affect their most common procedures.')

    h(doc, '6.6 Services per Patient by Specialty', level=2)
    img(doc, os.path.join(cd, '21_services_per_patient.png'), cap='Figure 25: Services-per-Patient Ratio')
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, 'This chart ranks specialties by how many services each patient receives on average. '
           'High ratios indicate specialties where patients need repeated treatments (dialysis, '
           'radiation therapy, physical therapy). Low ratios indicate one-time consultations.')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'Specialties with high services-per-patient ratios generate the most recurring prior '
           'authorization requests. Getting initial authorization once is not enough — these '
           'specialties need ongoing re-authorization. CareFlow AI should implement auto-renewal '
           'workflows for recurring treatment plans and predict when re-authorization is needed '
           'based on treatment frequency patterns.')

    h(doc, '6.7 Revenue Gap by Specialty', level=2)
    img(doc, os.path.join(cd, '26_revenue_gap_specialty.png'), cap='Figure 26: Revenue Gap by Specialty')
    p(doc, 'What This Chart Shows:', bold=True)
    gap_spec = df.groupby('provider_specialty').agg(
        ch=('avg_submitted_charge', 'mean'), pa=('avg_medicare_payment', 'mean'))
    gap_spec['gap'] = gap_spec['ch'] - gap_spec['pa']
    gap_spec['eff'] = (gap_spec['pa'] / gap_spec['ch'] * 100).round(1)
    worst_spec = gap_spec.sort_values('gap', ascending=False).head(3)
    p(doc, 'This overlay chart directly compares average charges vs payments for the 20 specialties '
           'with the largest dollar gaps. The blue bars show charges, green bars show payments — '
           'the visible gap between them represents unrealized revenue.')
    p(doc, 'Top 3 specialties by revenue gap:', bold=True)
    for sp, row in worst_spec.iterrows():
        doc.add_paragraph(f'{sp}: Gap ${row["gap"]:,.0f} (pays {row["eff"]:.1f}% of charges)', style='List Bullet')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'These specialties face the most severe disconnect between what they charge and what they '
           'receive. Providers in these specialties need the most help understanding Medicare fee '
           'schedules. CareFlow AI should provide specialty-specific dashboards showing expected '
           'reimbursement rates and recommend charge adjustments to minimize write-offs.')
    doc.add_page_break()

    # ── 7. CORRELATIONS ──
    h(doc, '7. Correlation Analysis')
    img(doc, os.path.join(cd, '22_correlation_heatmap.png'), w=Inches(5.5), cap='Figure 27: Correlation Matrix')
    p(doc, 'What This Chart Shows:', bold=True)
    p(doc, 'This heatmap shows the Pearson correlation coefficient between all numeric variables in the '
           'dataset. Values range from -1 (perfect negative correlation) to +1 (perfect positive correlation). '
           'Red indicates positive correlation, blue indicates negative correlation.')
    p(doc, 'Key correlations:', bold=True)
    doc.add_paragraph('Submitted charges and Medicare payments are strongly correlated — higher charges generally yield higher payments, but the relationship is not 1:1. This means charges DO influence payment but not proportionally.', style='List Bullet')
    doc.add_paragraph('Total patients and total services are very highly correlated, confirming that more patients = more services in a roughly linear relationship.', style='List Bullet')
    doc.add_paragraph('The standardized amount correlates strongly with actual payment but removes geographic variation, making it useful for fair cross-state comparisons.', style='List Bullet')
    doc.add_paragraph('Medicare allowed amount and actual payment are nearly identical, confirming that Medicare pays close to what it approves.', style='List Bullet')
    p(doc, 'Problem Identified:', bold=True)
    p(doc, 'The imperfect correlation between charges and payments (not 1.0) means that simply '
           'raising charges does NOT proportionally increase Medicare reimbursement. Many providers '
           'mistakenly believe higher charges will yield higher payments. CareFlow AI should educate '
           'users that Medicare payment is based on fee schedules, not submitted charges, and that '
           'inflating charges only increases the write-off burden.')
    doc.add_page_break()

    # ── 8. COMPREHENSIVE STATISTICS ──
    h(doc, '8. Comprehensive Statistics')

    h(doc, '8.1 Descriptive Statistics (All Numeric Columns)', level=2)
    p(doc, 'Full statistical breakdown of every numeric variable in the dataset:')
    numeric_cols = ['total_patients', 'total_services', 'total_patient_day_services',
                    'avg_submitted_charge', 'avg_medicare_allowed_amount',
                    'avg_medicare_payment', 'avg_medicare_standardized_amount']
    desc = df[numeric_cols].describe().round(2)
    short_names = ['Patients', 'Services', 'Pt-Days', 'Charge', 'Allowed', 'Payment', 'Standardized']
    add_stats_table(doc, [
        (stat,) + tuple(f'{desc.loc[stat, col]:,.2f}' if stat != 'count' else f'{desc.loc[stat, col]:,.0f}'
                        for col in numeric_cols)
        for stat in desc.index
    ], headers=('Statistic',) + tuple(short_names))

    h(doc, '8.2 Data Quality — Missing Values', level=2)
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0].sort_values(ascending=False)
    if len(missing_cols) > 0:
        p(doc, f'{len(missing_cols)} columns have missing values:')
        add_stats_table(doc, [
            (col, f'{missing_cols[col]:,}', f'{missing_cols[col]/n*100:.1f}%')
            for col in missing_cols.index
        ], headers=('Column', 'Missing Count', 'Missing %'))
    else:
        p(doc, 'No missing values detected. Data quality is excellent.')

    h(doc, '8.3 Payment Statistics by Specialty (Top 25)', level=2)
    p(doc, 'Column labels: Provider Charge = what the provider bills. Medicare Pays = what Medicare sends to the provider. '
           'Patient Pays = estimated patient coinsurance (Allowed − Medicare Payment). Write-Off = charge that is never collected.', italic=True)
    spec_stats = df.groupby('provider_specialty').agg(
        count=('provider_npi','count'),
        providers=('provider_npi','nunique'),
        avg_charge=('avg_submitted_charge','mean'),
        avg_allowed=('avg_medicare_allowed_amount','mean'),
        avg_payment=('avg_medicare_payment','mean'),
        med_payment=('avg_medicare_payment','median'),
        avg_patients=('total_patients','mean'),
    ).sort_values('count', ascending=False).head(25)
    spec_stats['patient_pays'] = spec_stats['avg_allowed'] - spec_stats['avg_payment']
    spec_stats['write_off'] = spec_stats['avg_charge'] - spec_stats['avg_allowed']
    spec_stats['efficiency'] = (spec_stats['avg_payment'] / spec_stats['avg_charge'] * 100).round(1)

    add_stats_table(doc, [
        (sp, f'{row["count"]:,}',
         f'${row["avg_charge"]:,.0f}', f'${row["avg_payment"]:,.0f}',
         f'${row["patient_pays"]:,.0f}', f'${row["write_off"]:,.0f}',
         f'{row["efficiency"]}%')
        for sp, row in spec_stats.iterrows()
    ], headers=('Specialty', 'Records',
                'Provider Charges', 'Medicare Pays',
                'Patient Pays (est)', 'Write-Off',
                'Eff%'))

    h(doc, '8.4 Payment Statistics by State (All States)', level=2)
    p(doc, 'Same column definitions as above. Efficiency = Medicare Payment / Provider Charge %.', italic=True)
    state_stats = df.groupby('provider_state').agg(
        count=('provider_npi','count'),
        providers=('provider_npi','nunique'),
        specialties=('provider_specialty','nunique'),
        avg_charge=('avg_submitted_charge','mean'),
        avg_allowed=('avg_medicare_allowed_amount','mean'),
        avg_payment=('avg_medicare_payment','mean'),
    ).sort_values('count', ascending=False)
    state_stats['patient_pays'] = state_stats['avg_allowed'] - state_stats['avg_payment']
    state_stats['write_off'] = state_stats['avg_charge'] - state_stats['avg_allowed']
    state_stats['efficiency'] = (state_stats['avg_payment'] / state_stats['avg_charge'] * 100).round(1)

    add_stats_table(doc, [
        (st, f'{row["count"]:,}', f'{row["providers"]:,}',
         f'${row["avg_charge"]:,.0f}', f'${row["avg_payment"]:,.0f}',
         f'${row["patient_pays"]:,.0f}', f'${row["write_off"]:,.0f}',
         f'{row["efficiency"]}%')
        for st, row in state_stats.iterrows()
    ], headers=('State', 'Records', 'Providers',
                'Provider Charges', 'Medicare Pays',
                'Patient Pays (est)', 'Write-Off',
                'Eff%'))
    doc.add_page_break()

    # ── 9. KEY PROBLEMS ──
    h(doc, '9. Key Problems Identified')
    problems = [
        ('Revenue Leakage', f'Providers lose an average of ${avg_gap:,.2f} ({gap_pct:.1f}%) per service between what they charge and what Medicare pays. Across {n:,} records, this represents massive unrealized revenue.'),
        ('Prior Auth Complexity', f'{n_procedures:,} procedures across {n_specialties} specialties create an enormous matrix of payer-specific authorization rules that are impossible to manage manually.'),
        ('Geographic Disparities', f'The top 5 states hold {top_st.sum()/n*100:.1f}% of records. Rural and underserved areas have critical provider shortages.'),
        ('Payment Unpredictability', f'The gap between mean (${avg_pay:,.2f}) and median (${med_pay:,.2f}) payment shows extreme skewness. Revenue forecasting without data tools is unreliable.'),
        ('High-Value Claim Risk', f'A small number of procedures command payments over ${max_pay:,.0f}. Denials on these claims cause severe financial harm.'),
        ('Cost Transparency Gap', f'Submitted charges (${avg_charge:,.2f}) bear little resemblance to actual payments (${avg_pay:,.2f}), creating patient confusion and surprise bills.'),
        ('Specialty Payment Inequality', 'Payment efficiency varies dramatically — some specialties receive less than 20% of submitted charges while others receive over 60%.'),
        ('Coding Complexity', f'With {n_procedures:,} unique HCPCS codes, incorrect coding is a leading cause of claim denials. AI-assisted coding review is essential.'),
    ]
    for i, (title, desc) in enumerate(problems, 1):
        h(doc, f'{i}. {title}', level=2)
        p(doc, desc)
    doc.add_page_break()

    # ── 10. RECOMMENDATIONS ──
    h(doc, '10. Recommendations for CareFlow AI')
    recs = [
        ('Real-Time Reimbursement Predictor', 'Use CMS data to predict actual payment for any provider/procedure/state combination before claim submission.'),
        ('Denial Risk Scoring Engine', 'Assign risk scores to claims based on procedure code, specialty, state, and historical patterns.'),
        ('Specialty-Specific Prior Auth Automation', 'Pre-populate authorization forms for the top 20 highest-volume procedures.'),
        ('High-Value Claim Priority Queue', 'Flag claims in the top 5% by expected value for mandatory manual review.'),
        ('Geographic Access Dashboard', 'Map provider availability to identify underserved areas for telehealth intervention.'),
        ('Charge Optimization Alerts', 'Alert billing staff when submitted charges deviate significantly from expected Medicare rates.'),
        ('Payment Trend Monitoring', 'Track payment efficiency over time by specialty and state to identify deteriorating reimbursement.'),
        ('Patient Cost Estimator', 'Show patients expected out-of-pocket costs using actual Medicare payment data instead of submitted charges.'),
    ]
    for i, (title, desc) in enumerate(recs, 1):
        h(doc, f'{i}. {title}', level=2)
        p(doc, desc)
    doc.add_page_break()

    # ── CONCLUSION ──
    h(doc, '11. Conclusion')
    p(doc, f'This expanded analysis of {n:,} Medicare records reveals systemic challenges in '
           f'healthcare revenue cycle management. The {gap_pct:.1f}% charge-to-payment gap, '
           f'combined with {n_procedures:,} procedure codes and {n_specialties} specialties, '
           f'creates complexity that demands AI-driven solutions. CareFlow AI is positioned to '
           f'transform these challenges into operational improvements.')
    doc.add_paragraph()
    p(doc, 'Disclaimer: This report uses public CMS data for demonstration only. '
           'No real patient data is included.', sz=9, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    doc.save(out)
    log(f"Report saved: {out}")


# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 60)
    log("CareFlow AI — Expanded Report Generator")
    log("=" * 60)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(CHARTS_DIR, exist_ok=True)

    engine = create_engine(DATABASE_URL, echo=False)
    df = load_data(engine)

    log("Generating 29 charts...")
    chart_funcs = [
        c01_specialty_bar, c02_state_bar, c03_payment_vs_charge, c04_payment_gap_state,
        c05_payment_hist, c06_scatter_utilization, c07_top_procedures, c08_gender_pie,
        c09_entity_pie, c10_payment_by_gender, c11_payment_by_entity, c12_place_of_service,
        c13_drug_vs_nondrug, c14_payment_by_place, c15_top_cities, c16_credentials,
        c17_highest_paying_procedures, c18_lowest_paying_procedures, c19_boxplot_specialty_payment,
        c20_payment_efficiency, c21_services_per_patient, c22_correlation_heatmap,
        c23_medicare_participation, c24_charge_hist, c25_payment_by_state_avg,
        c26_revenue_gap_specialty, c27_unique_providers_state,
        c28_who_pays_what, c29_who_pays_by_specialty,
    ]
    for func in chart_funcs:
        func(df, CHARTS_DIR)

    out = os.path.join(REPORTS_DIR, REPORT_FILENAME)
    build_report(df, CHARTS_DIR, out)

    log("=" * 60)
    log("DONE!")
    log(f"Report: {out}")
    log(f"Charts: {CHARTS_DIR} ({len(chart_funcs)} charts)")
    log("=" * 60)

if __name__ == '__main__':
    main()
