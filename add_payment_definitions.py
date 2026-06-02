"""
Adds a payment definitions cell to the top of expanded sections in cms_data_pipeline.ipynb
and relabels summary table columns for clarity.
"""
import json

NB = r"notebook/cms_data_pipeline.ipynb"

with open(NB, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# ── Find the cell index for Section 9 (Load Full Dataset) ──
insert_idx = None
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell.get('source', []))
    if '# 9. Load Full Dataset' in src:
        insert_idx = i
        break

if insert_idx is None:
    # Fallback: insert before last 30 cells
    insert_idx = max(0, len(nb['cells']) - 49)

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

# ── DEFINITIONS CELL ──
md("""---
# 📋 Payment Field Definitions — Who Pays What?

The CMS dataset contains **4 payment-related fields**. Understanding who each amount belongs to is critical:

| Field | Who Pays/Sets This | What It Means |
|-------|-------------------|---------------|
| **Avg Submitted Charge** | 🏥 **Provider** (billed amount) | The price the provider *charges* for the service. This is the provider's "sticker price" — like an MSRP. Medicare almost never pays this full amount. |
| **Avg Medicare Allowed Amount** | 🏛️ **Medicare** (approved maximum) | The maximum amount Medicare *approves* for this service based on the Medicare Fee Schedule. This is the ceiling — no one pays more than this (for participating providers). |
| **Avg Medicare Payment** | 🏛️ **Medicare** (actual payment to provider) | The amount Medicare *actually pays* the provider. Typically **80%** of the Allowed Amount. This is real money from Medicare to the provider. |
| **Avg Medicare Standardized Amount** | 🏛️ **Medicare** (geography-adjusted) | Same as Medicare Payment but adjusted to remove geographic cost differences (GPCI). Used for fair state-to-state comparisons. |

### 💰 What the **Patient** Pays (Out-of-Pocket)

The patient's cost is **NOT a separate column** in this dataset, but can be calculated:

```
Patient Cost = Medicare Allowed Amount − Medicare Payment
             ≈ 20% of the Allowed Amount (Medicare coinsurance)
```

### 📊 What the "Gap" Means

```
Gap = Submitted Charge − Medicare Payment
    = Amount the provider WRITES OFF (never collected from anyone)
```

The Gap is **NOT** what the patient pays. It is unrealized revenue — the provider billed it but neither Medicare nor the patient pays it.

### 🔑 Summary Flow

```
Provider charges $100 (Submitted Charge)
    → Medicare approves $40 (Allowed Amount)
        → Medicare pays $32 (Medicare Payment = 80% of Allowed)
        → Patient pays $8 (Coinsurance = 20% of Allowed)
    → Provider writes off $60 (Gap = Charge − Payment)
```

> **Key Insight:** The Submitted Charge is essentially meaningless for determining actual revenue. Only the Medicare Allowed Amount and Medicare Payment matter for financial planning.""")

# ── Visual comparison cell ──
md("## 💵 Payment Breakdown Visualization")

code("""# === WHO PAYS WHAT? ===
# Clear visual breakdown of the 4 payment fields

avg_charge = df['avg_submitted_charge'].mean()
avg_allowed = df['avg_medicare_allowed_amount'].mean()
avg_payment = df['avg_medicare_payment'].mean()
avg_std = df['avg_medicare_standardized_amount'].mean()
patient_cost = avg_allowed - avg_payment  # 20% coinsurance
write_off = avg_charge - avg_allowed      # provider eats this

print("=" * 65)
print("   💰 AVERAGE PAYMENT BREAKDOWN (per service)")
print("=" * 65)
print()
print(f"   🏥 Provider Charges (Submitted):     ${avg_charge:>10,.2f}")
print(f"   ─────────────────────────────────────────────────")
print(f"   🏛️  Medicare Approves (Allowed):       ${avg_allowed:>10,.2f}")
print(f"   🏛️  Medicare Pays (to Provider):       ${avg_payment:>10,.2f}  ← REAL REVENUE")
print(f"   👤 Patient Pays (20% coinsurance):    ${patient_cost:>10,.2f}  ← OUT OF POCKET")
print(f"   🏛️  Standardized Amount (geo-adj):     ${avg_std:>10,.2f}")
print(f"   ─────────────────────────────────────────────────")
print(f"   ❌ Write-Off (Charge − Allowed):       ${write_off:>10,.2f}  ← LOST REVENUE")
print(f"   ❌ Total Gap (Charge − Payment):       ${avg_charge - avg_payment:>10,.2f}")
print()
print("=" * 65)
print(f"   Provider keeps: ${avg_payment:,.2f} ({avg_payment/avg_charge*100:.1f}% of charge)")
print(f"   Patient pays:   ${patient_cost:,.2f} ({patient_cost/avg_charge*100:.1f}% of charge)")
print(f"   Written off:    ${write_off:,.2f} ({write_off/avg_charge*100:.1f}% of charge)")
print("=" * 65)""")

code("""# === VISUAL BAR: Who Pays What? ===
import plotly.graph_objects as go

avg_charge = df['avg_submitted_charge'].mean()
avg_allowed = df['avg_medicare_allowed_amount'].mean()
avg_payment = df['avg_medicare_payment'].mean()
patient_cost = avg_allowed - avg_payment
write_off = avg_charge - avg_allowed

fig = go.Figure()
fig.add_trace(go.Bar(
    name='🏛️ Medicare Pays (to Provider)', x=['Payment Breakdown'], y=[avg_payment],
    marker_color='#2A9D8F', text=f'${avg_payment:,.2f}', textposition='inside'
))
fig.add_trace(go.Bar(
    name='👤 Patient Pays (20% Coinsurance)', x=['Payment Breakdown'], y=[patient_cost],
    marker_color='#E9C46A', text=f'${patient_cost:,.2f}', textposition='inside'
))
fig.add_trace(go.Bar(
    name='❌ Provider Write-Off (Lost)', x=['Payment Breakdown'], y=[write_off],
    marker_color='#E76F51', text=f'${write_off:,.2f}', textposition='inside'
))
fig.update_layout(
    barmode='stack',
    title=f'Who Pays What? (Average per Service, Total Charge: ${avg_charge:,.2f})',
    yaxis_title='Amount ($)', yaxis_tickprefix='$',
    height=450, showlegend=True,
    legend=dict(orientation='h', yanchor='bottom', y=-0.25)
)
fig.show()""")

code("""# === PAYMENT BREAKDOWN BY TOP 10 SPECIALTIES ===

spec_pay = df.groupby('provider_specialty').agg(
    charge=('avg_submitted_charge', 'mean'),
    allowed=('avg_medicare_allowed_amount', 'mean'),
    medicare_pays=('avg_medicare_payment', 'mean'),
).sort_values('charge', ascending=False).head(10)
spec_pay['patient_pays'] = spec_pay['allowed'] - spec_pay['medicare_pays']
spec_pay['write_off'] = spec_pay['charge'] - spec_pay['allowed']

fig = go.Figure()
fig.add_trace(go.Bar(name='🏛️ Medicare Pays', y=spec_pay.index, x=spec_pay['medicare_pays'],
                     orientation='h', marker_color='#2A9D8F'))
fig.add_trace(go.Bar(name='👤 Patient Pays', y=spec_pay.index, x=spec_pay['patient_pays'],
                     orientation='h', marker_color='#E9C46A'))
fig.add_trace(go.Bar(name='❌ Write-Off', y=spec_pay.index, x=spec_pay['write_off'],
                     orientation='h', marker_color='#E76F51'))
fig.update_layout(
    barmode='stack',
    title='Who Pays What by Specialty (Top 10 Most Expensive)',
    xaxis_title='Amount ($)', xaxis_tickprefix='$',
    height=500, yaxis=dict(autorange='reversed'),
    legend=dict(orientation='h', yanchor='bottom', y=-0.2)
)
fig.show()

print("\\nBreakdown:")
for sp, row in spec_pay.iterrows():
    print(f"  {sp}:")
    print(f"    Provider charges: ${row['charge']:,.2f}")
    print(f"    Medicare pays:    ${row['medicare_pays']:,.2f} ({row['medicare_pays']/row['charge']*100:.1f}%)")
    print(f"    Patient pays:     ${row['patient_pays']:,.2f} ({row['patient_pays']/row['charge']*100:.1f}%)")
    print(f"    Write-off:        ${row['write_off']:,.2f} ({row['write_off']/row['charge']*100:.1f}%)")
    print()""")

# ── Now update the per-specialty table columns (Section 12) ──
# Find and update the Section 12 per-specialty summary cell
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell.get('source', []))
    if "# Comprehensive per-specialty stats" in src:
        nb['cells'][i]['source'] = [line + "\n" for line in """# Comprehensive per-specialty stats
# Column labels clearly show WHO pays/sets each amount
spec_summary = df.groupby('provider_specialty').agg(
    records=('provider_npi', 'count'),
    unique_providers=('provider_npi', 'nunique'),
    provider_charges=('avg_submitted_charge', 'mean'),       # What PROVIDER charges
    medicare_pays=('avg_medicare_payment', 'mean'),           # What MEDICARE pays provider
    medicare_pays_median=('avg_medicare_payment', 'median'),  # Median of what MEDICARE pays
    avg_patients=('total_patients', 'mean'),
    avg_services=('total_services', 'mean'),
).sort_values('records', ascending=False).head(25)

# Calculate derived fields
spec_summary['patient_pays'] = (
    df.groupby('provider_specialty')['avg_medicare_allowed_amount'].mean() -
    df.groupby('provider_specialty')['avg_medicare_payment'].mean()
).reindex(spec_summary.index)
spec_summary['write_off'] = spec_summary['provider_charges'] - spec_summary['medicare_pays'] - spec_summary['patient_pays']
spec_summary['efficiency'] = (spec_summary['medicare_pays'] / spec_summary['provider_charges'] * 100).round(1)

# Format
styled = spec_summary.copy()
for col in ['provider_charges', 'medicare_pays', 'medicare_pays_median', 'patient_pays', 'write_off']:
    styled[col] = styled[col].apply(lambda x: f'${x:,.2f}')
styled['efficiency'] = styled['efficiency'].apply(lambda x: f'{x}%')
styled['avg_patients'] = styled['avg_patients'].apply(lambda x: f'{x:.1f}')
styled['avg_services'] = styled['avg_services'].apply(lambda x: f'{x:.1f}')

styled.columns = ['Records', 'Providers',
                   '🏥 Provider Charges', '🏛️ Medicare Pays', '🏛️ Medicare Pays (Med)',
                   'Avg Patients', 'Avg Services',
                   '👤 Patient Pays (est)', '❌ Write-Off', 'Efficiency']
display(styled)""".split("\n")]
        break

# ── Update Section 13 per-state table ──
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell.get('source', []))
    if "# Comprehensive per-state stats" in src:
        nb['cells'][i]['source'] = [line + "\n" for line in """# Comprehensive per-state stats
# Column labels clearly show WHO pays/sets each amount
state_summary = df.groupby('provider_state').agg(
    records=('provider_npi', 'count'),
    unique_providers=('provider_npi', 'nunique'),
    unique_specialties=('provider_specialty', 'nunique'),
    provider_charges=('avg_submitted_charge', 'mean'),
    medicare_pays=('avg_medicare_payment', 'mean'),
    avg_patients=('total_patients', 'mean'),
    allowed=('avg_medicare_allowed_amount', 'mean'),
).sort_values('records', ascending=False)

state_summary['patient_pays'] = state_summary['allowed'] - state_summary['medicare_pays']
state_summary['write_off'] = state_summary['provider_charges'] - state_summary['allowed']
state_summary['efficiency'] = (state_summary['medicare_pays'] / state_summary['provider_charges'] * 100).round(1)

styled_state = state_summary.drop(columns=['allowed']).copy()
for col in ['provider_charges', 'medicare_pays', 'patient_pays', 'write_off']:
    styled_state[col] = styled_state[col].apply(lambda x: f'${x:,.2f}')
styled_state['efficiency'] = styled_state['efficiency'].apply(lambda x: f'{x}%')
styled_state['avg_patients'] = styled_state['avg_patients'].apply(lambda x: f'{x:.1f}')

styled_state.columns = ['Records', 'Providers', 'Specialties',
                         '🏥 Provider Charges', '🏛️ Medicare Pays',
                         'Avg Patients',
                         '👤 Patient Pays (est)', '❌ Write-Off', 'Efficiency']
display(styled_state)""".split("\n")]
        break

# Insert definition cells right before Section 9
for i, cell in enumerate(new_cells):
    nb['cells'].insert(insert_idx + i, cell)

with open(NB, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Added {len(new_cells)} definition cells at position {insert_idx}")
print("Updated Section 12 and 13 tables with clear payment labels")
