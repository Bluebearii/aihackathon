from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, DateTime, Boolean, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    phone = Column(String)
    address = Column(String)
    date_of_birth = Column(Date)
    gender = Column(String, nullable=True)
    insurance_provider = Column(String, nullable=True)
    role = Column(String, default="patient") # patient, staff, admin
    no_show_count = Column(Integer, default=0)
    last_visit_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    appointments = relationship("Appointment", back_populates="patient")
    points = relationship("Point", foreign_keys='Point.patient_id', back_populates="patient")
    medical_history = relationship("MedicalHistory", back_populates="patient", uselist=False)

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    appointment_type = Column(String)
    appointment_date = Column(Date)
    appointment_time = Column(Time)
    status = Column(String, default="Pending") # Pending, Confirmed, Completed, No Show, Cancelled, Rescheduled
    reason_for_visit = Column(String)
    insurance_provider = Column(String)
    provider = Column(String, nullable=True)  # Doctor/provider name
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("User", back_populates="appointments")
    points = relationship("Point", back_populates="appointment")

class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    points_added = Column(Integer)
    reason = Column(String)
    added_by_staff_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("User", foreign_keys=[patient_id], back_populates="points")
    appointment = relationship("Appointment", back_populates="points")
    staff = relationship("User", foreign_keys=[added_by_staff_id])

class MedicalHistory(Base):
    __tablename__ = "medical_history"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # Patient info (auto-filled from profile)
    patient_name = Column(String, nullable=True)
    height_ft = Column(Integer, nullable=True)
    height_in = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    date_of_injury = Column(String, nullable=True)
    latex_allergy_yes = Column(Boolean, default=False)
    latex_allergy_no = Column(Boolean, default=True)
    topical_allergy = Column(String, nullable=True)

    # Diagnosis & history
    diagnosis = Column(Text, nullable=True)
    injury_description = Column(Text, nullable=True)
    hospitalized = Column(Boolean, default=False)
    hospitalized_date = Column(String, nullable=True)
    surgery = Column(Boolean, default=False)
    surgery_date = Column(String, nullable=True)
    surgery_type = Column(String, nullable=True)

    # Falls
    falls_past_year = Column(Boolean, default=False)
    falls_count = Column(Integer, nullable=True)

    # Previous treatment
    previous_treatment = Column(Boolean, default=False)
    treatment_date = Column(String, nullable=True)
    treatment_summary = Column(Text, nullable=True)

    # Imaging tests
    emg = Column(Boolean, default=False)
    ct_scan = Column(Boolean, default=False)
    myelogram = Column(Boolean, default=False)
    mri = Column(Boolean, default=False)
    xray = Column(Boolean, default=False)

    # ---- Left column conditions ----
    acquired_respiratory_distress = Column(Boolean, default=False)
    angina = Column(Boolean, default=False)
    anxiety_panic = Column(Boolean, default=False)
    arthritis = Column(Boolean, default=False)
    asthma = Column(Boolean, default=False)
    copd = Column(Boolean, default=False)
    chf = Column(Boolean, default=False)
    degenerative_disc = Column(Boolean, default=False)
    depression = Column(Boolean, default=False)
    diabetes = Column(Boolean, default=False)
    emphysema = Column(Boolean, default=False)
    hearing_impairment = Column(Boolean, default=False)
    heart_attack = Column(Boolean, default=False)
    multiple_sclerosis = Column(Boolean, default=False)
    osteoporosis = Column(Boolean, default=False)
    parkinsons = Column(Boolean, default=False)
    peripheral_vascular = Column(Boolean, default=False)
    stroke_tia = Column(Boolean, default=False)
    upper_gi_disease = Column(Boolean, default=False)
    visual_impairment = Column(Boolean, default=False)

    # ---- Right column conditions ----
    allergies = Column(Boolean, default=False)
    headaches = Column(Boolean, default=False)
    back_injury = Column(Boolean, default=False)
    bleeding_disorders = Column(Boolean, default=False)
    bowel_bladder = Column(Boolean, default=False)
    cancer = Column(Boolean, default=False)
    dizzy_fainting = Column(Boolean, default=False)
    epilepsy_seizure = Column(Boolean, default=False)
    fracture = Column(Boolean, default=False)
    hepatitis = Column(Boolean, default=False)
    hernia = Column(Boolean, default=False)
    high_blood_pressure = Column(Boolean, default=False)
    hypoglycemia = Column(Boolean, default=False)
    immunosuppressant = Column(Boolean, default=False)
    kidney_problems = Column(Boolean, default=False)
    liver_gallbladder = Column(Boolean, default=False)
    metal_implants = Column(Boolean, default=False)
    nausea_vomiting = Column(Boolean, default=False)
    pacemaker = Column(Boolean, default=False)
    pregnancy = Column(Boolean, default=False)
    ringing_ears = Column(Boolean, default=False)
    sexual_dysfunction = Column(Boolean, default=False)
    skin_abnormalities = Column(Boolean, default=False)
    smoking = Column(Boolean, default=False)
    special_diet = Column(Boolean, default=False)
    tuberculosis = Column(Boolean, default=False)

    # Additional fields
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    current_medications = Column(Text, nullable=True)
    family_history = Column(Text, nullable=True)
    reason_for_visit = Column(Text, nullable=True)
    additional_notes = Column(Text, nullable=True)

    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("User", back_populates="medical_history")

class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    reward_name = Column(String)
    required_points = Column(Integer)
    description = Column(String)
    active_status = Column(Boolean, default=True)

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String) # e.g. "appointment_booked", "points_added"
    user_id = Column(Integer, ForeignKey("users.id"))
    details = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExternalDashboard(Base):
    __tablename__ = "external_dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
