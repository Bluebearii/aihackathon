from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, DateTime, Boolean
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
    role = Column(String, default="patient") # patient, staff, admin
    created_at = Column(DateTime, default=datetime.utcnow)

    appointments = relationship("Appointment", back_populates="patient")
    points = relationship("Point", foreign_keys='Point.patient_id', back_populates="patient")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    appointment_type = Column(String)
    appointment_date = Column(Date)
    appointment_time = Column(Time)
    status = Column(String, default="Pending") # Pending, Confirmed, Checked In, Completed, No Show, Cancelled
    reason_for_visit = Column(String)
    insurance_provider = Column(String)
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
