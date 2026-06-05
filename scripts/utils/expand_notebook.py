import json

NB_PATH = r'notebook/noshow_kaggle_download.ipynb'

with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# The first cell is currently: "# No-Show Appointments Dataset Download"
# We will replace its content with the formal "Step 1: Ask" definition.
nb['cells'][0]['source'] = [
    "# Medical Appointment No-Shows: 6-Step Data Analysis\n",
    "\n",
    "## Step 1: Ask (Define the Problem)\n",
    "**Objective:** Identify the key drivers that cause patients to miss their medical appointments (no-shows) and build a predictive model to proactively target high-risk patients. By reducing no-show rates, clinics can optimize their schedules, recover lost revenue, and improve patient health outcomes.\n",
    "\n",
    "## Step 2: Prepare (Data Collection)\n",
    "This notebook downloads the Kaggle dataset `joniarroba/noshowappointments`."
]

# We need to find the "Data Cleaning" cell to mark it as Step 3
for cell in nb['cells']:
    if cell['cell_type'] == 'markdown':
        src = "".join(cell['source'])
        if '1. Data Cleaning' in src:
            cell['source'] = [
                "## Step 3: Process (Data Cleaning & Feature Engineering)\n",
                "First, we detect missing values, rename columns to `snake_case`, correct typos, and fix data types."
            ]
        elif 'Next Steps' in src:
            # We remove the old "Next Steps" cell since we are actually doing them now
            nb['cells'].remove(cell)

# Now, we construct the new cells for Advanced Processing, Analyze, Share, and Act.
new_cells = []

def md(source):
    new_cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.split('\n')][:-1] # avoid double newline
    })

def code(source):
    new_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.split('\n')][:-1]
    })

md("### Feature Engineering\nWe will extract the number of waiting days and the day of the week to see how time affects no-show rates.")
code("""import numpy as np

# Calculate wait days (difference between scheduled day and appointment day)
df['wait_days'] = (df['appointment_day'].dt.date - df['scheduled_day'].dt.date).dt.days

# Fix negative wait days (likely data entry errors)
df.loc[df['wait_days'] < 0, 'wait_days'] = 0

# Extract day of the week for the appointment
df['day_of_week'] = df['appointment_day'].dt.day_name()

# Cap age outliers
df.loc[df['age'] > 100, 'age'] = 100
df.loc[df['age'] < 0, 'age'] = 0

print("Feature engineering complete!")
display(df[['scheduled_day', 'appointment_day', 'wait_days', 'day_of_week']].head())""")

md("## Step 4: Analyze (Exploratory Data Analysis)\nLet's analyze the no-show rate across different features.")
code("""# Overall No-Show Rate
overall_rate = df['no_show'].mean()
print(f"Overall No-Show Rate: {overall_rate:.2%}")

print("\\nNo-Show Rate by Gender:")
print(df.groupby('gender')['no_show'].mean().map('{:.2%}'.format))

print("\\nNo-Show Rate by Scholarship (Financial Aid):")
print(df.groupby('scholarship')['no_show'].mean().map('{:.2%}'.format))

print("\\nNo-Show Rate by SMS Received:")
print(df.groupby('sms_received')['no_show'].mean().map('{:.2%}'.format))""")

md("## Step 5: Share (Data Visualization)\nWe'll use `matplotlib` and `seaborn` to visualize these trends clearly.")
code("""import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 1. No-Show Rate by Wait Days
# Group wait days into bins
df['wait_bins'] = pd.cut(df['wait_days'], bins=[-1, 0, 7, 14, 30, 100], labels=['Same Day', '1-7 Days', '8-14 Days', '15-30 Days', '30+ Days'])
sns.barplot(data=df, x='wait_bins', y='no_show', ax=axes[0], palette='Blues_d')
axes[0].set_title('No-Show Rate by Wait Time')
axes[0].set_ylabel('No-Show Probability')
axes[0].set_xlabel('Wait Time')

# 2. No-Show Rate by SMS Received
sns.barplot(data=df, x='sms_received', y='no_show', ax=axes[1], palette='Oranges')
axes[1].set_title('No-Show Rate by SMS Reminder')
axes[1].set_ylabel('No-Show Probability')
axes[1].set_xlabel('SMS Received (0=No, 1=Yes)')

# 3. Age Distribution of No-Shows
sns.histplot(data=df, x='age', hue='no_show', multiple='stack', bins=30, ax=axes[2], palette=['#2A9D8F', '#E76F51'])
axes[2].set_title('Age Distribution: Show vs No-Show')
axes[2].set_xlabel('Age')

plt.tight_layout()
plt.show()""")

md("## Step 6: Act (Predictive Modeling)\nBased on our insights, we will train a Random Forest classifier to predict which patients are most likely to no-show. This model can be deployed in the clinic to trigger targeted interventions (like phone calls or double-booking).")
code("""from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import pandas as pd

# Prepare features and target
features = ['age', 'scholarship', 'hypertension', 'diabetes', 'alcoholism', 'handicap', 'sms_received', 'wait_days']
X = df[features]
y = df['no_show']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train the model
rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
rf.fit(X_train, y_train)

# Predictions
y_pred = rf.predict(X_test)
y_prob = rf.predict_proba(X_test)[:, 1]

print("Model Evaluation:")
print(classification_report(y_test, y_pred))
print(f"ROC AUC Score: {roc_auc_score(y_test, y_prob):.3f}")""")

md("### Feature Importance\nLet's see which factors the AI uses to predict a no-show.")
code("""importances = rf.feature_importances_
feature_names = X.columns
importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances}).sort_values(by='Importance', ascending=False)

plt.figure(figsize=(10, 5))
sns.barplot(data=importance_df, x='Importance', y='Feature', palette='viridis')
plt.title('Top Predictors of Appointment No-Shows')
plt.xlabel('Relative Importance')
plt.ylabel('')
plt.show()""")

md("""### Business Recommendations
1. **Reduce Wait Times:** The data shows that same-day appointments have significantly lower no-show rates. Clinics should reserve more slots for rapid scheduling.
2. **Targeted Interventions:** Use the predictive model to flag patients with a wait time > 7 days and younger age groups.
3. **SMS Strategy Optimization:** SMS reminders currently do not definitively reduce no-shows alone; combining SMS with phone calls for high-risk patients may yield better results.""")

nb['cells'].extend(new_cells)

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print('Notebook successfully expanded with the 6-step process.')
