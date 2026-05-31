# 🏥 CareFlow AI

An intelligent healthcare operations platform designed to improve patient access, prior authorization, and revenue cycle management. Built with Python, PostgreSQL, and AI-ready architecture.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup Guide](#setup-guide)
  - [Step 1: Clone the Repository](#step-1-clone-the-repository)
  - [Step 2: Create a Python Virtual Environment](#step-2-create-a-python-virtual-environment)
  - [Step 3: Activate the Virtual Environment](#step-3-activate-the-virtual-environment)
  - [Step 4: Install Python Packages](#step-4-install-python-packages)
  - [Step 5: Register the Jupyter Kernel](#step-5-register-the-jupyter-kernel)
  - [Step 6: Install PostgreSQL](#step-6-install-postgresql)
  - [Step 7: Verify PostgreSQL is Running](#step-7-verify-postgresql-is-running)
  - [Step 8: Test Database Connection](#step-8-test-database-connection)
  - [Step 9: Configure Database Credentials](#step-9-configure-database-credentials)
- [Importing CMS Medicare Data](#importing-cms-medicare-data)
  - [Option A: Full Import (1.5M Records via Script)](#option-a-full-import-15m-records-via-script)
  - [Option B: Sample Import (10K Records via Notebook)](#option-b-sample-import-10k-records-via-notebook)
- [Using the Jupyter Notebook](#using-the-jupyter-notebook)
- [Database Schema](#database-schema)
  - [Column Reference](#column-reference)
- [Data Source](#data-source)
- [Environment Variables](#environment-variables)
- [Common Issues & Troubleshooting](#common-issues--troubleshooting)
- [What's Next](#whats-next)

---

## Overview

CareFlow AI is a healthcare operations dashboard that uses real CMS (Centers for Medicare & Medicaid Services) data to power features like:

- **Patient Access** — Appointment scheduling, insurance verification, referral tracking
- **Prior Authorization** — Case management, documentation review, payer rule matching
- **Revenue Cycle Management** — Claim review, denial risk prediction, payment tracking
- **AI Assistant** — Chatbot for patients and staff (future integration)

This repository contains the **data pipeline** that fetches Medicare provider data from the CMS API and imports it into a PostgreSQL database.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.12+ |
| **Database** | PostgreSQL 17/18 |
| **ORM** | SQLAlchemy |
| **DB Driver** | psycopg2-binary |
| **Data Processing** | pandas, numpy, polars |
| **Visualization** | plotly, matplotlib, seaborn, altair |
| **API Framework** | FastAPI (future) |
| **AI/LLM** | OpenAI, LangChain, ChromaDB (future) |
| **Notebook** | Jupyter |
| **Dashboard** | Streamlit (future) |

---

## Project Structure

```
aihackathon/
├── .git/                        # Git repository
├── .gitignore                   # Ignores venv, data, .env, caches, etc.
├── Document/
│   ├── instruction_app.txt      # Full application specification
│   └── api.txt                  # CMS API endpoint reference
├── cms_data_pipeline.ipynb      # Jupyter notebook for data exploration & visualization
├── import_all_cms_data.py       # Standalone script to import 1.5M records into PostgreSQL
├── main.py                      # Application entry point (placeholder)
├── requirements.txt             # All Python dependencies
├── venv/                        # Python virtual environment (not committed)
└── README.md                    # This file
```

---

## Prerequisites

Before starting, make sure you have:

1. **Python 3.12+** installed
   - Check: `python --version`
   - Download: https://www.python.org/downloads/

2. **Git** installed
   - Check: `git --version`
   - Download: https://git-scm.com/downloads

3. **PostgreSQL 17 or 18** (installed in Step 6 below)

4. **VS Code** (recommended) with the **Jupyter** extension installed

---

## Setup Guide

### Step 1: Clone the Repository

```powershell
cd C:\Users\YourName\Desktop\CodeWorld
git clone https://github.com/Bluebearii/aihackathon.git
cd aihackathon
```

Or if you already have the project folder, navigate to it:

```powershell
cd C:\Users\YourName\OneDrive\Desktop\CodeWorld\aihackathon
```

---

### Step 2: Create a Python Virtual Environment

A virtual environment isolates this project's packages from your system Python. This prevents dependency conflicts.

```powershell
python -m venv venv
```

This creates a `venv/` folder in your project directory. It contains its own Python interpreter and `pip`.

> ⚠️ The `venv/` folder is in `.gitignore` — it will NOT be committed to Git. Each developer creates their own.

---

### Step 3: Activate the Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\activate
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
source venv/bin/activate
```

After activation, your terminal prompt will show `(venv)` at the beginning:
```
(venv) PS C:\...\aihackathon>
```

> 💡 You must activate the venv **every time** you open a new terminal to work on this project.

---

### Step 4: Install Python Packages

With the virtual environment activated, install all dependencies:

```powershell
pip install -r requirements.txt
```

This installs **~250 packages** including pandas, SQLAlchemy, plotly, scikit-learn, LangChain, and more. It may take **5–10 minutes** on the first install.

**Verify the installation:**
```powershell
pip list | Measure-Object -Line
```
You should see approximately **250+ packages**.

**Optional — upgrade pip:**
```powershell
python -m pip install --upgrade pip
```

---

### Step 5: Register the Jupyter Kernel

This step registers your virtual environment as a Jupyter kernel so VS Code's notebook interface can find it:

```powershell
python -m ipykernel install --user --name=careflow_venv --display-name="Python (CareFlow AI)"
```

**After this, when opening a `.ipynb` file in VS Code:**
1. Click **"Select Kernel"** in the top-right of the notebook
2. Choose **"Python Environments..."**
3. Select **"Python (CareFlow AI)"**

---

### Step 6: Install PostgreSQL

PostgreSQL is a system-level database server (NOT installed inside the venv). The Python driver `psycopg2-binary` (already installed in Step 4) connects Python to PostgreSQL.

#### Option A: Install via winget (recommended)

```powershell
winget install PostgreSQL.PostgreSQL.17
```

This launches a GUI installer. Follow these steps:

1. **Click through the setup wizard** using default settings
2. **Set the superuser password** — choose something simple like `postgres` and **remember it**
3. **Keep the default port** — usually `5432` (or `5433` if you have an older version)
4. Click **Next → Install → Finish**
5. When asked about **Stack Builder**, uncheck/skip it — you don't need it

#### Option B: Manual download

1. Go to https://www.postgresql.org/download/windows/
2. Download the installer for PostgreSQL 17
3. Follow the same steps as above

> 💡 PostgreSQL runs as a Windows service automatically after installation. It starts when Windows boots.

---

### Step 7: Verify PostgreSQL is Running

Check that the PostgreSQL service is active:

```powershell
Get-Service -Name "postgresql*"
```

You should see something like:
```
Name               Status  DisplayName
----               ------  -----------
postgresql-x64-17  Running postgresql-x64-17
```

If the status is `Stopped`, start it:
```powershell
Start-Service -Name "postgresql-x64-17"
```

---

### Step 8: Test Database Connection

Run this command to verify Python can connect to PostgreSQL (replace the password and port if different):

```powershell
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, database='postgres', user='postgres', password='postgres'); print('Connection successful!'); conn.close()"
```

**If you get a password error**, try port `5433` (common when multiple PostgreSQL versions are installed):

```powershell
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5433, database='postgres', user='postgres', password='postgres'); print('Connection successful!'); conn.close()"
```

**If you forgot your password**, you can reset it:
1. Find `pg_hba.conf` in your PostgreSQL data directory (e.g., `C:\Program Files\PostgreSQL\17\data\`)
2. Change the `md5` or `scram-sha-256` entries to `trust` temporarily
3. Restart the PostgreSQL service
4. Connect and run: `ALTER USER postgres WITH PASSWORD 'newpassword';`
5. Change `pg_hba.conf` back to `scram-sha-256` and restart

---

### Step 9: Configure Database Credentials

The database connection is configured in two places. Update both if your port or password differs from the defaults:

#### In `import_all_cms_data.py` (lines 21–26):
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,              # ← your PostgreSQL port
    'database': 'careflow_ai',
    'user': 'postgres',
    'password': 'postgres',    # ← your PostgreSQL password
}
```

#### In `cms_data_pipeline.ipynb` (Section 2.1 — Configuration cell):
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,              # ← same port as above
    'database': 'careflow_ai',
    'user': 'postgres',
    'password': 'postgres',    # ← same password as above
}
```

> ⚠️ Never commit passwords to Git. The `.env` file (generated by the notebook) is already in `.gitignore`.

---

## Importing CMS Medicare Data

### Option A: Full Import (1.5M Records via Script)

This is the recommended method for importing a large amount of data. The script streams data from the CMS API directly into PostgreSQL in batches — it uses minimal memory.

```powershell
# Make sure venv is activated
.\venv\Scripts\activate

# Run the import script
python import_all_cms_data.py
```

**What this does:**
1. Creates the `careflow_ai` database (if it doesn't exist)
2. Drops and recreates the `cms_medicare_providers` table
3. Fetches 1,500,000 records from the CMS API in batches of 5,000
4. Converts all column names from CMS abbreviations to human-readable names
5. Inserts data into PostgreSQL with proper data types
6. Creates indexes for fast querying

**Expected output:**
```
[17:23:44] ============================================================
[17:23:44] CareFlow AI - Full CMS Medicare Data Import
[17:23:44] ============================================================
[17:23:45] Connected to PostgreSQL: careflow_ai @ port 5433
[17:23:45] Creating table schema...
[17:23:45] Table 'cms_medicare_providers' created with indexes.
[17:23:45] Fetching 1,500,000 records from CMS API (batch size: 5,000)
[17:23:45] ------------------------------------------------------------
[17:23:47]   Batch     1 | Imported:        5,000 | Elapsed:       2s | Rate:  2,500 rec/s
[17:23:49]   Batch     2 | Imported:       10,000 | Elapsed:       4s | Rate:  2,500 rec/s
...
[17:40:34]   Batch   300 | Imported:    1,500,000 | Elapsed:    1010s | Rate:  1,486 rec/s
[17:40:34] Reached target of 1,500,000 records. Stopping.
[17:40:34] ============================================================
[17:40:34] IMPORT COMPLETE
[17:40:34]   Total records imported: 1,500,000
[17:40:34]   Total time: 16.8 minutes
[17:40:34]   Average rate: 1,486 records/sec
[17:40:34] ============================================================
```

**To change the number of records**, edit `TOTAL_RECORDS` in `import_all_cms_data.py`:
```python
TOTAL_RECORDS = 1_500_000   # Change this to any number, or None for ALL (~10M+)
```

---

### Option B: Sample Import (10K Records via Notebook)

For quick exploration and visualization, the Jupyter notebook fetches a smaller sample:

1. Open `cms_data_pipeline.ipynb` in VS Code
2. Select the **"Python (CareFlow AI)"** kernel
3. Run cells from **Section 1** through **Section 4** sequentially

The notebook fetches 10,000 records by default and provides interactive charts.

> ⚠️ **Do NOT run Section 4.3 (Create Table Schema) in the notebook if you've already imported data via the script.** That cell drops and recreates the table, which erases all data.

---

## Using the Jupyter Notebook

The notebook `cms_data_pipeline.ipynb` is organized into 8 sections:

| Section | What it Does | Safe to Re-run? |
|---------|-------------|-----------------|
| **1. Setup & Imports** | Loads libraries | ✅ Always |
| **2.1 Configuration** | Sets API URL, DB credentials, batch size | ✅ Always |
| **2.2 Column Mapping** | Defines CMS → human-readable rename map | ✅ Always |
| **2.3 Sample Fetch** | Fetches 5 records to preview schema | ✅ Always |
| **2.4 Full Fetch** | Fetches 10K records into pandas DataFrame | ✅ Always |
| **3. Exploration** | Data stats, missing values, distributions | ✅ Always |
| **4.2 Create Database** | Creates `careflow_ai` DB if not exists | ✅ Safe |
| **4.3 Create Table** | ⚠️ DROPS and recreates the table | ⛔ Only if re-importing |
| **4.4 Import to DB** | Inserts DataFrame into PostgreSQL | ⚠️ May duplicate rows |
| **4.5 Verify** | Checks row count | ✅ Always |
| **5. Visualizations** | Charts and plots | ✅ Always |
| **6. SQL Queries** | Queries PostgreSQL directly | ✅ Always (uses full dataset) |
| **7. Save Parquet** | Exports to local file | ✅ Always |
| **8. Generate .env** | Creates .env file for backend | ✅ Always |

---

## Database Schema

The `cms_medicare_providers` table stores Medicare provider service data with clean, human-readable column names:

```sql
CREATE TABLE cms_medicare_providers (
    id                                SERIAL PRIMARY KEY,

    -- Provider Identification
    provider_npi                      VARCHAR(20),
    provider_last_or_org_name         VARCHAR(255),
    provider_first_name               VARCHAR(100),
    provider_middle_initial           VARCHAR(10),
    provider_credentials              VARCHAR(50),
    provider_entity_type              VARCHAR(5),

    -- Provider Address
    provider_street_address_1         VARCHAR(255),
    provider_street_address_2         VARCHAR(255),
    provider_city                     VARCHAR(100),
    provider_state                    VARCHAR(5),
    provider_state_fips               VARCHAR(5),
    provider_zip_code                 VARCHAR(10),
    provider_ruca_code                VARCHAR(10),
    provider_rural_urban_description  TEXT,
    provider_country                  VARCHAR(5),

    -- Provider Classification
    provider_specialty                VARCHAR(255),
    medicare_participating            VARCHAR(5),
    provider_gender                   VARCHAR(5),

    -- Service / Procedure
    procedure_code                    VARCHAR(20),
    procedure_description             TEXT,
    is_drug_service                   VARCHAR(5),
    place_of_service                  VARCHAR(5),

    -- Utilization Metrics
    total_patients                    INTEGER,
    total_services                    NUMERIC(15, 2),
    total_patient_day_services        NUMERIC(15, 2),

    -- Payment Metrics
    avg_submitted_charge              NUMERIC(15, 2),
    avg_medicare_allowed_amount       NUMERIC(15, 2),
    avg_medicare_payment              NUMERIC(15, 2),
    avg_medicare_standardized_amount  NUMERIC(15, 2),

    -- Metadata
    imported_at                       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes** (for fast queries):
- `provider_npi` — lookup by National Provider Identifier
- `provider_state` — filter by state
- `provider_specialty` — filter by specialty
- `procedure_code` — filter by HCPCS/CPT code
- `provider_city, provider_state` — geographic searches

### Column Reference

| Category | Clean Name | CMS Original | Description |
|----------|-----------|--------------|-------------|
| **ID** | `provider_npi` | Rndrng_NPI | National Provider Identifier (unique 10-digit) |
| **ID** | `provider_last_or_org_name` | Rndrng_Prvdr_Last_Org_Name | Last name or organization name |
| **ID** | `provider_first_name` | Rndrng_Prvdr_First_Name | First name (blank if organization) |
| **ID** | `provider_middle_initial` | Rndrng_Prvdr_MI | Middle initial |
| **ID** | `provider_credentials` | Rndrng_Prvdr_Crdntls | Credentials (M.D., D.O., NP, etc.) |
| **ID** | `provider_entity_type` | Rndrng_Prvdr_Ent_Cd | I=Individual, O=Organization |
| **Address** | `provider_street_address_1` | Rndrng_Prvdr_St1 | Street address line 1 |
| **Address** | `provider_street_address_2` | Rndrng_Prvdr_St2 | Street address line 2 |
| **Address** | `provider_city` | Rndrng_Prvdr_City | City |
| **Address** | `provider_state` | Rndrng_Prvdr_State_Abrvtn | State abbreviation (CA, TX, NY, etc.) |
| **Address** | `provider_state_fips` | Rndrng_Prvdr_State_FIPS | State FIPS code |
| **Address** | `provider_zip_code` | Rndrng_Prvdr_Zip5 | 5-digit ZIP code |
| **Address** | `provider_ruca_code` | Rndrng_Prvdr_RUCA | Rural-Urban Commuting Area code |
| **Address** | `provider_rural_urban_description` | Rndrng_Prvdr_RUCA_Desc | Rural/Urban classification |
| **Address** | `provider_country` | Rndrng_Prvdr_Cntry | Country code |
| **Class** | `provider_specialty` | Rndrng_Prvdr_Type | Medical specialty |
| **Class** | `medicare_participating` | Rndrng_Prvdr_Mdcr_Prtcptg_Ind | Y/N — accepts Medicare assignment |
| **Class** | `provider_gender` | Rndrng_Prvdr_Gndr | M=Male, F=Female |
| **Service** | `procedure_code` | HCPCS_Cd | HCPCS/CPT procedure code |
| **Service** | `procedure_description` | HCPCS_Desc | Procedure name in plain English |
| **Service** | `is_drug_service` | HCPCS_Drug_Ind | Y=Drug, N=Non-drug |
| **Service** | `place_of_service` | Place_Of_Srvc | F=Facility, O=Office |
| **Metrics** | `total_patients` | Tot_Benes | Number of unique Medicare patients |
| **Metrics** | `total_services` | Tot_Srvcs | Total services provided |
| **Metrics** | `total_patient_day_services` | Tot_Bene_Day_Srvcs | Distinct patient-day service count |
| **Payment** | `avg_submitted_charge` | Avg_Sbmtd_Chrg | Average charge submitted by provider |
| **Payment** | `avg_medicare_allowed_amount` | Avg_Mdcr_Alowd_Amt | Average Medicare-approved amount |
| **Payment** | `avg_medicare_payment` | Avg_Mdcr_Pymt_Amt | Average actual Medicare payment |
| **Payment** | `avg_medicare_standardized_amount` | Avg_Mdcr_Stdzd_Amt | Standardized payment (adjusted for geography) |

---

## Data Source

**Dataset:** Medicare Physician & Other Practitioners — by Provider and Service

**Source:** Centers for Medicare & Medicaid Services (CMS)

**API Endpoint:**
```
https://data.cms.gov/data-api/v1/dataset/92396110-2aed-4d63-a6a2-5d6207d46a29/data
```

**API Parameters:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| `size` | Number of records to return (max ~5000) | `?size=1000` |
| `offset` | Starting position for pagination | `?offset=5000` |

**Documentation:** https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service

**Total dataset size:** ~10,000,000+ rows

> ⚠️ This project uses **synthetic/public CMS data** only. No real patient data is stored or processed.

---

## Environment Variables

The notebook generates a `.env` file for the future FastAPI backend. You can also create it manually:

```env
# CareFlow AI — Database Configuration

DATABASE_HOST=localhost
DATABASE_PORT=5433
DATABASE_NAME=careflow_ai
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/careflow_ai
```

> ⚠️ The `.env` file is in `.gitignore` — it is never committed to Git. Each developer creates their own.

---

## Common Issues & Troubleshooting

### "ModuleNotFoundError: No module named 'xyz'"

You forgot to activate the virtual environment:
```powershell
.\venv\Scripts\activate
```

### "password authentication failed for user postgres"

Your PostgreSQL password doesn't match. Try:
1. A different password (the one you set during PostgreSQL install)
2. A different port (`5432` vs `5433`)
3. Reset the password (see [Step 8](#step-8-test-database-connection))

### "connection refused" or "could not connect to server"

PostgreSQL service isn't running:
```powershell
Get-Service -Name "postgresql*"
Start-Service -Name "postgresql-x64-17"
```

### Table is empty after running the import script

You likely re-ran **Section 4.3** in the notebook, which drops and recreates the table. Re-run the import script:
```powershell
.\venv\Scripts\activate
python import_all_cms_data.py
```

### Jupyter notebook can't find the kernel

Re-register the kernel:
```powershell
.\venv\Scripts\activate
python -m ipykernel install --user --name=careflow_venv --display-name="Python (CareFlow AI)"
```

### Import script is slow

The CMS API has rate limits. The script already includes a 0.2s delay between batches. If you experience timeouts:
- Reduce `BATCH_SIZE` to `2000`
- Increase `timeout` in the `requests.get()` call
- The script auto-retries up to 5 times per failed batch

### PowerShell says "running scripts is disabled"

Run this once as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## What's Next

After the data pipeline is set up, the next steps for CareFlow AI are:

1. **FastAPI Backend** — REST API endpoints to query the PostgreSQL database
2. **Frontend (React/Next.js)** — Healthcare dashboard UI
3. **AI Integration** — Connect OpenAI/Gemini/Claude for chatbot and AI features
4. **RAG Pipeline** — LangChain + vector database for document Q&A
5. **Additional Data** — Import more CMS datasets (claims, denial rates, etc.)

See `Document/instruction_app.txt` for the full application specification.

---

## License

This project is for the AI Hackathon. CMS Medicare data is public domain.

> **Disclaimer:** This demo uses synthetic/public CMS data and is intended for healthcare workflow demonstration only. It is not connected to real medical records and should not be used for clinical decision-making.
