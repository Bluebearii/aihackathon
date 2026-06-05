from pydantic import BaseModel
from typing import List, Optional, Optional
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

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Appointments
class AppointmentBase(BaseModel):
    appointment_type: str
    appointment_date: date
    appointment_time: time
    reason_for_visit: str
    insurance_provider: str
    status: str = "Pending"

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
    added_by_staff_id: int

class PointCreate(PointBase):
    patient_id: int

class Point(PointBase):
    id: int
    patient_id: int
    created_at: datetime
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
        orm_mode = True# Rewards
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
