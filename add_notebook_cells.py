"""
Adds expanded visualization cells to the bottom of cms_data_pipeline.ipynb
"""
import json

NOTEBOOK_PATH = r"cms_data_pipeline.ipynb"

# Read existing notebook
with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_cells = []

def md(source):
    new_cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")]
    })

def code(source):
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.split("\n")]
    })

# ── SECTION 9: LOAD FULL DATASET ──
md("---\n# 9. Load Full Dataset from PostgreSQL\n\nLoad all 1.5M records from PostgreSQL for comprehensive analysis.\n\n> **Note:** Run this cell to replace the 10K sample `df` with the full dataset.")

code("""# Load full dataset from PostgreSQL
print("Loading full dataset from PostgreSQL...")
df = pd.read_sql("SELECT * FROM cms_medicare_providers", engine)
print(f"Loaded {len(df):,} records ({df.memory_usage(deep=True).sum() / 1024**2:.0f} MB in RAM)")
df.head()""")

# ── SECTION 10: COMPREHENSIVE STATS ──
md("---\n# 10. Comprehensive Dataset Statistics\n\nFull statistical overview of the dataset.")

code("""# Key summary statistics
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
gap = avg_charge - avg_pay
gap_pct = (1 - avg_pay / avg_charge) * 100

print("=" * 55)
print("       CareFlow AI — Dataset Summary")
print("=" * 55)
print(f"  Total Records:               {n:>12,}")
print(f"  Unique Providers (NPI):       {n_providers:>12,}")
print(f"  Unique Specialties:           {n_specialties:>12,}")
print(f"  Unique Procedures (HCPCS):    {n_procedures:>12,}")
print(f"  States/Territories:           {n_states:>12,}")
print(f"  Cities:                       {n_cities:>12,}")
print("-" * 55)
print(f"  Avg Submitted Charge:         ${avg_charge:>11,.2f}")
print(f"  Median Submitted Charge:      ${med_charge:>11,.2f}")
print(f"  Avg Medicare Payment:         ${avg_pay:>11,.2f}")
print(f"  Median Medicare Payment:      ${med_pay:>11,.2f}")
print(f"  Avg Medicare Allowed Amt:     ${avg_allowed:>11,.2f}")
print(f"  Avg Standardized Amt:         ${avg_std:>11,.2f}")
print(f"  Avg Charge-to-Payment Gap:    ${gap:>11,.2f} ({gap_pct:.1f}%)")
print(f"  Max Payment:                  ${df['avg_medicare_payment'].max():>11,.2f}")
print(f"  Min Payment:                  ${df['avg_medicare_payment'].min():>11,.2f}")
print("-" * 55)
print(f"  Avg Patients/Record:          {df['total_patients'].mean():>12,.1f}")
print(f"  Median Patients/Record:       {df['total_patients'].median():>12,.1f}")
print(f"  Avg Services/Record:          {df['total_services'].mean():>12,.1f}")
print(f"  Median Services/Record:       {df['total_services'].median():>12,.1f}")
print("=" * 55)""")

md("## 10.1 Descriptive Statistics (All Numeric Columns)")

code("""# Full descriptive statistics
numeric_cols = ['total_patients', 'total_services', 'total_patient_day_services',
                'avg_submitted_charge', 'avg_medicare_allowed_amount',
                'avg_medicare_payment', 'avg_medicare_standardized_amount']
df[numeric_cols].describe().round(2)""")

md("## 10.2 Missing Values Analysis")

code("""# Missing values
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({'Missing Count': missing, 'Missing %': missing_pct})
missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
if len(missing_df) > 0:
    print(f"{len(missing_df)} columns have missing values:\\n")
    display(missing_df)
else:
    print("No missing values! Data quality is excellent.")""")

# ── SECTION 11: EXPANDED VISUALIZATIONS ──
md("---\n# 11. Expanded Data Visualizations\n\nComprehensive charts covering provider demographics, payment breakdowns, service analysis, and more.")

md("## 11.1 Provider Credentials Distribution")

code("""# Top 15 provider credentials
creds = df['provider_credentials'].dropna().value_counts().head(15)

fig = px.bar(
    x=creds.index, y=creds.values,
    title='Top 15 Provider Credentials',
    labels={'x': 'Credential', 'y': 'Number of Records'},
    color=creds.values,
    color_continuous_scale='Teal',
)
fig.update_layout(height=450, showlegend=False, coloraxis_showscale=False)
fig.show()
print(f"\\nTop 3: {creds.index[0]} ({creds.values[0]:,}), {creds.index[1]} ({creds.values[1]:,}), {creds.index[2]} ({creds.values[2]:,})")""")

md("## 11.2 Medicare Participation Rate")

code("""# Medicare participating vs non-participating
mp = df['medicare_participating'].dropna().value_counts()
labels_map = {'Y': 'Participating', 'N': 'Non-Participating'}

fig = px.pie(
    values=mp.values,
    names=[labels_map.get(k, k) for k in mp.index],
    title='Medicare Participation Rate',
    color_discrete_sequence=['#2A9D8F', '#E07A5F'],
    hole=0.4
)
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.update_layout(height=400)
fig.show()

if 'Y' in mp.index:
    print(f"\\n{mp['Y']/mp.sum()*100:.1f}% of records are Medicare-participating providers")""")

md("## 11.3 Place of Service (Facility vs Office)")

code("""# Place of service distribution
pos = df['place_of_service'].dropna().value_counts()
labels_map = {'F': 'Facility', 'O': 'Office'}

fig = px.pie(
    values=pos.values,
    names=[labels_map.get(k, k) for k in pos.index],
    title='Place of Service Distribution',
    color_discrete_sequence=['#264653', '#2A9D8F'],
    hole=0.4
)
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.update_layout(height=400)
fig.show()""")

md("## 11.4 Drug vs Non-Drug Services")

code("""# Drug vs non-drug services
drug = df['is_drug_service'].dropna().value_counts()
labels_map = {'Y': 'Drug Services', 'N': 'Non-Drug Services'}

fig = px.pie(
    values=drug.values,
    names=[labels_map.get(k, k) for k in drug.index],
    title='Drug vs Non-Drug Services',
    color_discrete_sequence=['#7B2D8E', '#6BAA75'],
    hole=0.4
)
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.update_layout(height=400)
fig.show()

if 'Y' in drug.index:
    print(f"\\nDrug services: {drug['Y']/drug.sum()*100:.1f}% of all records")""")

md("## 11.5 Payment by Provider Gender")

code("""# Average payment by gender
gender_pay = df.groupby('provider_gender')['avg_medicare_payment'].agg(['mean', 'median']).reset_index()
gender_pay.columns = ['Gender', 'Mean Payment', 'Median Payment']
gender_pay['Gender'] = gender_pay['Gender'].map({'M': 'Male', 'F': 'Female'})
gender_pay = gender_pay.dropna(subset=['Gender'])

fig = go.Figure()
fig.add_trace(go.Bar(name='Mean Payment', x=gender_pay['Gender'], y=gender_pay['Mean Payment'],
                     marker_color='#3A7CA5'))
fig.add_trace(go.Bar(name='Median Payment', x=gender_pay['Gender'], y=gender_pay['Median Payment'],
                     marker_color='#E07A5F'))
fig.update_layout(barmode='group', title='Average Medicare Payment by Provider Gender',
                  yaxis_title='Payment ($)', height=400)
fig.show()

for _, row in gender_pay.iterrows():
    print(f"{row['Gender']}: Mean ${row['Mean Payment']:,.2f} | Median ${row['Median Payment']:,.2f}")""")

md("## 11.6 Payment by Entity Type (Individual vs Organization)")

code("""# Average payment by entity type
entity_pay = df.groupby('provider_entity_type')['avg_medicare_payment'].agg(['mean', 'median']).reset_index()
entity_pay.columns = ['Entity', 'Mean Payment', 'Median Payment']
entity_pay['Entity'] = entity_pay['Entity'].map({'I': 'Individual', 'O': 'Organization'})
entity_pay = entity_pay.dropna(subset=['Entity'])

fig = go.Figure()
fig.add_trace(go.Bar(name='Mean Payment', x=entity_pay['Entity'], y=entity_pay['Mean Payment'],
                     marker_color='#6BAA75'))
fig.add_trace(go.Bar(name='Median Payment', x=entity_pay['Entity'], y=entity_pay['Median Payment'],
                     marker_color='#E9C46A'))
fig.update_layout(barmode='group', title='Average Medicare Payment by Entity Type',
                  yaxis_title='Payment ($)', height=400)
fig.show()

for _, row in entity_pay.iterrows():
    print(f"{row['Entity']}: Mean ${row['Mean Payment']:,.2f} | Median ${row['Median Payment']:,.2f}")""")

md("## 11.7 Payment: Facility vs Office")

code("""# Payment by place of service
place_pay = df.groupby('place_of_service')['avg_medicare_payment'].agg(['mean', 'median']).reset_index()
place_pay.columns = ['Place', 'Mean Payment', 'Median Payment']
place_pay['Place'] = place_pay['Place'].map({'F': 'Facility', 'O': 'Office'})
place_pay = place_pay.dropna(subset=['Place'])

fig = go.Figure()
fig.add_trace(go.Bar(name='Mean Payment', x=place_pay['Place'], y=place_pay['Mean Payment'],
                     marker_color='#264653'))
fig.add_trace(go.Bar(name='Median Payment', x=place_pay['Place'], y=place_pay['Median Payment'],
                     marker_color='#2A9D8F'))
fig.update_layout(barmode='group', title='Average Payment: Facility vs Office',
                  yaxis_title='Payment ($)', height=400)
fig.show()

for _, row in place_pay.iterrows():
    print(f"{row['Place']}: Mean ${row['Mean Payment']:,.2f} | Median ${row['Median Payment']:,.2f}")""")

md("## 11.8 Top 20 Cities by Provider Count")

code("""# Top 20 cities
cities = df.groupby(['provider_city', 'provider_state']).size().reset_index(name='count')
cities['label'] = cities['provider_city'] + ', ' + cities['provider_state']
cities = cities.sort_values('count', ascending=False).head(20)

fig = px.bar(
    cities, x='count', y='label', orientation='h',
    title='Top 20 Cities by Medicare Provider Records',
    labels={'count': 'Records', 'label': 'City'},
    color='count', color_continuous_scale='Teal'
)
fig.update_layout(height=550, yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
fig.show()""")

md("## 11.9 Top 20 Highest-Paying Procedures")

code("""# Highest paying procedures (min 1000 total services for significance)
proc_pay = df.groupby(['procedure_code', 'procedure_description']).agg(
    avg_payment=('avg_medicare_payment', 'mean'),
    total_svc=('total_services', 'sum')
).reset_index()
proc_pay = proc_pay[proc_pay['total_svc'] >= 1000]
top_pay = proc_pay.sort_values('avg_payment', ascending=False).head(20)
top_pay['label'] = top_pay['procedure_code'] + ' - ' + top_pay['procedure_description'].str[:40]

fig = px.bar(
    top_pay, x='avg_payment', y='label', orientation='h',
    title='Top 20 Highest-Paying Procedures (min 1,000 services)',
    labels={'avg_payment': 'Avg Medicare Payment ($)', 'label': 'Procedure'},
    color='avg_payment', color_continuous_scale='Greens'
)
fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
fig.show()""")

md("## 11.10 Top 20 Lowest-Paying Procedures")

code("""# Lowest paying procedures
low_pay = proc_pay.sort_values('avg_payment', ascending=True).head(20)
low_pay['label'] = low_pay['procedure_code'] + ' - ' + low_pay['procedure_description'].str[:40]

fig = px.bar(
    low_pay, x='avg_payment', y='label', orientation='h',
    title='Top 20 Lowest-Paying Procedures (min 1,000 services)',
    labels={'avg_payment': 'Avg Medicare Payment ($)', 'label': 'Procedure'},
    color='avg_payment', color_continuous_scale='Reds_r'
)
fig.update_layout(height=600, yaxis={'categoryorder': 'total descending'}, coloraxis_showscale=False)
fig.show()""")

md("## 11.11 Payment Efficiency by Specialty\n\n*How much of the submitted charge does Medicare actually pay? Lower = more revenue loss.*")

code("""# Payment efficiency = (payment / charge) * 100
efficiency = df.groupby('provider_specialty').agg(
    avg_charge=('avg_submitted_charge', 'mean'),
    avg_payment=('avg_medicare_payment', 'mean')
)
efficiency['efficiency_pct'] = (efficiency['avg_payment'] / efficiency['avg_charge'] * 100).round(1)
bottom20 = efficiency.sort_values('efficiency_pct').head(20).reset_index()

fig = px.bar(
    bottom20, x='efficiency_pct', y='provider_specialty', orientation='h',
    title='Bottom 20 Specialties by Payment Efficiency (Payment/Charge %)',
    labels={'efficiency_pct': 'Payment Efficiency (%)', 'provider_specialty': 'Specialty'},
    color='efficiency_pct', color_continuous_scale='RdYlGn',
    range_color=[0, 60]
)
fig.add_vline(x=50, line_dash="dash", line_color="gray", annotation_text="50%")
fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
fig.show()

print("\\nSpecialties receiving LESS than 25% of submitted charges:")
for _, row in bottom20[bottom20['efficiency_pct'] < 25].iterrows():
    print(f"  {row['provider_specialty']}: {row['efficiency_pct']:.1f}%")""")

md("## 11.12 Services per Patient by Specialty\n\n*Which specialties see each patient the most times?*")

code("""# Services per patient ratio
svc = df.dropna(subset=['total_patients', 'total_services'])
svc = svc[svc['total_patients'] > 0].copy()
svc['svc_per_patient'] = svc['total_services'] / svc['total_patients']

ratio = svc.groupby('provider_specialty')['svc_per_patient'].mean().sort_values(ascending=False).head(20).reset_index()
ratio.columns = ['Specialty', 'Avg Services per Patient']

fig = px.bar(
    ratio, x='Avg Services per Patient', y='Specialty', orientation='h',
    title='Top 20 Specialties by Services-per-Patient Ratio',
    color='Avg Services per Patient', color_continuous_scale='Purples'
)
fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
fig.show()""")

md("## 11.13 Submitted Charge Distribution")

code("""# Charge distribution histogram
charges = df['avg_submitted_charge'].dropna()
q99 = charges.quantile(0.99)
charges_clipped = charges[charges <= q99]

fig = go.Figure()
fig.add_trace(go.Histogram(x=charges_clipped, nbinsx=80, marker_color='#264653', opacity=0.85))
fig.add_vline(x=charges.median(), line_dash="dash", line_color="#E07A5F",
              annotation_text=f"Median: ${charges.median():,.2f}")
fig.add_vline(x=charges.mean(), line_dash="dash", line_color="#6BAA75",
              annotation_text=f"Mean: ${charges.mean():,.2f}")
fig.update_layout(title='Distribution of Submitted Charges (99th percentile)',
                  xaxis_title='Avg Submitted Charge ($)', yaxis_title='Frequency', height=400)
fig.show()

print(f"Min: ${charges.min():,.2f} | Mean: ${charges.mean():,.2f} | Median: ${charges.median():,.2f} | Max: ${charges.max():,.2f}")""")

md("## 11.14 Average Payment by State (Top 20)")

code("""# Average payment by state
state_pay = df.groupby('provider_state')['avg_medicare_payment'].mean().sort_values(ascending=False).head(20).reset_index()
state_pay.columns = ['State', 'Avg Payment']

fig = px.bar(
    state_pay, x='State', y='Avg Payment',
    title='Top 20 States by Average Medicare Payment',
    color='Avg Payment', color_continuous_scale='Teal'
)
fig.update_layout(height=450, coloraxis_showscale=False, yaxis_tickprefix='$')
fig.show()""")

md("## 11.15 Correlation Heatmap")

code("""# Correlation matrix of all numeric columns
import plotly.figure_factory as ff

numeric_cols = ['total_patients', 'total_services', 'total_patient_day_services',
                'avg_submitted_charge', 'avg_medicare_allowed_amount',
                'avg_medicare_payment', 'avg_medicare_standardized_amount']

corr = df[numeric_cols].corr().round(2)
labels = ['Patients', 'Services', 'Patient-Days', 'Charge', 'Allowed', 'Payment', 'Standardized']

fig = ff.create_annotated_heatmap(
    z=corr.values, x=labels, y=labels,
    colorscale='RdBu_r', showscale=True, reversescale=False
)
fig.update_layout(title='Correlation Matrix of Numeric Variables', height=550, width=700)
fig.show()

print("\\nKey correlations:")
print(f"  Charge <-> Payment:    {corr.loc['avg_submitted_charge','avg_medicare_payment']:.2f}")
print(f"  Patients <-> Services: {corr.loc['total_patients','total_services']:.2f}")
print(f"  Payment <-> Allowed:   {corr.loc['avg_medicare_payment','avg_medicare_allowed_amount']:.2f}")""")

md("## 11.16 Payment Boxplot by Top 8 Specialties")

code("""# Box plot of payments by top specialties
top8_specs = df['provider_specialty'].value_counts().head(8).index.tolist()
box_df = df[df['provider_specialty'].isin(top8_specs)][['provider_specialty', 'avg_medicare_payment']].dropna()

# Clip to 95th percentile to remove extreme outliers
q95 = box_df['avg_medicare_payment'].quantile(0.95)
box_df = box_df[box_df['avg_medicare_payment'] <= q95]

fig = px.box(
    box_df, x='provider_specialty', y='avg_medicare_payment',
    title='Payment Distribution by Top 8 Specialties (95th percentile)',
    labels={'provider_specialty': 'Specialty', 'avg_medicare_payment': 'Avg Medicare Payment ($)'},
    color='provider_specialty'
)
fig.update_layout(height=500, showlegend=False, xaxis_tickangle=-30)
fig.show()""")

md("## 11.17 Revenue Gap Analysis by Specialty")

code("""# Revenue gap by specialty (top 20 largest gaps)
gap_spec = df.groupby('provider_specialty').agg(
    avg_charge=('avg_submitted_charge', 'mean'),
    avg_payment=('avg_medicare_payment', 'mean'),
    records=('provider_npi', 'count')
).reset_index()
gap_spec['gap'] = gap_spec['avg_charge'] - gap_spec['avg_payment']
gap_spec['payment_pct'] = (gap_spec['avg_payment'] / gap_spec['avg_charge'] * 100).round(1)
gap_spec = gap_spec.sort_values('gap', ascending=False).head(20)

fig = go.Figure()
fig.add_trace(go.Bar(
    y=gap_spec['provider_specialty'], x=gap_spec['avg_charge'],
    name='Avg Charge', orientation='h', marker_color='#3A7CA5'
))
fig.add_trace(go.Bar(
    y=gap_spec['provider_specialty'], x=gap_spec['avg_payment'],
    name='Avg Payment', orientation='h', marker_color='#6BAA75'
))
fig.update_layout(
    barmode='overlay', title='Revenue Gap: Charges vs Payments by Specialty (Top 20 Gaps)',
    xaxis_title='Amount ($)', height=650,
    yaxis={'categoryorder': 'total ascending'},
    xaxis_tickprefix='$'
)
fig.show()

print("\\nLargest gaps:")
for _, row in gap_spec.head(5).iterrows():
    print(f"  {row['provider_specialty']}: Gap ${row['gap']:,.0f} (pays {row['payment_pct']:.1f}% of charge)")""")

md("## 11.18 Provider Count per State (Unique NPIs)")

code("""# Unique providers per state
providers_state = df.groupby('provider_state')['provider_npi'].nunique().sort_values(ascending=False).head(20).reset_index()
providers_state.columns = ['State', 'Unique Providers']

fig = px.bar(
    providers_state, x='State', y='Unique Providers',
    title='Top 20 States by Number of Unique Providers',
    color='Unique Providers', color_continuous_scale='Viridis'
)
fig.update_layout(height=450, coloraxis_showscale=False)
fig.show()

total_provs = df['provider_npi'].nunique()
top5_provs = providers_state.head(5)['Unique Providers'].sum()
print(f"\\nTotal unique providers: {total_provs:,}")
print(f"Top 5 states hold: {top5_provs:,} ({top5_provs/total_provs*100:.1f}% of all providers)")""")

# ── SECTION 12: SUMMARY TABLE ──
md("---\n# 12. Per-Specialty Summary Table")

code("""# Comprehensive per-specialty stats
spec_summary = df.groupby('provider_specialty').agg(
    records=('provider_npi', 'count'),
    unique_providers=('provider_npi', 'nunique'),
    avg_charge=('avg_submitted_charge', 'mean'),
    avg_payment=('avg_medicare_payment', 'mean'),
    median_payment=('avg_medicare_payment', 'median'),
    avg_patients=('total_patients', 'mean'),
    avg_services=('total_services', 'mean'),
).sort_values('records', ascending=False).head(25)

spec_summary['gap'] = spec_summary['avg_charge'] - spec_summary['avg_payment']
spec_summary['efficiency'] = (spec_summary['avg_payment'] / spec_summary['avg_charge'] * 100).round(1)

# Format
styled = spec_summary.copy()
for col in ['avg_charge', 'avg_payment', 'median_payment', 'gap']:
    styled[col] = styled[col].apply(lambda x: f'${x:,.2f}')
styled['efficiency'] = styled['efficiency'].apply(lambda x: f'{x}%')
styled['avg_patients'] = styled['avg_patients'].apply(lambda x: f'{x:.1f}')
styled['avg_services'] = styled['avg_services'].apply(lambda x: f'{x:.1f}')

styled.columns = ['Records', 'Providers', 'Avg Charge', 'Avg Payment', 'Med Payment', 
                   'Avg Patients', 'Avg Services', 'Gap', 'Efficiency']
display(styled)""")

md("---\n# 13. Per-State Summary Table")

code("""# Comprehensive per-state stats
state_summary = df.groupby('provider_state').agg(
    records=('provider_npi', 'count'),
    unique_providers=('provider_npi', 'nunique'),
    unique_specialties=('provider_specialty', 'nunique'),
    avg_charge=('avg_submitted_charge', 'mean'),
    avg_payment=('avg_medicare_payment', 'mean'),
    avg_patients=('total_patients', 'mean'),
).sort_values('records', ascending=False)

state_summary['gap'] = state_summary['avg_charge'] - state_summary['avg_payment']
state_summary['efficiency'] = (state_summary['avg_payment'] / state_summary['avg_charge'] * 100).round(1)

styled_state = state_summary.copy()
for col in ['avg_charge', 'avg_payment', 'gap']:
    styled_state[col] = styled_state[col].apply(lambda x: f'${x:,.2f}')
styled_state['efficiency'] = styled_state['efficiency'].apply(lambda x: f'{x}%')
styled_state['avg_patients'] = styled_state['avg_patients'].apply(lambda x: f'{x:.1f}')

styled_state.columns = ['Records', 'Providers', 'Specialties', 'Avg Charge', 'Avg Payment',
                         'Avg Patients', 'Gap', 'Efficiency']
display(styled_state)""")

# ── Add all cells to notebook ──
nb['cells'].extend(new_cells)

# Save
with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Added {len(new_cells)} cells to {NOTEBOOK_PATH}")
print("Sections added: 9 (Load Full Data), 10 (Stats), 11 (18 Visualizations), 12-13 (Summary Tables)")
