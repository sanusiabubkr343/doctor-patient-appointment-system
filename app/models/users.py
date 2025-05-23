import datetime
from sqlalchemy import JSON, TIMESTAMP, Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="patient") 
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=datetime.datetime.utcnow)

    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)
    available_time_slots = relationship("AvailableTimeSlot", back_populates="doctor")

class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    specialization = Column(String)
    experience_years = Column(Integer)
    academic_history = Column(JSON)  
    bio = Column(String)

    user = relationship("User", back_populates="doctor_profile", passive_deletes=True)
