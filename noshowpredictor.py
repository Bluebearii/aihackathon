import pandas as pd
import numpy as np
import os
from math import radians, sin, cos, sqrt, atan2
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.utils import class_weight

csv_path = "/Users/tommynguyen/codingprojects/AIhackathon/output/csv/"

# ── Load data ──────────────────────────────────────────────────────────────────
patients   = pd.read_csv(os.path.join(csv_path, "patients.csv"))
encounters = pd.read_csv(os.path.join(csv_path, "encounters.csv"))

# ── Drop BIRTHDATE from encounters (prevents column conflict) ──────────────────
encounters = encounters.drop(columns=['BIRTHDATE'], errors='ignore')

# ── Merge (only bring needed patient columns) ──────────────────────────────────
patient_cols = patients[['Id', 'BIRTHDATE', 'GENDER', 'MARITAL', 'INCOME', 'LAT', 'LON']]
df = encounters.merge(patient_cols, left_on='PATIENT', right_on='Id')

# ── Feature Engineering ────────────────────────────────────────────────────────

# Age
df['BIRTHDATE'] = pd.to_datetime(df['BIRTHDATE'], errors='coerce')
df['AGE']       = ((pd.Timestamp('today') - df['BIRTHDATE']).dt.days // 365).astype(int)

# Marital status
df['MARITAL'] = df['MARITAL'].fillna('U')

# Education (proxied from income)
df['EDUCATION'] = pd.cut(df['INCOME'], bins=3, labels=['Low', 'Medium', 'High'], duplicates='drop')

# Real distance using haversine (replace random with actual lat/lon)
HOSPITAL_LAT = 32.7767   # Dallas, TX
HOSPITAL_LON = -96.7970


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

df['DISTANCE_KM'] = df.apply(
    lambda row: haversine(row['LAT'], row['LON'], HOSPITAL_LAT, HOSPITAL_LON),
    axis=1
)

# Prior visits per patient
df = df.sort_values(['PATIENT', 'START'])
df['PRIOR_VISITS'] = df.groupby('PATIENT').cumcount()

# Day of week & month
df['START']       = pd.to_datetime(df['START'], errors='coerce')
df['DAY_OF_WEEK'] = df['START'].dt.dayofweek  # 0=Mon, 6=Sun
df['MONTH']       = df['START'].dt.month

# Encounter type
df['ENCOUNTER_TYPE'] = df['ENCOUNTERCLASS'].astype(str)

# ── Simulate No-Show Label (calibrated from real Kaggle data) ──────────────────
def no_show_prob(row):
    p = 0.2019  # base rate from real Kaggle data

    # Age (calibrated)
    if row['AGE'] < 18:    p += 0.0234
    elif row['AGE'] < 30:  p += 0.0452
    elif row['AGE'] < 60:  p -= 0.0064
    else:                  p -= 0.0498

    # Gender (calibrated)
    if row['GENDER'] == 'F':   p += 0.0012
    elif row['GENDER'] == 'M': p -= 0.0023

    # Marital status (literature-based)
    if row['MARITAL'] == 'S':   p += 0.05
    elif row['MARITAL'] == 'D': p += 0.04
    elif row['MARITAL'] == 'W': p += 0.02
    elif row['MARITAL'] == 'M': p -= 0.03
    elif row['MARITAL'] == 'U': p += 0.01

    # Distance (literature-based)
    if row['DISTANCE_KM'] > 50:   p += 0.12
    elif row['DISTANCE_KM'] > 20: p += 0.07
    elif row['DISTANCE_KM'] > 10: p += 0.03

    # Education/Income (literature-based)
    if str(row['EDUCATION']) == 'Low':      p += 0.06
    elif str(row['EDUCATION']) == 'Medium': p += 0.02
    elif str(row['EDUCATION']) == 'High':   p -= 0.04

    # Prior visits (frequent patients are more reliable)
    if row['PRIOR_VISITS'] > 10:   p -= 0.08
    elif row['PRIOR_VISITS'] > 5:  p -= 0.04
    elif row['PRIOR_VISITS'] == 0: p += 0.06

    # Day of week (Mon/Fri higher no-show)
    if row['DAY_OF_WEEK'] == 0:   p += 0.04  # Monday
    elif row['DAY_OF_WEEK'] == 4: p += 0.03  # Friday
    elif row['DAY_OF_WEEK'] == 2: p -= 0.02  # Wednesday

    # Encounter type
    enc = row['ENCOUNTER_TYPE'].lower()
    if 'wellness' in enc:    p += 0.05
    elif 'urgent' in enc:    p -= 0.10
    elif 'emergency' in enc: p -= 0.15

    return min(max(p, 0.01), 0.95)

df['NO_SHOW_PROB'] = df.apply(no_show_prob, axis=1)
df['NO_SHOW']      = (np.random.rand(len(df)) < df['NO_SHOW_PROB']).astype(int)

# ── Sanity Check ───────────────────────────────────────────────────────────────
print(df[['AGE', 'GENDER', 'MARITAL', 'EDUCATION', 'DISTANCE_KM',
          'PRIOR_VISITS', 'DAY_OF_WEEK', 'ENCOUNTER_TYPE', 'NO_SHOW']].head(10))
print(f"\nNo-show rate:  {df['NO_SHOW'].mean():.2%}")
print(f"Total records: {len(df):,}")
print(f"Age range:     {df['AGE'].min()} – {df['AGE'].max()}")
print(f"Distance range: {df['DISTANCE_KM'].min():.1f} – {df['DISTANCE_KM'].max():.1f} km")
print(f"Encounter types:\n{df['ENCOUNTER_TYPE'].value_counts()}")

# ── Prepare features for model ─────────────────────────────────────────────────
features = ['AGE', 'GENDER', 'MARITAL', 'EDUCATION', 'DISTANCE_KM',
            'PRIOR_VISITS', 'DAY_OF_WEEK', 'MONTH', 'ENCOUNTER_TYPE']
target   = 'NO_SHOW'

model_df = df[features + [target]].dropna().copy()

for col in ['GENDER', 'MARITAL', 'EDUCATION', 'ENCOUNTER_TYPE']:
    model_df[col] = LabelEncoder().fit_transform(model_df[col].astype(str))

X = model_df[features]
y = model_df[target]

# ── Train / Test Split ─────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\nTraining samples: {len(X_train):,}")
print(f"Testing samples:  {len(X_test):,}")

# ── Class balancing ────────────────────────────────────────────────────────────
classes = np.array([0, 1])
weights = class_weight.compute_class_weight(
    class_weight='balanced',
    classes=classes,
    y=y_train
)
class_weights  = dict(zip(classes, weights))
sample_weights = np.array([class_weights[label] for label in y_train])
print(f"Class weights: {class_weights}")

# ── Train Model ────────────────────────────────────────────────────────────────
print("\nTraining model...")
model = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.8,
    random_state=42
)
model.fit(X_train, y_train, sample_weight=sample_weights)
print("Done!")

# ── Evaluate ───────────────────────────────────────────────────────────────────
y_pred  = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("\n── Classification Report ──────────────────────────────")
print(classification_report(y_test, y_pred, target_names=['Show', 'No-Show']))
print(f"AUC-ROC: {roc_auc_score(y_test, y_proba):.4f}")

# ── Feature Importance ─────────────────────────────────────────────────────────
importance = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
print(f"\n── Feature Importance ─────────────────────────────────")
for feat, score in importance.items():
    bar = '█' * int(score * 100)
    print(f"  {feat:<18} {score:.4f}  {bar}")

# ── Save predictions ───────────────────────────────────────────────────────────
model_df['PREDICTED_PROB'] = model.predict_proba(model_df[features])[:, 1]
output_path = "/Users/tommynguyen/codingprojects/AIhackathon/noshow_predictions.csv"
model_df.to_csv(output_path, index=False)
print(f"\nPredictions saved to: {output_path}")
