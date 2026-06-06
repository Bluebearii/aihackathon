import pandas as pd
import numpy as np

# ── Load real Kaggle no-show data ──────────────────────────────────────────────
kaggle = pd.read_csv("/Users/tommynguyen/codingprojects/AIhackathon/KaggleV2-May-2016.csv")

# Standardize the no-show column to 0/1
kaggle['NO_SHOW'] = (kaggle['No-show'] == 'Yes').astype(int)

# ── Base rate ──────────────────────────────────────────────────────────────────
base_rate = kaggle['NO_SHOW'].mean()
print(f"Base no-show rate: {base_rate:.4f}")

# ── Age buckets ────────────────────────────────────────────────────────────────
kaggle['AGE_BUCKET'] = pd.cut(
    kaggle['Age'],
    bins=[0, 18, 30, 60, 120],
    labels=['<18', '18-30', '30-60', '60+']
)
age_rates = kaggle.groupby('AGE_BUCKET')['NO_SHOW'].mean()
print(f"\nNo-show rate by age:\n{age_rates}")

# ── Gender ─────────────────────────────────────────────────────────────────────
gender_rates = kaggle.groupby('Gender')['NO_SHOW'].mean()
print(f"\nNo-show rate by gender:\n{gender_rates}")

# ── Compute deltas from base rate ──────────────────────────────────────────────
print("\n── Calibrated weight adjustments (delta from base) ──")
print("\nAge weights:")
for bucket, rate in age_rates.items():
    delta = rate - base_rate
    print(f"  {bucket}: {delta:+.4f}")

print("\nGender weights:")
for gender, rate in gender_rates.items():
    delta = rate - base_rate
    print(f"  {gender}: {delta:+.4f}")
