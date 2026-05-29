# Healthcare Data Science & Dashboard Tool Instructions

This guide explains the recommended tools, libraries, setup steps, and workflow for working with healthcare datasets, generating dashboards, building charts, creating business insights, and preparing for a future AI chatbot/RAG application.

Project goal:

Build a cost-effective healthcare analytics and AI prototype focused on:

- Patient access
- No-show prediction
- Prior authorization support
- Revenue cycle management
- Claims and reimbursement insights
- Patient experience improvement
- Future AI chatbot integration

---

## 1. Recommended Main Stack

Use this stack first:

```text
Python
Pandas
DuckDB
PostgreSQL
Streamlit
Plotly
Scikit-learn
XGBoost
Power BI
GitHub
```

Why this stack:

- Low cost
- Beginner-friendly
- Strong for data science
- Good for dashboards
- Good for healthcare business insights
- Easy to expand into a full AI healthcare app later

---

## 2. Tool Purpose Summary

| Tool | Purpose | Why it is useful |
|---|---|---|
| Python | Main programming language | Best for data science, ML, automation, and AI |
| Pandas | Data cleaning and analysis | Easy for CSV, Excel, healthcare tables, and feature engineering |
| Polars | Faster dataframe processing | Useful when datasets become larger |
| DuckDB | Local SQL analytics | Query large CSV/Parquet files without setting up a full database |
| PostgreSQL | App database | Good for production-style app development |
| pgvector | Vector search inside PostgreSQL | Useful for future RAG chatbot |
| Jupyter Notebook | Research notebooks | Best for experimenting and documenting analysis |
| Google Colab | Cloud notebook | Free/low-cost notebook environment without local setup |
| Streamlit | Python dashboard app | Fastest way to build interactive data dashboards |
| Plotly | Interactive charts | Good for dashboards and business reports |
| Matplotlib | Basic charts | Reliable for notebooks and reports |
| Seaborn | Statistical charts | Good for correlation, distributions, and exploratory data analysis |
| Scikit-learn | Machine learning | Good for no-show prediction, risk scoring, and classification |
| XGBoost | Advanced ML model | Strong for tabular healthcare prediction tasks |
| LightGBM | Fast gradient boosting | Good for large tabular datasets |
| SHAP | Model explainability | Explains why a model predicted high risk |
| Power BI | Business dashboard | Professional dashboard for managers/executives |
| Metabase | Open-source BI dashboard | Good for internal analytics dashboards |
| Apache Superset | Advanced open-source BI | Good for enterprise-style dashboards |
| FastAPI | Backend API | Good for connecting ML models, dashboards, and frontend apps |
| Next.js | Final frontend app | Good for polished healthcare app UI |
| LangChain / LlamaIndex | RAG and AI workflow | Useful for future chatbot and document Q&A |
| Chroma / FAISS | Vector database | Useful for document search and chatbot memory |
| OpenAI / Gemini | AI model APIs | Useful for chatbot, summarization, and workflow automation |

---

## 3. Recommended Project Phases

### Phase 1: Data Research and Cleaning

Use:

```text
Python
Pandas
DuckDB
Jupyter Notebook
Google Colab
```

Tasks:

- Load healthcare datasets
- Clean missing values
- Standardize column names
- Convert dates
- Remove duplicates
- Create useful features
- Export cleaned data as CSV or Parquet

Example use cases:

- Clean CMS payment data
- Analyze no-show appointment data
- Prepare HCAHPS patient experience data
- Prepare claims data
- Prepare provider directory data

---

### Phase 2: Exploratory Data Analysis

Use:

```text
Pandas
DuckDB
Matplotlib
Seaborn
Plotly
```

Business questions to answer:

- Which appointment types have the highest no-show rate?
- Which providers have the longest wait time?
- Which payers have the highest denial rate?
- Which procedures have the largest charge vs reimbursement gap?
- Which hospitals have lower patient experience scores?
- Which ZIP codes may have provider access gaps?

Recommended notebook structure:

```text
1. Business problem
2. Data source
3. Data cleaning
4. Exploratory analysis
5. Charts
6. Key findings
7. Business recommendations
```

---

### Phase 3: Machine Learning

Use:

```text
Scikit-learn
XGBoost
LightGBM
SHAP
Joblib
```

Good first models:

1. No-show prediction
2. Claim denial risk prediction
3. Reimbursement prediction
4. Prior authorization delay risk
5. Patient payment risk
6. Patient satisfaction score analysis

Recommended model workflow:

```text
1. Define target variable
2. Select features
3. Split train/test data
4. Train baseline model
5. Train stronger model
6. Evaluate model
7. Explain model with SHAP
8. Save model
9. Use model in dashboard/app
```

Example evaluation metrics:

| Problem type | Metrics |
|---|---|
| Classification | Accuracy, Precision, Recall, F1, ROC-AUC |
| Regression | MAE, RMSE, R² |
| Business risk scoring | Recall, Precision, Top-risk capture rate |

---

### Phase 4: Interactive Dashboard

Use:

```text
Streamlit
Plotly
Pandas
DuckDB
Scikit-learn
```

Recommended Streamlit dashboard pages:

```text
Dashboard Overview
Patient Access
No-Show Risk
Insurance Verification
Prior Authorization
Revenue Cycle
Claims
Patient Experience
AI Assistant Placeholder
Settings
```

Good dashboard components:

- KPI cards
- Search filters
- Date filters
- Provider filters
- Payer filters
- Status filters
- Data tables
- Line charts
- Bar charts
- Pie charts
- Risk score cards
- Download CSV button

Example KPIs:

```text
Total Appointments
No-Show Rate
Average Wait Time
Pending Prior Authorizations
Claim Denial Rate
Average Days in A/R
Estimated Revenue Leakage
Patient Satisfaction Score
```

---

### Phase 5: Business Dashboard

Use:

```text
Power BI
PostgreSQL
CSV
Parquet
Excel
```

Power BI is best for professional business dashboards.

Recommended Power BI pages:

1. Executive Overview
2. Patient Access
3. No-Show Analysis
4. Prior Authorization
5. Revenue Cycle
6. Claim Denials
7. Patient Experience
8. Provider/Location Analysis

Best for:

- Portfolio presentation
- Business stakeholder reporting
- Healthcare manager dashboard
- Executive summary

---

### Phase 6: Backend API

Use:

```text
FastAPI
PostgreSQL
SQLAlchemy
Pydantic
Uvicorn
```

Use FastAPI when you want your dashboard or web app to connect to backend services.

Recommended backend modules:

```text
auth
users
patients
appointments
insurance
prior_authorization
claims
tasks
analytics
chatbot
```

Example API routes:

```text
GET /patients
GET /patients/{id}
POST /patients
PUT /patients/{id}
DELETE /patients/{id}

GET /appointments
POST /appointments
PUT /appointments/{id}

GET /prior-auth
POST /prior-auth
POST /prior-auth/{id}/generate-draft

GET /claims
POST /claims/{id}/predict-denial-risk

POST /chat/message
GET /analytics/dashboard
```

---

### Phase 7: Future AI Chatbot / RAG

Use:

```text
OpenAI
Google Gemini
LangChain
LlamaIndex
Chroma
FAISS
pgvector
Sentence Transformers
```

Use RAG for:

- Patient FAQs
- Prior authorization policies
- Billing rules
- CMS coverage documents
- Claim denial policies
- Internal workflow documents

Recommended chatbot modes:

1. Patient Mode
2. Staff Mode
3. Admin Mode

Example patient questions:

```text
Can I book an appointment?
Do I need a referral?
What does prior authorization mean?
Why did I receive this bill?
Can I reschedule my appointment?
```

Example staff questions:

```text
Which patients are high no-show risk today?
Which prior auth cases are missing documents?
Why is this claim high denial risk?
Generate a prior authorization draft.
Summarize this patient access case.
```

Important safety rules:

- Do not diagnose patients
- Do not replace a doctor
- Do not hallucinate insurance rules
- Use retrieved documents when available
- Always show uncertainty
- Require human review for clinical, billing, and authorization decisions
- Do not use real PHI in public demos

---

## 4. Recommended Folder Structure

```text
healthcare-ai-analytics/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_no_show_model.ipynb
│   ├── 04_claim_denial_model.ipynb
│   └── 05_business_insights.ipynb
│
├── src/
│   ├── data/
│   │   ├── load_data.py
│   │   ├── clean_data.py
│   │   └── feature_engineering.py
│   │
│   ├── models/
│   │   ├── train_no_show_model.py
│   │   ├── train_claim_model.py
│   │   └── predict.py
│   │
│   ├── dashboards/
│   │   └── streamlit_app.py
│   │
│   ├── api/
│   │   └── main.py
│   │
│   └── utils/
│       └── helpers.py
│
├── models/
│   ├── no_show_model.pkl
│   └── claim_denial_model.pkl
│
├── reports/
│   ├── charts/
│   └── business_summary.md
│
├── requirements.txt
├── README.md
└── tools_instruction.md
```

---

## 5. Virtual Environment Setup

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on Mac/Linux:

```bash
source venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install all libraries:

```bash
pip install -r requirements.txt
```

Save installed packages:

```bash
pip freeze > requirements.txt
```

---

## 6. Recommended requirements.txt

Use this for your virtual environment:

```txt
# Core data science
pandas
numpy
polars
duckdb
pyarrow
fastparquet

# Notebooks / development
jupyter
notebook
ipykernel

# Data visualization
matplotlib
seaborn
plotly
altair

# Dashboard app
streamlit
streamlit-option-menu
streamlit-folium

# Machine learning
scikit-learn
xgboost
lightgbm
shap
joblib

# Database / SQL
SQLAlchemy
psycopg2-binary
alembic

# API / backend
fastapi
uvicorn[standard]
pydantic
python-multipart
python-dotenv
requests
httpx

# AI / LLM / RAG future use
openai
google-generativeai
langchain
langchain-openai
langchain-community
langchain-text-splitters
chromadb
faiss-cpu
sentence-transformers
tiktoken

# File handling
openpyxl
xlsxwriter
python-docx
pypdf

# Healthcare / FHIR data support
fhir.resources

# Utilities
tqdm
python-dateutil
```

---

## 7. Recommended Data Sources

Use these free or low-cost healthcare data sources:

```text
CMS Medicare Physician & Other Practitioners
CMS HCAHPS / Care Compare
AHRQ HCUP / HCUPnet
NPPES / NPI Registry
CMS Open Payments
CMS Coverage API
Transparency in Coverage files
CMS SynPUF
Synthea
MIMIC-IV, if credentialed access is approved
```

Recommended starting data:

1. No-show appointment dataset
2. CMS Medicare payment/utilization data
3. HCAHPS patient experience data
4. NPPES provider directory
5. CMS SynPUF synthetic claims data
6. Synthea synthetic patient records
7. CMS Coverage API or coverage documents

---

## 8. Recommended Business Insights

### Patient Access

Analyze:

- No-show rate
- Wait time
- Appointment demand
- Reminder effectiveness
- Referral delay
- Insurance verification delay

Possible insights:

```text
Patients with longer wait times are more likely to miss appointments.
Reminder messages reduce no-show risk.
Certain appointment types have higher cancellation rates.
Some provider locations have access gaps.
```

---

### Prior Authorization

Analyze:

- Prior auth turnaround time
- Approval rate
- Denial rate
- Missing documentation
- Payer response delay
- Service types requiring authorization

Possible insights:

```text
Missing documentation is a major cause of prior authorization delay.
Some payers have slower authorization response times.
Certain services require more review and staff attention.
```

---

### Revenue Cycle

Analyze:

- Claim denial rate
- Days in A/R
- Reimbursement gap
- Patient balance
- Coding/documentation issues
- Payer-level payment delay

Possible insights:

```text
Claims with missing documentation are more likely to be denied.
Some payers have longer reimbursement cycles.
Certain procedure codes have high denial risk.
High patient balances may require earlier cost transparency.
```

---

### Patient Experience

Analyze:

- Hospital rating
- Communication score
- Discharge instruction score
- Cleanliness score
- Overall satisfaction
- Relationship between delays and satisfaction

Possible insights:

```text
Poor communication scores may indicate need for better patient navigation.
Better discharge instructions may improve patient experience.
Operational delays may reduce satisfaction scores.
```

---

## 9. Recommended Dashboard KPIs

Use these KPIs for your dashboards:

```text
Total Appointments
No-Show Rate
Average Appointment Wait Time
Insurance Verification Completion Rate
Referral Completion Rate
Prior Authorization Approval Rate
Prior Authorization Denial Rate
Average Prior Authorization Turnaround Time
Claim Denial Rate
Average Days in A/R
Expected Reimbursement
Submitted Charges
Revenue Leakage Estimate
Patient Balance
Patient Satisfaction Score
```

---

## 10. Recommended Chart Types

| Business question | Best chart |
|---|---|
| Trend over time | Line chart |
| Compare categories | Bar chart |
| Show percentage breakdown | Pie or donut chart |
| Show distribution | Histogram |
| Compare two numeric variables | Scatter plot |
| Show risk ranking | Horizontal bar chart |
| Show location differences | Map |
| Show KPI summary | Metric cards |

Examples:

```text
No-show rate by appointment type → Bar chart
Claim denial rate over time → Line chart
Prior auth status breakdown → Donut chart
Provider access by ZIP code → Map
Reimbursement vs submitted charge → Scatter plot
Top denial reasons → Horizontal bar chart
```

---

## 11. Recommended Streamlit App Structure

Create a file named:

```text
app.py
```

Basic structure:

```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="CareFlow AI Analytics",
    page_icon="🏥",
    layout="wide"
)

st.title("CareFlow AI Analytics Dashboard")

page = st.sidebar.selectbox(
    "Navigation",
    [
        "Overview",
        "Patient Access",
        "No-Show Risk",
        "Prior Authorization",
        "Revenue Cycle",
        "Claims",
        "Patient Experience",
        "AI Assistant"
    ]
)

if page == "Overview":
    st.header("Executive Overview")

elif page == "Patient Access":
    st.header("Patient Access")

elif page == "No-Show Risk":
    st.header("No-Show Risk")

elif page == "Prior Authorization":
    st.header("Prior Authorization")

elif page == "Revenue Cycle":
    st.header("Revenue Cycle")

elif page == "Claims":
    st.header("Claims")

elif page == "Patient Experience":
    st.header("Patient Experience")

elif page == "AI Assistant":
    st.header("AI Assistant")
```

Run Streamlit:

```bash
streamlit run app.py
```

---

## 12. Recommended Power BI Workflow

1. Download dataset
2. Clean dataset in Python or Power Query
3. Load data into Power BI
4. Create relationships between tables
5. Create DAX measures
6. Build dashboard pages
7. Add slicers and filters
8. Publish or export report

Useful Power BI dashboard pages:

```text
Executive Overview
Patient Access
No-Show Risk
Prior Authorization
Revenue Cycle
Patient Experience
Provider Access
```

Example DAX measures:

```DAX
No Show Rate = DIVIDE([No Show Count], [Total Appointments])

Claim Denial Rate = DIVIDE([Denied Claims], [Total Claims])

Average Days in AR = AVERAGE(Claims[DaysInAR])

Prior Auth Approval Rate = DIVIDE([Approved Prior Auths], [Total Prior Auths])
```

---

## 13. Recommended ML Features

### No-Show Prediction Features

```text
Patient age
Appointment type
Appointment day of week
Scheduled lead time
Previous no-show history
Reminder sent
Insurance type
Provider
Department
Distance/location
Time of appointment
```

Target:

```text
No-show: yes/no
```

---

### Claim Denial Prediction Features

```text
Payer
Procedure code
Diagnosis code
Billed amount
Expected reimbursement
Provider specialty
Missing documentation flag
Eligibility verified flag
Prior authorization required flag
Prior authorization completed flag
Days since service
Claim type
```

Target:

```text
Denied: yes/no
```

---

### Prior Authorization Delay Risk Features

```text
Payer
Service type
Required documents count
Missing documents count
Urgency level
Provider specialty
Previous payer turnaround time
Submission completeness
Clinical note length
Diagnosis category
```

Target:

```text
Delayed: yes/no
```

---

## 14. Model Saving and Loading

Save a trained model:

```python
import joblib

joblib.dump(model, "models/no_show_model.pkl")
```

Load a trained model:

```python
model = joblib.load("models/no_show_model.pkl")
```

Use model prediction:

```python
prediction = model.predict(input_data)
probability = model.predict_proba(input_data)
```

---

## 15. Cost-Effective Hosting Options

| Need | Recommended option |
|---|---|
| Static frontend | Vercel |
| Streamlit dashboard | Streamlit Community Cloud |
| Backend API | Render, Railway, Fly.io |
| PostgreSQL database | Supabase, Neon, Railway |
| File storage | Supabase Storage, AWS S3 free/low tier |
| Full app prototype | Render + Supabase + Vercel |
| Portfolio dashboard | GitHub + Power BI screenshots + Streamlit demo |

Recommended cheap setup:

```text
Frontend: Vercel
Backend: FastAPI on Render
Database: Supabase PostgreSQL
Dashboard: Streamlit Community Cloud
Code: GitHub
```

---

## 16. Healthcare Privacy Rules

For demo and portfolio work:

- Use synthetic data whenever possible
- Do not use real patient names
- Do not use real DOBs
- Do not use real insurance IDs
- Do not upload real PHI into public AI tools
- Do not publish private medical data
- Use de-identified or public datasets
- Add a disclaimer if using synthetic data

Recommended disclaimer:

```text
This project uses public and/or synthetic healthcare data for educational and demonstration purposes only. It is not connected to real patient records and should not be used for medical diagnosis, treatment decisions, or production billing without proper validation, security, and compliance review.
```

---

## 17. Recommended Build Order

Build in this order:

```text
1. Create project folder
2. Create virtual environment
3. Install requirements.txt
4. Download first dataset
5. Clean dataset in notebook
6. Create first charts
7. Write first business insights
8. Train first simple model
9. Build Streamlit dashboard
10. Add filters and KPI cards
11. Add model prediction page
12. Build Power BI report
13. Add FastAPI backend
14. Add PostgreSQL database
15. Add AI chatbot placeholder
16. Add RAG later
```

---

## 18. Best First Project Recommendation

Start with:

```text
Patient No-Show Prediction + Patient Access Dashboard
```

Why:

- Easy to understand
- Good business value
- Good patient care impact
- Good for ML
- Good for dashboard
- Easy to explain in interviews

Main features:

```text
Upload appointment data
Clean and analyze no-show patterns
Show no-show rate by appointment type
Show no-show risk by wait time
Predict high-risk patients
Recommend reminder strategy
Display dashboard in Streamlit
Export business report
```

Then add:

```text
Revenue Cycle Claim Denial Risk Dashboard
```

Then add:

```text
Prior Authorization RAG Assistant
```

---

## 19. Example Business Insight Format

Use this format when presenting insights:

```text
Finding:
Patients with longer scheduling lead time have a higher no-show rate.

Evidence:
The no-show rate increased when appointments were scheduled more than 14 days in advance.

Business impact:
Missed appointments reduce provider productivity, delay patient care, and create revenue loss.

Recommendation:
Send additional reminders for high-risk appointments and offer earlier appointment slots when available.

Expected outcome:
Lower no-show rate, better patient access, and improved clinic utilization.
```

---

## 20. Final Recommended Path

Use this roadmap:

```text
Step 1: Learn dataset with Python + Pandas
Step 2: Query larger files with DuckDB
Step 3: Create charts with Plotly
Step 4: Build a Streamlit dashboard
Step 5: Train ML model with Scikit-learn/XGBoost
Step 6: Create professional Power BI dashboard
Step 7: Store data in PostgreSQL
Step 8: Add FastAPI backend
Step 9: Build final web app with Next.js
Step 10: Add AI chatbot and RAG later
```

Best starting combination:

```text
Python + Pandas + DuckDB + Streamlit + Plotly + Scikit-learn + Power BI
```

Best future application stack:

```text
Next.js + FastAPI + PostgreSQL + pgvector + LangChain + OpenAI/Gemini + Recharts
```
