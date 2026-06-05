# 🏥 CareFlow AI

An intelligent healthcare operations platform designed to improve patient access, prior authorization, and revenue cycle management. Built with Python, PostgreSQL, and AI-ready architecture.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [A to Z: Repository File Guide](#a-to-z-repository-file-guide)
- [Prerequisites](#prerequisites)
- [Step-by-Step Setup Guide](#step-by-step-setup-guide)
- [Running the Project from A to Z](#running-the-project-from-a-to-z)
- [Database Schema & Data Source](#database-schema--data-source)
- [Common Issues & Troubleshooting](#common-issues--troubleshooting)

---

## Overview

CareFlow AI is a healthcare operations dashboard that uses real CMS (Centers for Medicare & Medicaid Services) data to power features like:

- **Patient Access** — Appointment scheduling, insurance verification, referral tracking
- **Prior Authorization** — Case management, documentation review, payer rule matching
- **Revenue Cycle Management** — Claim review, denial risk prediction, payment tracking

This repository contains the **data pipeline** that fetches Medicare provider data from the CMS API, imports it into a PostgreSQL database, a **Streamlit interactive dashboard**, a **FastAPI backend**, and **report generation tools**.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.12+ |
| **Database** | PostgreSQL 17/18 |
| **ORM** | SQLAlchemy |
| **Data Processing** | pandas, numpy, polars |
| **Visualization** | plotly, matplotlib, seaborn, altair |
| **Dashboard** | Streamlit + Plotly (interactive) |
| **API Framework** | FastAPI |
| **Notebook** | Jupyter |

---

## A to Z: Repository File Guide

Here is a comprehensive breakdown of **every single file and folder** in this project to help you understand how it all fits together:

### Directories
- `.git/` & `.gitignore`: Git repository tracking and ignore configurations.
- `.streamlit/`: Contains `config.toml` for Streamlit dashboard theming (colors, font).
- `careflow_app/`: The FastAPI backend application folder. Contains its own `main.py` entry point and `static/` files.
- `data/` & `data_source/`: Directories meant for storing raw and processed CSV/Parquet data files (like `medical-appointments-no-show-en.csv`).
- `Document/`: Documentation text files containing instructions and architecture plans (`instruction_app.txt`, `tools_instruction.md`, `api.txt`).
- `notebook/`: Contains Jupyter notebooks for exploration (`cms_data_pipeline.ipynb` and `no_show.ipynb`).
- `reports/`: The destination directory where `.docx` reports and charts are generated.
- `venv/`: The Python virtual environment (created during setup).
- `__pycache__/`: Compiled Python files (auto-generated).

### Main Application Files
- `README.md`: This documentation file.
- `requirements.txt`: Python dependency list (~250 packages) required to run the project.
- `main.py`: A simple placeholder entry point script in the root directory.
- `dashboard.py`: **⭐ The main interactive Streamlit dashboard.** Contains 29+ interactive charts, KPIs, and data tables.
- `import_all_cms_data.py`: Data ingestion script. Streams 1.5M records from the CMS API directly into PostgreSQL in batches.

### Report Generators
- `generate_report.py`: Generates a professional `.docx` analysis report with matplotlib charts from the PostgreSQL dataset.
- `generate_report_expanded.py`: Generates an expanded version of the `.docx` report featuring 29 charts and a full data dictionary.

### Utility & Patch Scripts
These are development scripts used to programmatically update notebooks or patch code:
- `add_notebook_cells.py`: Utility to inject new cells into the Jupyter notebook.
- `add_payment_definitions.py`: Adds payment definition markdown cells to `cms_data_pipeline.ipynb` and updates summary tables.
- `copy_templates.py`: Utility to copy HTML/Jinja templates (used during web app development).
- `expand_notebook.py`: Script to expand the data pipeline notebook with additional sections.
- `patch.py`, `patch2.py`, `patch_links.py`: Custom scripts used to patch routing, links, or specific code blocks across the project.

---

## Prerequisites

Before starting on your new computer, ensure you have:

1. **Python 3.12+** installed (`python --version`)
2. **Git** installed (`git --version`)
3. **PostgreSQL 17** (installed in the steps below)
4. **VS Code** with the **Jupyter** extension installed

---

## Step-by-Step Setup Guide

### Step 1: Open the Project Directory
Open PowerShell and navigate to the project directory on your new computer:
```powershell
cd C:\Users\trahu\OneDrive\Desktop\CodeWorld\aihackathon
```

### Step 2: Set up the Python Virtual Environment
Isolate your dependencies to avoid conflicts:
```powershell
python -m venv venv
.\venv\Scripts\activate
```
*(Your prompt should now show `(venv)` at the beginning)*

### Step 3: Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```
*(This installs pandas, SQLAlchemy, plotly, Streamlit, FastAPI, etc.)*

### Step 4: Register Jupyter Kernel
To use the notebook inside VS Code:
```powershell
python -m ipykernel install --user --name=careflow_venv --display-name="Python (CareFlow AI)"
```

### Step 5: Install and Verify PostgreSQL
1. Install PostgreSQL 17 using winget:
   ```powershell
   winget install PostgreSQL.PostgreSQL.17
   ```
2. **Important:** During setup, set the superuser password to `postgres` and keep the default port `5432` (or `5433` if you have older versions).
3. Verify it is running:
   ```powershell
   Get-Service -Name "postgresql*"
   ```
   *(If stopped, run `Start-Service -Name "postgresql-x64-17"`)*

4. **Database Configuration:** Check `import_all_cms_data.py` (lines 21-26) and `dashboard.py` to ensure the `DB_CONFIG` port matches your PostgreSQL installation (`5432` or `5433`).

---

## Running the Project from A to Z

Follow these steps to fully execute every part of the CareFlow AI project.

### 1. Database Setup & Data Import
First, you need to populate your PostgreSQL database with the CMS data.
```powershell
.\venv\Scripts\activate
python import_all_cms_data.py
```
*This will create the `careflow_ai` database, set up the tables, and import 1.5 million records from the CMS API. (Takes ~15-20 mins).*

### 2. Jupyter Notebook Analysis
Open VS Code and navigate to `notebook/cms_data_pipeline.ipynb`:
1. Select the **"Python (CareFlow AI)"** kernel in the top right.
2. Run the cells sequentially to perform exploratory data analysis, generate charts, and export Parquet/CSV data.
*(Note: Skip Section 4.3 if you already ran the import script above, to avoid dropping the table).*

### 3. Launch the Interactive Dashboard
The core visual experience of CareFlow AI:
```powershell
.\venv\Scripts\activate
streamlit run dashboard.py
```
*This starts a local server at `http://localhost:8501`. Explore the 8 pages of healthcare analytics.*

### 4. Run the FastAPI Backend
Start the web application backend API:
```powershell
.\venv\Scripts\activate
cd careflow_app
uvicorn main:app --reload
```
*Open `http://localhost:8000` in your browser. (Note: Keep the Streamlit dashboard running in a separate terminal if the web app embeds it).*

### 5. Run the WeCarePeople Web App (React + FastAPI)
The primary patient and admin portal, newly developed:

**Backend Server:**
```powershell
.\venv\Scripts\activate
cd carepoint-clinic\backend
uvicorn main:app --port 8001 --reload
```

**Frontend (React/Vite):**
```powershell
cd carepoint-clinic\frontend
npm run dev
```
*(Open `http://localhost:5173` in your browser. Log in as `sarah@carepoint.com` to see the Admin Analytics Hub, which embeds the Streamlit dashboard!)*

### 6. Generate Word Reports
To generate professional `.docx` reports summarizing the data insights:
```powershell
.\venv\Scripts\activate
python generate_report.py
python generate_report_expanded.py
```
*The resulting documents and charts will be saved in the `reports/` directory.*

### 7. Team Collaboration: Adding New Dashboards via the AI Analytics Hub
The new WeCarePeople Admin portal includes a dynamic **AI Analytics Hub**. This allows your team to build their own independent dashboards without touching the main codebase!

**How teammates can add their work:**
1. A teammate creates their own data visualizations (e.g., using a Jupyter Notebook and converting the charts into a simple Streamlit `.py` script).
2. They run their Streamlit app locally (e.g., `streamlit run my_model.py --server.port 8502`).
3. Log into the WeCarePeople web app as the Admin (`sarah@carepoint.com`).
4. Navigate to the **AI Analytics** page.
5. In the **Add New Dashboard** form, type a name (e.g., "Alice's Model") and paste the URL (e.g., `http://localhost:8502`).
6. Click **+ Register URL**. Their dashboard will instantly be embedded into the hub as a new tab!

### 8. Run Utility Scripts (Optional)

The PostgreSQL table `cms_medicare_providers` maps raw CMS columns to human-readable names:
- **ID & Demographics:** `provider_npi`, `provider_specialty`, `provider_gender`
- **Location:** `provider_state`, `provider_city`, `provider_zip_code`
- **Services:** `procedure_code`, `total_patients`, `total_services`
- **Payments:** `avg_submitted_charge`, `avg_medicare_allowed_amount`, `avg_medicare_payment`

---

## Common Issues & Troubleshooting

- **"ModuleNotFoundError"**: You forgot to activate the virtual environment (`.\venv\Scripts\activate`).
- **"password authentication failed for user postgres"**: Update the password or port (`5432` vs `5433`) in the `DB_CONFIG` dicts inside `import_all_cms_data.py`, `dashboard.py`, and the Jupyter notebooks.
- **"connection refused"**: PostgreSQL service is not running. Start it via `Start-Service -Name "postgresql-x64-17"`.
- **"running scripts is disabled"**: Run PowerShell as Administrator and execute: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.

---
> **Disclaimer:** This demo uses synthetic/public CMS data and is intended for healthcare workflow demonstration only. It is not connected to real medical records and should not be used for clinical decision-making.
