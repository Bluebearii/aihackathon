from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import random
from pathlib import Path

app = FastAPI(title="CareFlow AI Platform")

# Mount static files (HTML, CSS, JS)
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(static_dir / "index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/schedule")
async def get_schedule():
    # Mock data for tomorrow's schedule
    return [
        {
            "id": "APT-001",
            "time": "09:00 AM",
            "patient": "Sarah J.",
            "age": 28,
            "condition": "General Checkup",
            "wait_days": 21,
            "neighborhood": "JARDIM DA PENHA",
            "risk_score": 88,
            "risk_level": "High"
        },
        {
            "id": "APT-002",
            "time": "09:30 AM",
            "patient": "Michael T.",
            "age": 62,
            "condition": "Hypertension",
            "wait_days": 2,
            "neighborhood": "MATA DA PRAIA",
            "risk_score": 12,
            "risk_level": "Low"
        },
        {
            "id": "APT-003",
            "time": "10:00 AM",
            "patient": "Elena R.",
            "age": 35,
            "condition": "Test Results",
            "wait_days": 15,
            "neighborhood": "ITARARÉ",
            "risk_score": 75,
            "risk_level": "Medium"
        },
        {
            "id": "APT-004",
            "time": "11:00 AM",
            "patient": "James B.",
            "age": 45,
            "condition": "Diabetes Follow-up",
            "wait_days": 0,
            "neighborhood": "CENTRO",
            "risk_score": 5,
            "risk_level": "Low"
        },
        {
            "id": "APT-005",
            "time": "01:30 PM",
            "patient": "Amanda W.",
            "age": 22,
            "condition": "Consultation",
            "wait_days": 30,
            "neighborhood": "JARDIM CAMBURI",
            "risk_score": 92,
            "risk_level": "High"
        }
    ]

@app.get("/api/pricing")
async def get_pricing():
    # Mock data for pricing efficiency auditor
    return [
        {"state": "CA", "procedure": "DRG-871 (Sepsis)", "avg_charge": 85000, "medicare_payment": 15000, "write_off_pct": 82, "status": "Critical"},
        {"state": "TX", "procedure": "DRG-470 (Joint Replacement)", "avg_charge": 72000, "medicare_payment": 14000, "write_off_pct": 80, "status": "Critical"},
        {"state": "NY", "procedure": "DRG-291 (Heart Failure)", "avg_charge": 55000, "medicare_payment": 12000, "write_off_pct": 78, "status": "Warning"},
        {"state": "FL", "procedure": "DRG-392 (Esophagitis)", "avg_charge": 35000, "medicare_payment": 8000, "write_off_pct": 77, "status": "Warning"}
    ]

@app.get("/api/insurance")
async def get_insurance():
    # Mock data for out-of-pocket estimator
    return [
        {"patient_id": "P-8821", "name": "Robert K.", "procedure": "MRI Scan", "insurance": "Aetna HDHP", "estimated_cost": 2400, "patient_oop": 1800, "risk": "High Bad Debt"},
        {"patient_id": "P-1092", "name": "Lisa M.", "procedure": "CT Scan", "insurance": "UHC PPO", "estimated_cost": 1500, "patient_oop": 300, "risk": "Low"},
        {"patient_id": "P-4439", "name": "David S.", "procedure": "Surgery", "insurance": "Cigna HMO", "estimated_cost": 12000, "patient_oop": 2500, "risk": "High Bad Debt"},
    ]
