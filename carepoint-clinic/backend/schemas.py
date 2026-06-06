from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time, datetime

# Users
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    date_of_birth: date
    role: str = "patient"
    gender: Optional[str] = None
    insurance_provider: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    insurance_provider: Optional[str] = None

class User(UserBase):
    id: int
    no_show_count: int = 0
    last_visit_date: Optional[date] = None
    created_at: datetime

    class Config:
        orm_mode = True

# Appointments
class AppointmentBase(BaseModel):
    appointment_type: str
    appointment_date: date
    appointment_time: time
    reason_for_visit: str
    insurance_provider: Optional[str] = None
    status: str = "Pending"
    provider: Optional[str] = None
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    patient_id: int

class Appointment(AppointmentBase):
    id: int
    patient_id: int
    created_at: datetime
    patient: Optional[User] = None

    class Config:
        orm_mode = True

# Points
class PointBase(BaseModel):
    points_added: int
    reason: str
    appointment_id: Optional[int] = None
    added_by_staff_id: Optional[int] = None

class PointCreate(PointBase):
    patient_id: int

class Point(PointBase):
    id: int
    patient_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Dashboards
class ExternalDashboardBase(BaseModel):
    name: str
    url: str
    description: Optional[str] = None

class ExternalDashboardCreate(ExternalDashboardBase):
    pass

class ExternalDashboard(ExternalDashboardBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Rewards
class RewardBase(BaseModel):
    reward_name: str
    required_points: int
    description: str
    active_status: bool = True

class RewardCreate(RewardBase):
    pass

class Reward(RewardBase):
    id: int

    class Config:
        orm_mode = True

# Medical History
class MedicalHistoryBase(BaseModel):
    patient_name: Optional[str] = None
    height_ft: Optional[int] = None
    height_in: Optional[int] = None
    weight: Optional[float] = None
    date_of_injury: Optional[str] = None
    latex_allergy_yes: bool = False
    latex_allergy_no: bool = True
    topical_allergy: Optional[str] = None
    diagnosis: Optional[str] = None
    injury_description: Optional[str] = None
    hospitalized: bool = False
    hospitalized_date: Optional[str] = None
    surgery: bool = False
    surgery_date: Optional[str] = None
    surgery_type: Optional[str] = None
    falls_past_year: bool = False
    falls_count: Optional[int] = None
    previous_treatment: bool = False
    treatment_date: Optional[str] = None
    treatment_summary: Optional[str] = None
    emg: bool = False
    ct_scan: bool = False
    myelogram: bool = False
    mri: bool = False
    xray: bool = False

    # Left column conditions
    acquired_respiratory_distress: bool = False
    angina: bool = False
    anxiety_panic: bool = False
    arthritis: bool = False
    asthma: bool = False
    copd: bool = False
    chf: bool = False
    degenerative_disc: bool = False
    depression: bool = False
    diabetes: bool = False
    emphysema: bool = False
    hearing_impairment: bool = False
    heart_attack: bool = False
    multiple_sclerosis: bool = False
    osteoporosis: bool = False
    parkinsons: bool = False
    peripheral_vascular: bool = False
    stroke_tia: bool = False
    upper_gi_disease: bool = False
    visual_impairment: bool = False

    # Right column conditions
    allergies: bool = False
    headaches: bool = False
    back_injury: bool = False
    bleeding_disorders: bool = False
    bowel_bladder: bool = False
    cancer: bool = False
    dizzy_fainting: bool = False
    epilepsy_seizure: bool = False
    fracture: bool = False
    hepatitis: bool = False
    hernia: bool = False
    high_blood_pressure: bool = False
    hypoglycemia: bool = False
    immunosuppressant: bool = False
    kidney_problems: bool = False
    liver_gallbladder: bool = False
    metal_implants: bool = False
    nausea_vomiting: bool = False
    pacemaker: bool = False
    pregnancy: bool = False
    ringing_ears: bool = False
    sexual_dysfunction: bool = False
    skin_abnormalities: bool = False
    smoking: bool = False
    special_diet: bool = False
    tuberculosis: bool = False

    # Additional fields
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    current_medications: Optional[str] = None
    family_history: Optional[str] = None
    reason_for_visit: Optional[str] = None
    additional_notes: Optional[str] = None

class MedicalHistoryCreate(MedicalHistoryBase):
    patient_id: int

class MedicalHistory(MedicalHistoryBase):
    id: int
    patient_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True

# Dashboard stats
class AdminStats(BaseModel):
    total_patients: int
    today_appointments: int
    upcoming_appointments: int
    completed_appointments: int
    noshow_appointments: int
    pending_medical_forms: int
    total_points_awarded: int
