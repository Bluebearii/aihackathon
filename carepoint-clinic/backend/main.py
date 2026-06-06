from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CarePoint Clinic API")

import ai_router
app.include_router(ai_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Care Flow AI API! Please visit the frontend at http://localhost:5173 or go to /docs for the API documentation."}

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

@app.post("/auth/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user_data = user.dict()
    del db_user_data['password']
    
    new_user = models.User(**db_user_data, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=schemas.User)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user

# ==========================================
# User / Patient Endpoints
# ==========================================

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"ok": True}

@app.get("/patients/", response_model=List[schemas.User])
def list_patients(
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.User).filter(models.User.role == "patient")
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (models.User.first_name.ilike(search_term)) |
            (models.User.last_name.ilike(search_term)) |
            (models.User.email.ilike(search_term)) |
            (models.User.phone.ilike(search_term))
        )
    return query.all()

@app.get("/patients/{patient_id}/profile")
def get_patient_profile(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.User).filter(models.User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    appointments = db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()
    points = db.query(models.Point).filter(models.Point.patient_id == patient_id).all()
    medical_history = db.query(models.MedicalHistory).filter(models.MedicalHistory.patient_id == patient_id).first()
    total_points = sum(p.points_added for p in points)
    
    return {
        "patient": schemas.User.from_orm(patient),
        "appointments": [schemas.Appointment.from_orm(a) for a in appointments],
        "points": [schemas.Point.from_orm(p) for p in points],
        "total_points": total_points,
        "medical_history": schemas.MedicalHistory.from_orm(medical_history) if medical_history else None
    }

# ==========================================
# Appointment Endpoints
# ==========================================

@app.post("/appointments/", response_model=schemas.Appointment)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@app.get("/appointments/", response_model=List[schemas.Appointment])
def read_appointments(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    appointments = db.query(models.Appointment).offset(skip).limit(limit).all()
    return appointments

@app.get("/appointments/calendar")
def get_calendar_appointments(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    provider: Optional[str] = None,
    status: Optional[str] = None,
    appointment_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Appointment)
    if start_date:
        query = query.filter(models.Appointment.appointment_date >= start_date)
    if end_date:
        query = query.filter(models.Appointment.appointment_date <= end_date)
    if provider:
        query = query.filter(models.Appointment.provider == provider)
    if status:
        query = query.filter(models.Appointment.status == status)
    if appointment_type:
        query = query.filter(models.Appointment.appointment_type == appointment_type)
    
    appointments = query.all()
    result = []
    for appt in appointments:
        patient = db.query(models.User).filter(models.User.id == appt.patient_id).first()
        result.append({
            "id": appt.id,
            "patient_id": appt.patient_id,
            "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            "appointment_type": appt.appointment_type,
            "appointment_date": str(appt.appointment_date),
            "appointment_time": str(appt.appointment_time),
            "status": appt.status,
            "provider": appt.provider,
            "reason_for_visit": appt.reason_for_visit,
            "notes": appt.notes
        })
    return result

@app.put("/appointments/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(appointment_id: int, appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    update_data = appointment.dict()
    for key, value in update_data.items():
        setattr(db_appointment, key, value)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@app.put("/appointments/{appointment_id}/status", response_model=schemas.Appointment)
def update_appointment_status(
    appointment_id: int,
    status: str,
    noshow_note: Optional[str] = None,
    db: Session = Depends(get_db)
):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db_appointment.status = status
    
    # Update patient record based on status
    patient = db.query(models.User).filter(models.User.id == db_appointment.patient_id).first()
    if patient:
        if status == "Completed":
            patient.last_visit_date = date.today()
        elif status == "No Show":
            patient.no_show_count = (patient.no_show_count or 0) + 1
            if noshow_note:
                db_appointment.notes = noshow_note
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(appt)
    db.commit()
    return {"ok": True}

# ==========================================
# Points Endpoints
# ==========================================

@app.post("/points/", response_model=schemas.Point)
def add_points(point: schemas.PointCreate, db: Session = Depends(get_db)):
    # check if points already added for this appointment
    if point.appointment_id:
        existing = db.query(models.Point).filter(models.Point.appointment_id == point.appointment_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Points already added for this appointment")
            
    db_point = models.Point(**point.dict())
    db.add(db_point)
    db.commit()
    db.refresh(db_point)
    return db_point

@app.get("/users/{user_id}/points", response_model=List[schemas.Point])
def get_user_points(user_id: int, db: Session = Depends(get_db)):
    points = db.query(models.Point).filter(models.Point.patient_id == user_id).all()
    return points

@app.get("/users/{user_id}/total_points")
def get_user_total_points(user_id: int, db: Session = Depends(get_db)):
    points = db.query(models.Point).filter(models.Point.patient_id == user_id).all()
    total = sum(p.points_added for p in points)
    return {"total_points": total}

# ==========================================
# Medical History Endpoints
# ==========================================

@app.post("/medical-history/", response_model=schemas.MedicalHistory)
def create_medical_history(mh: schemas.MedicalHistoryCreate, db: Session = Depends(get_db)):
    existing = db.query(models.MedicalHistory).filter(models.MedicalHistory.patient_id == mh.patient_id).first()
    if existing:
        # Update existing
        update_data = mh.dict()
        for key, value in update_data.items():
            setattr(existing, key, value)
        existing.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    
    db_mh = models.MedicalHistory(**mh.dict(), completed_at=datetime.utcnow())
    db.add(db_mh)
    db.commit()
    db.refresh(db_mh)
    return db_mh

@app.get("/medical-history/{patient_id}", response_model=Optional[schemas.MedicalHistory])
def get_medical_history(patient_id: int, db: Session = Depends(get_db)):
    mh = db.query(models.MedicalHistory).filter(models.MedicalHistory.patient_id == patient_id).first()
    if not mh:
        return None
    return mh

@app.put("/medical-history/{patient_id}", response_model=schemas.MedicalHistory)
def update_medical_history(patient_id: int, mh_update: schemas.MedicalHistoryBase, db: Session = Depends(get_db)):
    mh = db.query(models.MedicalHistory).filter(models.MedicalHistory.patient_id == patient_id).first()
    if not mh:
        raise HTTPException(status_code=404, detail="Medical history not found")
    update_data = mh_update.dict()
    for key, value in update_data.items():
        setattr(mh, key, value)
    mh.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(mh)
    return mh

# ==========================================
# Admin Stats Endpoint
# ==========================================

@app.get("/admin/stats")
def get_admin_stats(db: Session = Depends(get_db)):
    total_patients = db.query(models.User).filter(models.User.role == "patient").count()
    today = date.today()
    today_appts = db.query(models.Appointment).filter(models.Appointment.appointment_date == today).count()
    upcoming = db.query(models.Appointment).filter(
        models.Appointment.appointment_date >= today,
        models.Appointment.status.in_(["Pending", "Confirmed"])
    ).count()
    completed = db.query(models.Appointment).filter(models.Appointment.status == "Completed").count()
    noshow = db.query(models.Appointment).filter(models.Appointment.status == "No Show").count()
    
    # Count patients without medical history
    patients_with_mh = db.query(models.MedicalHistory.patient_id).distinct().count()
    pending_mh = total_patients - patients_with_mh
    
    total_points = db.query(func.coalesce(func.sum(models.Point.points_added), 0)).scalar()
    
    return {
        "total_patients": total_patients,
        "today_appointments": today_appts,
        "upcoming_appointments": upcoming,
        "completed_appointments": completed,
        "noshow_appointments": noshow,
        "pending_medical_forms": pending_mh,
        "total_points_awarded": total_points
    }

# ==========================================
# Dashboards Endpoints
# ==========================================

@app.post("/dashboards/", response_model=schemas.ExternalDashboard)
def create_dashboard(dash: schemas.ExternalDashboardCreate, db: Session = Depends(get_db)):
    new_dash = models.ExternalDashboard(**dash.dict())
    db.add(new_dash)
    db.commit()
    db.refresh(new_dash)
    return new_dash

@app.get("/dashboards/", response_model=List[schemas.ExternalDashboard])
def get_dashboards(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.ExternalDashboard).offset(skip).limit(limit).all()

@app.delete("/dashboards/{dash_id}")
def delete_dashboard(dash_id: int, db: Session = Depends(get_db)):
    dash = db.query(models.ExternalDashboard).filter(models.ExternalDashboard.id == dash_id).first()
    if not dash:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    db.delete(dash)
    db.commit()
    return {"ok": True}

# ==========================================
# ML Prediction Endpoint
# ==========================================
import xgboost as xgb
import pandas as pd
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'noshow_model.json')
xgb_model = None
if os.path.exists(MODEL_PATH):
    xgb_model = xgb.XGBClassifier()
    xgb_model.load_model(MODEL_PATH)

@app.get("/predict-attendance")
def predict_attendance(temp: float = 20.0, rain: float = 0.0, storm: int = 0):
    if not xgb_model:
        return {"error": "Model not loaded", "predicted_show_rate_pct": 90.0}
    
    # Create a synthetic distribution of 100 patients to average out the day's prediction
    np.random.seed(42)
    n = 100
    ages = np.random.normal(35, 15, n).clip(0, 100)
    under_12 = (ages < 12).astype(int)
    over_60 = (ages > 60).astype(int)
    companion = np.random.choice([0, 1], size=n, p=[0.95, 0.05])
    
    rainy_before = 1 if rain > 0 else 0
    
    df_pred = pd.DataFrame({
        'age': ages,
        'under_12_years_old': under_12,
        'over_60_years_old': over_60,
        'patient_needs_companion': companion,
        'average_temp_day': temp,
        'average_rain_day': rain,
        'rainy_day_before': rainy_before,
        'storm_day_before': storm
    })
    
    probs = xgb_model.predict_proba(df_pred)
    raw_noshow_prob = float(probs[:, 1].mean())
    
    # Calibrate baseline from XGBoost (trained with scale_pos_weight=9)
    calibrated_noshow_prob = raw_noshow_prob / 4.5
    
    # --- Hackathon Heuristics ---
    # Apply dramatic overrides AFTER calibration for demo effect
    
    # Is temperature in Fahrenheit? If > 80, it's hot. If < 40, it's cold.
    is_f = temp > 50
    heatwave = temp > 95 if is_f else temp > 35
    freezing = temp < 32 if is_f else temp < 0

    if storm == 1:
        # Storms cause massive cancellations
        calibrated_noshow_prob = max(calibrated_noshow_prob, 0.65) # 65% no-show
    elif rain > 0:
        # Rain causes moderate cancellations
        calibrated_noshow_prob = max(calibrated_noshow_prob, 0.35 + (rain * 0.05))
    else:
        # Sunny/clear days cap the no-show risk
        calibrated_noshow_prob = min(calibrated_noshow_prob, 0.15)
        
    if heatwave or freezing:
        calibrated_noshow_prob = max(calibrated_noshow_prob * 1.5, 0.45)
    
    # Cap probability to ensure realism
    calibrated_noshow_prob = min(0.85, max(0.01, calibrated_noshow_prob))
    
    show_rate = float((1.0 - calibrated_noshow_prob) * 100)
    
    return {
        "weather": {"temp": temp, "rain": rain, "storm": storm},
        "predicted_show_rate_pct": round(show_rate, 1)
    }
