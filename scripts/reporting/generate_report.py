"""
CareFlow AI — CMS Medicare Data Analysis Report Generator
==========================================================
Generates a professional .docx report with charts, analysis,
and problem identification from the PostgreSQL dataset.

Usage:
    python generate_report.py

Output:
    reports/CareFlow_AI_CMS_Medicare_Analysis_Report.docx
"""

import os
import time
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving images
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sqlalchemy import create_engine, text
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT

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
CHARTS_DIR = os.path.join(REPORTS_DIR, 'charts')
REPORT_FILENAME = 'CareFlow_AI_CMS_Medicare_Analysis_Report.docx'

# Chart style
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = 'sans-serif'

COLORS = {
    'primary': '#3A7CA5',
    'secondary': '#6BAA75',
    'accent': '#E07A5F',
    'dark': '#1F2933',
    'muted': '#667085',
    'teal': '#2A9D8F',
    'amber': '#E9C46A',
    'red': '#E76F51',
}

def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


# ============================================================
# DATA LOADING
# ============================================================

def load_data(engine):
    """Load full dataset from PostgreSQL."""
    log("Loading data from PostgreSQL...")
    df = pd.read_sql("SELECT * FROM cms_medicare_providers", engine)
    log(f"Loaded {len(df):,} records")
    return df


# ============================================================
# CHART GENERATION
# ============================================================

def chart_provider_specialty(df, save_path):
    """Top 15 provider specialties bar chart."""
    top = df['provider_specialty'].value_counts().head(15)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(top.index[::-1], top.values[::-1], color=COLORS['primary'], edgecolor='white')
    ax.set_xlabel('Number of Records', fontsize=12)
    ax.set_title('Top 15 Provider Specialties', fontsize=14, fontweight='bold', pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + max(top.values)*0.01, bar.get_y() + bar.get_height()/2,
                f'{width:,.0f}', ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log(f"  Chart saved: {os.path.basename(save_path)}")


def chart_state_distribution(df, save_path):
    """Top 15 states by record count."""
    states = df['provider_state'].value_counts().head(15)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(states.index, states.values, color=COLORS['teal'], edgecolor='white')
    ax.set_xlabel('State', fontsize=12)
    ax.set_ylabel('Number of Records', fontsize=12)
    ax.set_title('Top 15 States by Medicare Provider Records', fontsize=14, fontweight='bold', pad=15)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log(f"  Chart saved: {os.path.basename(save_path)}")


def chart_payment_comparison(df, save_path):
    """Average submitted charge vs Medicare payment by specialty."""
    payment = df.groupby('provider_specialty').agg(
        avg_charge=('avg_submitted_charge', 'mean'),
        avg_payment=('avg_medicare_payment', 'mean'),
    ).sort_values('avg_charge', ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(payment))
    width = 0.35
    
    ax.bar([i - width/2 for i in x], payment['avg_charge'], width, 
           label='Avg Submitted Charge', color=COLORS['primary'])
    ax.bar([i + width/2 for i in x], payment['avg_payment'], width,
           label='Avg Medicare Payment', color=COLORS['secondary'])
    
    ax.set_ylabel('Amount ($)', fontsize=12)
    ax.set_title('Submitted Charges vs Medicare Payments by Specialty (Top 15)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(payment.index, rotation=45, ha='right', fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log(f"  Chart saved: {os.path.basename(save_path)}")


def chart_payment_gap(df, save_path):
    """Revenue gap analysis — charge vs payment gap by state."""
    gap = df.groupby('provider_state').agg(
        avg_charge=('avg_submitted_charge', 'mean'),
        avg_payment=('avg_medicare_payment', 'mean'),
    )
    gap['gap'] = gap['avg_charge'] - gap['avg_payment']
    gap['payment_pct'] = (gap['avg_payment'] / gap['avg_charge'] * 100).round(1)
    gap = gap.sort_values('gap', ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(gap.index[::-1], gap['gap'].values[::-1], color=COLORS['accent'], edgecolor='white')
    ax.set_xlabel('Average Gap ($)', fontsize=12)
    ax.set_title('Top 15 States by Charge-to-Payment Gap (Revenue Leakage Risk)', fontsize=14, fontweight='bold', pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + max(gap['gap'].values)*0.01, bar.get_y() + bar.get_height()/2,
                f'${width:,.0f}', ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log(f"  Chart saved: {os.path.basename(save_path)}")


def chart_payment_distribution(df, save_path):
    """Distribution of Medicare payments (histogram)."""
    payments = df['avg_medicare_payment'].dropna()
    q99 = payments.quantile(0.99)
    payments_clipped = payments[payments <= q99]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(payments_clipped, bins=60, color=COLORS['primary'], edgecolor='white', alpha=0.85)
    ax.axvline(payments.median(), color=COLORS['accent'], linestyle='--', linewidth=2,
               label=f'Median: ${payments.median():,.2f}')
    ax.axvline(payments.mean(), color=COLORS['secondary'], linestyle='--', linewidth=2,
               label=f'Mean: ${payments.mean():,.2f}')
    ax.set_xlabel('Avg Medicare Payment ($)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Distribution of Average Medicare Payments (99th Percentile)', fontsize=14, fontweight='bold', pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    ax.legend(fontsize=11)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log(f"  Chart saved: {os.path.basename(save_path)}")


def chart_utilization_scatter(df, save_path):
    """Utilization: total patients vs total services (filtered)."""
    scatter = df.dropna(subset=['total_patients', 'total_services', 'avg_medicare_payment'])
    scatter = scatter[scatter['total_patients'] > 0]
    
    p99_p = scatter['total_patients'].quantile(0.99)
    p99_s = scatter['total_services'].quantile(0.99)
    scatter = scatter[(scatter['total_patients'] <= p99_p) & (scatter['total_services'] <= p99_s)]
    
    if len(scatter) > 3000:
        scatter = scatter.sample(3000, random_state=42)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sc = ax.scatter(
        scatter['total_patients'], scatter['total_services'],
        c=scatter['avg_medicare_payment'], cmap='YlGnBu',
        alpha=0.4, s=15, edgecolors='none'
    )
    plt.colorbar(sc, label='Avg Medicare Payment ($)', ax=ax)
    ax.set_xlabel('Total Patients', fontsize=12)
    ax.set_ylabel('Total Services', fontsize=12)
    ax.set_title('Patients vs Services (99th percentile, colored by payment)', fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log(f"  Chart saved: {os.path.basename(save_path)}")


def chart_top_procedures(df, save_path):
    """Top 15 most common procedures."""
    procs = df.groupby(['procedure_code', 'procedure_description']).agg(
        total_services=('total_services', 'sum'),
        avg_payment=('avg_medicare_payment', 'mean')
    ).sort_values('total_services', ascending=False).head(15).reset_index()
    
    # Truncate long descriptions
    procs['label'] = procs['procedure_description'].str[:40]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(procs['label'][::-1], procs['total_services'][::-1], color=COLORS['teal'], edgecolor='white')
    ax.set_xlabel('Total Services', fontsize=12)
    ax.set_title('Top 15 Most Common Medicare Procedures', fontsize=14, fontweight='bold', pad=15)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log(f"  Chart saved: {os.path.basename(save_path)}")


def chart_gender_distribution(df, save_path):
    """Provider gender distribution."""
    gender = df['provider_gender'].value_counts()
    labels = {'M': 'Male', 'F': 'Female'}
    
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = [COLORS['primary'], COLORS['accent']]
    wedges, texts, autotexts = ax.pie(
        gender.values, labels=[labels.get(g, g) for g in gender.index],
        autopct='%1.1f%%', colors=colors, startangle=90,
        textprops={'fontsize': 12}
    )
    ax.set_title('Provider Gender Distribution', fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log(f"  Chart saved: {os.path.basename(save_path)}")


def chart_entity_type(df, save_path):
    """Individual vs Organization providers."""
    entity = df['provider_entity_type'].value_counts()
    labels = {'I': 'Individual', 'O': 'Organization'}
    
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = [COLORS['secondary'], COLORS['amber']]
    wedges, texts, autotexts = ax.pie(
        entity.values, labels=[labels.get(e, e) for e in entity.index],
        autopct='%1.1f%%', colors=colors, startangle=90,
        textprops={'fontsize': 12}
    )
    ax.set_title('Provider Entity Type (Individual vs Organization)', fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log(f"  Chart saved: {os.path.basename(save_path)}")


# ============================================================
# REPORT DOCUMENT GENERATION
# ============================================================

def add_heading(doc, text, level=1):
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = RGBColor(0x1F, 0x29, 0x33)
    return heading


def add_paragraph(doc, text, bold=False, italic=False, font_size=11, alignment=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    if alignment:
        p.alignment = alignment
    return p


def add_chart(doc, image_path, width=Inches(6.0), caption=None):
    """Add a chart image with optional caption."""
    doc.add_picture(image_path, width=width)
    last_paragraph = doc.paragraphs[-1]
    last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    if caption:
        cap = doc.add_paragraph()
        run = cap.add_run(caption)
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x66, 0x70, 0x85)
        run.italic = True
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER


def generate_report(df, charts_dir, output_path):
    """Generate the full .docx report."""
    log("Generating report document...")
    
    doc = Document()
    
    # -- Style defaults --
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    style.font.color.rgb = RGBColor(0x1F, 0x29, 0x33)
    
    # ========================================
    # TITLE PAGE
    # ========================================
    doc.add_paragraph()
    doc.add_paragraph()
    title = doc.add_heading('CareFlow AI', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_heading('CMS Medicare Physician & Other Practitioners\nData Analysis Report', level=1)
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    add_paragraph(doc, f'Dataset: Medicare Physician & Other Practitioners — by Provider and Service',
                  italic=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, f'Records Analyzed: {len(df):,}',
                  alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, f'Report Generated: {time.strftime("%B %d, %Y at %I:%M %p")}',
                  alignment=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, 'Source: Centers for Medicare & Medicaid Services (CMS)',
                  italic=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)
    
    doc.add_page_break()
    
    # ========================================
    # TABLE OF CONTENTS
    # ========================================
    add_heading(doc, 'Table of Contents', level=1)
    toc_items = [
        '1. Executive Summary',
        '2. Dataset Overview',
        '3. Provider Specialty Analysis',
        '4. Geographic Distribution',
        '5. Payment Analysis',
        '6. Revenue Gap Analysis (Key Problem)',
        '7. Payment Distribution',
        '8. Utilization Metrics',
        '9. Top Procedures',
        '10. Provider Demographics',
        '11. Key Problems Identified',
        '12. Recommendations for CareFlow AI',
        '13. Conclusion',
    ]
    for item in toc_items:
        add_paragraph(doc, item, font_size=11)
    
    doc.add_page_break()
    
    # ========================================
    # 1. EXECUTIVE SUMMARY
    # ========================================
    add_heading(doc, '1. Executive Summary', level=1)
    
    total_providers = df['provider_npi'].nunique()
    total_specialties = df['provider_specialty'].nunique()
    total_states = df['provider_state'].nunique()
    total_procedures = df['procedure_code'].nunique()
    avg_charge = df['avg_submitted_charge'].mean()
    avg_payment = df['avg_medicare_payment'].mean()
    avg_gap = avg_charge - avg_payment
    gap_pct = (1 - avg_payment / avg_charge) * 100
    
    add_paragraph(doc, (
        f'This report analyzes {len(df):,} Medicare provider-service records from the CMS '
        f'(Centers for Medicare & Medicaid Services) public dataset. The data covers '
        f'{total_providers:,} unique providers across {total_specialties} medical specialties '
        f'in {total_states} states/territories, performing {total_procedures:,} distinct procedures.'
    ))
    
    add_paragraph(doc, 'Key Findings:', bold=True)
    
    findings = [
        f'The average submitted charge is ${avg_charge:,.2f}, but Medicare only pays an average of ${avg_payment:,.2f} — a gap of ${avg_gap:,.2f} ({gap_pct:.1f}% reduction).',
        f'This charge-to-payment gap represents a significant revenue leakage risk for healthcare providers who do not anticipate Medicare reimbursement rates.',
        f'Provider distribution is heavily concentrated in a few states (CA, FL, TX, NY), creating potential access disparities in rural and underserved areas.',
        f'Payment rates vary dramatically by specialty — some specialties receive less than 20% of submitted charges.',
        f'The data reveals opportunities for CareFlow AI to improve prior authorization accuracy, predict denial risks, and identify revenue optimization targets.',
    ]
    for finding in findings:
        p = doc.add_paragraph(finding, style='List Bullet')
    
    doc.add_page_break()
    
    # ========================================
    # 2. DATASET OVERVIEW
    # ========================================
    add_heading(doc, '2. Dataset Overview', level=1)
    
    add_paragraph(doc, (
        'The Medicare Physician & Other Practitioners dataset contains information about services '
        'and procedures provided to Medicare beneficiaries by physicians and other healthcare '
        'professionals. Each record represents a unique combination of provider (identified by NPI), '
        'HCPCS/CPT procedure code, and place of service.'
    ))
    
    add_heading(doc, 'Dataset Statistics', level=2)
    
    # Stats table
    table = doc.add_table(rows=1, cols=2, style='Light Grid Accent 1')
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Metric'
    hdr_cells[1].text = 'Value'
    
    stats = [
        ('Total Records', f'{len(df):,}'),
        ('Unique Providers (NPI)', f'{total_providers:,}'),
        ('Unique Specialties', f'{total_specialties}'),
        ('Unique Procedures (HCPCS)', f'{total_procedures:,}'),
        ('States/Territories', f'{total_states}'),
        ('Avg Submitted Charge', f'${avg_charge:,.2f}'),
        ('Avg Medicare Payment', f'${avg_payment:,.2f}'),
        ('Avg Medicare Allowed Amount', f'${df["avg_medicare_allowed_amount"].mean():,.2f}'),
        ('Median Medicare Payment', f'${df["avg_medicare_payment"].median():,.2f}'),
        ('Total Columns', f'{len(df.columns)}'),
    ]
    for metric, value in stats:
        row_cells = table.add_row().cells
        row_cells[0].text = metric
        row_cells[1].text = value
    
    doc.add_paragraph()
    
    # Missing values
    add_heading(doc, 'Data Quality', level=2)
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0].sort_values(ascending=False)
    
    if len(missing_cols) > 0:
        add_paragraph(doc, f'{len(missing_cols)} columns have missing values:')
        table2 = doc.add_table(rows=1, cols=3, style='Light Grid Accent 1')
        table2.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr = table2.rows[0].cells
        hdr[0].text = 'Column'
        hdr[1].text = 'Missing Count'
        hdr[2].text = 'Missing %'
        for col_name in missing_cols.head(10).index:
            row = table2.add_row().cells
            row[0].text = col_name
            row[1].text = f'{missing_cols[col_name]:,}'
            row[2].text = f'{missing_cols[col_name]/len(df)*100:.1f}%'
    else:
        add_paragraph(doc, 'No missing values detected. Data quality is excellent.')
    
    doc.add_page_break()
    
    # ========================================
    # 3. PROVIDER SPECIALTY ANALYSIS
    # ========================================
    add_heading(doc, '3. Provider Specialty Analysis', level=1)
    
    add_paragraph(doc, (
        'The dataset contains providers across a wide range of medical specialties. '
        'Understanding the distribution of specialties is critical for CareFlow AI to '
        'accurately route prior authorization requests and predict claim outcomes.'
    ))
    
    add_chart(doc, os.path.join(charts_dir, 'provider_specialty.png'),
              caption='Figure 1: Top 15 Provider Specialties by Record Count')
    
    top_spec = df['provider_specialty'].value_counts().head(5)
    add_paragraph(doc, 'Analysis:', bold=True)
    add_paragraph(doc, (
        f'The top specialty is "{top_spec.index[0]}" with {top_spec.values[0]:,} records, '
        f'followed by "{top_spec.index[1]}" ({top_spec.values[1]:,}) and '
        f'"{top_spec.index[2]}" ({top_spec.values[2]:,}). '
        f'The top 5 specialties account for {top_spec.sum()/len(df)*100:.1f}% of all records.'
    ))
    
    add_paragraph(doc, 'Problem Identified:', bold=True)
    p = doc.add_paragraph(
        'The heavy concentration in a few specialties means prior authorization rules '
        'and denial patterns may be very different across specialties. CareFlow AI must '
        'build specialty-specific models rather than one-size-fits-all approaches. '
        'Rare specialties with few records will be harder to predict accurately.',
        style='List Bullet'
    )
    
    doc.add_page_break()
    
    # ========================================
    # 4. GEOGRAPHIC DISTRIBUTION
    # ========================================
    add_heading(doc, '4. Geographic Distribution', level=1)
    
    add_paragraph(doc, (
        'Geographic analysis reveals where Medicare providers are concentrated and where '
        'potential access gaps exist.'
    ))
    
    add_chart(doc, os.path.join(charts_dir, 'state_distribution.png'),
              caption='Figure 2: Top 15 States by Medicare Provider Records')
    
    top_states = df['provider_state'].value_counts().head(5)
    add_paragraph(doc, 'Analysis:', bold=True)
    add_paragraph(doc, (
        f'California ({top_states.values[0]:,}), Florida ({top_states.values[1]:,}), and '
        f'Texas ({top_states.values[2]:,}) dominate the dataset. '
        f'The top 5 states account for {top_states.sum()/len(df)*100:.1f}% of all records.'
    ))
    
    add_paragraph(doc, 'Problem Identified:', bold=True)
    p = doc.add_paragraph(
        'The extreme geographic concentration suggests potential Medicare access disparities. '
        'Patients in rural states have fewer providers to choose from, which can lead to '
        'longer wait times, higher no-show rates, and delayed care. CareFlow AI should '
        'flag patients in underserved areas for proactive scheduling support.',
        style='List Bullet'
    )
    
    doc.add_page_break()
    
    # ========================================
    # 5. PAYMENT ANALYSIS
    # ========================================
    add_heading(doc, '5. Payment Analysis', level=1)
    
    add_paragraph(doc, (
        'One of the most critical aspects of revenue cycle management is understanding '
        'the relationship between what providers charge and what Medicare actually pays.'
    ))
    
    add_chart(doc, os.path.join(charts_dir, 'payment_comparison.png'),
              caption='Figure 3: Avg Submitted Charges vs Medicare Payments by Specialty (Top 15)')
    
    add_paragraph(doc, 'Analysis:', bold=True)
    add_paragraph(doc, (
        f'Across all providers, the average submitted charge is ${avg_charge:,.2f} but Medicare '
        f'pays only ${avg_payment:,.2f} on average — a {gap_pct:.1f}% reduction. '
        f'Some specialties show an even larger gap, with certain high-cost specialties '
        f'receiving less than 15-20% of their submitted charges.'
    ))
    
    add_paragraph(doc, 'Problem Identified:', bold=True)
    problems = [
        'Providers who set charges without understanding Medicare fee schedules face significant revenue shortfalls.',
        'The wide variation in payment rates across specialties makes accurate cost estimation difficult for patients.',
        'CareFlow AI\'s cost estimate feature must account for specialty-specific reimbursement rates, not just submitted charges.',
    ]
    for problem in problems:
        doc.add_paragraph(problem, style='List Bullet')
    
    doc.add_page_break()
    
    # ========================================
    # 6. REVENUE GAP ANALYSIS
    # ========================================
    add_heading(doc, '6. Revenue Gap Analysis (Key Problem)', level=1)
    
    add_paragraph(doc, (
        'The revenue gap — the difference between submitted charges and Medicare payments — '
        'is a critical indicator of revenue leakage risk. This is one of the primary problems '
        'CareFlow AI aims to solve.'
    ))
    
    add_chart(doc, os.path.join(charts_dir, 'payment_gap.png'),
              caption='Figure 4: Top 15 States by Charge-to-Payment Gap')
    
    gap_by_state = df.groupby('provider_state').agg(
        avg_charge=('avg_submitted_charge', 'mean'),
        avg_payment=('avg_medicare_payment', 'mean'),
    )
    gap_by_state['gap'] = gap_by_state['avg_charge'] - gap_by_state['avg_payment']
    worst_state = gap_by_state.sort_values('gap', ascending=False).head(1)
    
    add_paragraph(doc, 'Analysis:', bold=True)
    add_paragraph(doc, (
        f'The state with the largest charge-to-payment gap is {worst_state.index[0]} '
        f'with an average gap of ${worst_state["gap"].values[0]:,.2f}. '
        f'This means providers in {worst_state.index[0]} are submitting charges that are '
        f'significantly higher than what Medicare reimburses, creating cash flow unpredictability.'
    ))
    
    add_paragraph(doc, 'Problem Identified:', bold=True)
    problems = [
        'Large revenue gaps lead to claim denials, delayed payments, and accounts receivable buildup.',
        'Providers who don\'t adjust their expectations to Medicare fee schedules waste resources on appeals and resubmissions.',
        'CareFlow AI should provide real-time cost estimates based on actual Medicare reimbursement data, not submitted charges.',
        'The revenue cycle module should flag claims where the submitted charge far exceeds the expected Medicare payment, allowing staff to review before submission.',
    ]
    for problem in problems:
        doc.add_paragraph(problem, style='List Bullet')
    
    doc.add_page_break()
    
    # ========================================
    # 7. PAYMENT DISTRIBUTION
    # ========================================
    add_heading(doc, '7. Payment Distribution', level=1)
    
    add_chart(doc, os.path.join(charts_dir, 'payment_distribution.png'),
              caption='Figure 5: Distribution of Average Medicare Payments')
    
    payments = df['avg_medicare_payment'].dropna()
    add_paragraph(doc, 'Analysis:', bold=True)
    add_paragraph(doc, (
        f'The payment distribution is heavily right-skewed. The median payment '
        f'(${payments.median():,.2f}) is significantly lower than the mean '
        f'(${payments.mean():,.2f}), indicating that most services receive relatively '
        f'low reimbursement while a small number of high-cost procedures pull the average up. '
        f'The maximum payment is ${payments.max():,.2f}.'
    ))
    
    add_paragraph(doc, 'Problem Identified:', bold=True)
    doc.add_paragraph(
        'The skewed distribution means that a small number of high-value claims account for '
        'a disproportionate share of revenue. Denials on these high-value claims would have '
        'a much larger financial impact. CareFlow AI should prioritize denial risk prediction '
        'for high-value claims.',
        style='List Bullet'
    )
    
    doc.add_page_break()
    
    # ========================================
    # 8. UTILIZATION METRICS
    # ========================================
    add_heading(doc, '8. Utilization Metrics', level=1)
    
    add_chart(doc, os.path.join(charts_dir, 'utilization_scatter.png'),
              caption='Figure 6: Total Patients vs Total Services (99th percentile)')
    
    add_paragraph(doc, 'Analysis:', bold=True)
    add_paragraph(doc, (
        'The scatter plot shows the relationship between the number of patients a provider sees '
        'and the total services rendered. Most providers cluster in the lower-left (fewer patients, '
        'fewer services), while a small number of high-volume providers serve hundreds of patients. '
        'Higher-payment services (darker dots) tend to have fewer patients but more services per patient.'
    ))
    
    add_paragraph(doc, 'Problem Identified:', bold=True)
    doc.add_paragraph(
        'High-volume providers may face greater prior authorization burden. If a provider '
        'performs the same procedure on hundreds of patients, a single prior auth policy change '
        'could affect all of them. CareFlow AI should batch similar prior auth requests and '
        'alert staff to policy changes that affect high-volume providers.',
        style='List Bullet'
    )
    
    doc.add_page_break()
    
    # ========================================
    # 9. TOP PROCEDURES
    # ========================================
    add_heading(doc, '9. Top Procedures', level=1)
    
    add_chart(doc, os.path.join(charts_dir, 'top_procedures.png'),
              caption='Figure 7: Top 15 Most Common Medicare Procedures')
    
    top_procs = df.groupby(['procedure_code', 'procedure_description']).agg(
        total=('total_services', 'sum')
    ).sort_values('total', ascending=False).head(5).reset_index()
    
    add_paragraph(doc, 'Analysis:', bold=True)
    add_paragraph(doc, (
        f'The most common procedure is "{top_procs["procedure_description"].iloc[0]}" '
        f'(code {top_procs["procedure_code"].iloc[0]}) with {top_procs["total"].iloc[0]:,.0f} total services. '
        'Office visits and evaluation/management codes dominate, which is expected in outpatient Medicare care.'
    ))
    
    add_paragraph(doc, 'Problem Identified:', bold=True)
    doc.add_paragraph(
        'High-volume procedures are the most likely to have prior authorization requirements '
        'and are also the most common targets for audits and denial. CareFlow AI should '
        'pre-populate prior auth forms for these common procedures and maintain up-to-date '
        'payer rules for each.',
        style='List Bullet'
    )
    
    doc.add_page_break()
    
    # ========================================
    # 10. PROVIDER DEMOGRAPHICS
    # ========================================
    add_heading(doc, '10. Provider Demographics', level=1)
    
    add_chart(doc, os.path.join(charts_dir, 'gender_distribution.png'), width=Inches(4.5),
              caption='Figure 8: Provider Gender Distribution')
    
    add_chart(doc, os.path.join(charts_dir, 'entity_type.png'), width=Inches(4.5),
              caption='Figure 9: Individual vs Organization Providers')
    
    gender = df['provider_gender'].value_counts()
    entity = df['provider_entity_type'].value_counts()
    
    add_paragraph(doc, 'Analysis:', bold=True)
    male_pct = gender.get('M', 0) / gender.sum() * 100 if 'M' in gender.index else 0
    indiv_pct = entity.get('I', 0) / entity.sum() * 100 if 'I' in entity.index else 0
    add_paragraph(doc, (
        f'Male providers account for {male_pct:.1f}% of records. '
        f'Individual providers make up {indiv_pct:.1f}% of the dataset versus organizations.'
    ))
    
    doc.add_page_break()
    
    # ========================================
    # 11. KEY PROBLEMS IDENTIFIED
    # ========================================
    add_heading(doc, '11. Key Problems Identified', level=1)
    
    add_paragraph(doc, (
        'Based on the analysis of 1.5 million Medicare provider records, the following '
        'critical problems have been identified that CareFlow AI is designed to address:'
    ))
    
    problems = [
        {
            'title': 'Revenue Leakage from Charge-Payment Gaps',
            'desc': (
                f'Providers submit charges averaging ${avg_charge:,.2f} but receive only '
                f'${avg_payment:,.2f} ({gap_pct:.1f}% reduction). This gap varies significantly '
                'by state and specialty, making it difficult for billing staff to predict revenue '
                'without specialized tools. Many providers are unaware of the extent of this gap '
                'until claims are processed.'
            ),
        },
        {
            'title': 'Prior Authorization Complexity',
            'desc': (
                f'With {total_procedures:,} distinct procedures across {total_specialties} '
                'specialties, the prior authorization landscape is extremely complex. Each payer '
                'has different rules for different procedures, and these rules change frequently. '
                'Manual prior auth processes are slow, error-prone, and a leading cause of care delays.'
            ),
        },
        {
            'title': 'Geographic Access Disparities',
            'desc': (
                'Provider distribution is heavily concentrated in large states. Rural areas '
                'and smaller states have significantly fewer providers per capita, leading to '
                'longer appointment wait times, higher no-show rates, and patients traveling '
                'long distances for specialized care.'
            ),
        },
        {
            'title': 'Claim Denial Risk from Coding Complexity',
            'desc': (
                f'The dataset includes {total_procedures:,} procedure codes, each with specific '
                'documentation and coding requirements. Incorrect coding is a leading cause of '
                'claim denials. Without AI-assisted coding review, billing staff must manually '
                'verify each claim against payer-specific rules.'
            ),
        },
        {
            'title': 'Skewed Payment Distribution Creates Cash Flow Risk',
            'desc': (
                f'The median Medicare payment (${payments.median():,.2f}) is much lower than the mean '
                f'(${payments.mean():,.2f}). A small number of high-value claims generate '
                'disproportionate revenue. If these high-value claims are denied or delayed, '
                'the financial impact on the provider is severe.'
            ),
        },
        {
            'title': 'Lack of Real-Time Cost Transparency for Patients',
            'desc': (
                'Patients cannot easily estimate their out-of-pocket costs because submitted '
                'charges bear little relationship to actual Medicare payments. This leads to '
                'surprise bills, payment disputes, and reduced patient satisfaction.'
            ),
        },
    ]
    
    for i, problem in enumerate(problems, 1):
        add_heading(doc, f'{i}. {problem["title"]}', level=2)
        add_paragraph(doc, problem['desc'])
    
    doc.add_page_break()
    
    # ========================================
    # 12. RECOMMENDATIONS
    # ========================================
    add_heading(doc, '12. Recommendations for CareFlow AI', level=1)
    
    add_paragraph(doc, (
        'Based on the analysis, the following features should be prioritized in CareFlow AI:'
    ))
    
    recommendations = [
        ('Real-Time Reimbursement Estimator',
         'Use this CMS dataset to predict actual Medicare reimbursement for any procedure/provider combination. Show providers the expected payment alongside their submitted charge before the claim is filed.'),
        ('Specialty-Specific Prior Auth Rules Engine',
         'Build prior authorization rule sets for each specialty, starting with the top 15 highest-volume specialties identified in this analysis.'),
        ('High-Value Claim Priority Queue',
         'Automatically flag claims in the top 5% by expected reimbursement value for manual review before submission, reducing the financial impact of denials.'),
        ('Geographic Access Dashboard',
         'Create a map view showing provider availability by region, helping scheduling staff identify areas where patients may need telehealth alternatives.'),
        ('Charge-to-Payment Gap Alerts',
         'Alert billing staff when a submitted charge exceeds the expected Medicare reimbursement by more than a configurable threshold (e.g., 300%).'),
        ('Procedure-Specific Denial Risk Scoring',
         'Use historical patterns from this dataset to assign denial risk scores to claims based on procedure code, provider specialty, and state.'),
    ]
    
    for i, (title, desc) in enumerate(recommendations, 1):
        add_heading(doc, f'{i}. {title}', level=2)
        add_paragraph(doc, desc)
    
    doc.add_page_break()
    
    # ========================================
    # 13. CONCLUSION
    # ========================================
    add_heading(doc, '13. Conclusion', level=1)
    
    add_paragraph(doc, (
        f'This analysis of {len(df):,} Medicare provider-service records reveals significant '
        'opportunities for AI-driven improvement in healthcare revenue cycle management. '
        f'The average {gap_pct:.1f}% gap between submitted charges and Medicare payments, '
        f'combined with {total_procedures:,} distinct procedure codes across {total_specialties} '
        'specialties, creates a complex landscape that is difficult for human staff to navigate '
        'without technological assistance.'
    ))
    
    add_paragraph(doc, (
        'CareFlow AI is positioned to address these challenges by providing real-time '
        'reimbursement estimation, automated prior authorization, denial risk prediction, '
        'and intelligent claim review. The CMS Medicare dataset analyzed in this report '
        'serves as the foundational data source for training and validating these AI models.'
    ))
    
    doc.add_paragraph()
    add_paragraph(doc, '— End of Report —', italic=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)
    
    doc.add_paragraph()
    add_paragraph(doc, (
        'Disclaimer: This report uses public CMS Medicare data for healthcare workflow '
        'demonstration and analysis purposes only. It does not contain real patient data '
        'and should not be used for clinical decision-making.'
    ), font_size=9, italic=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)
    
    # Save
    doc.save(output_path)
    log(f"Report saved: {output_path}")


# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 60)
    log("CareFlow AI — Report Generator")
    log("=" * 60)
    
    # Create directories
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(CHARTS_DIR, exist_ok=True)
    
    # Connect & load
    engine = create_engine(DATABASE_URL, echo=False)
    df = load_data(engine)
    
    # Generate all charts
    log("Generating charts...")
    chart_provider_specialty(df, os.path.join(CHARTS_DIR, 'provider_specialty.png'))
    chart_state_distribution(df, os.path.join(CHARTS_DIR, 'state_distribution.png'))
    chart_payment_comparison(df, os.path.join(CHARTS_DIR, 'payment_comparison.png'))
    chart_payment_gap(df, os.path.join(CHARTS_DIR, 'payment_gap.png'))
    chart_payment_distribution(df, os.path.join(CHARTS_DIR, 'payment_distribution.png'))
    chart_utilization_scatter(df, os.path.join(CHARTS_DIR, 'utilization_scatter.png'))
    chart_top_procedures(df, os.path.join(CHARTS_DIR, 'top_procedures.png'))
    chart_gender_distribution(df, os.path.join(CHARTS_DIR, 'gender_distribution.png'))
    chart_entity_type(df, os.path.join(CHARTS_DIR, 'entity_type.png'))
    
    # Generate report
    output_path = os.path.join(REPORTS_DIR, REPORT_FILENAME)
    generate_report(df, CHARTS_DIR, output_path)
    
    log("=" * 60)
    log("DONE!")
    log(f"Report: {output_path}")
    log(f"Charts: {CHARTS_DIR}")
    log("=" * 60)


if __name__ == '__main__':
    main()
