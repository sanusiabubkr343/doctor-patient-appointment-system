import datetime
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, DateTime, text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), index=True,nullable=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), index=True)
    available_time_slot_id = Column(Integer, ForeignKey("available_time_slots.id"), index=True)
    status = Column(String)  # e.g., 'scheduled', 'completed', 'canceled'
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=datetime.datetime.utcnow)


    patient = relationship("User", foreign_keys=[patient_id])
    doctor = relationship("User", foreign_keys=[doctor_id])


class AvailableTimeSlot(Base):
    __tablename__ = "available_time_slots"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=datetime.datetime.utcnow)


    doctor = relationship("User", back_populates="available_time_slots")
