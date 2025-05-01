# app/services/appointments.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.appointments import Appointment, AvailableTimeSlot
from app.schemas.appointment import (
    AvailableTimeSlotCreate,
    AvailableTimeSlotResponse,
    AppointmentResponse,
    CreateAppointment,
    ApointmentDetail,
)
from typing import List


class AppointmentService:
    @staticmethod
    def create_time_slot(
        db: Session, doctor_id: int, time_slot_data: AvailableTimeSlotCreate
    ) -> AvailableTimeSlotResponse:
        """Create a new available time slot for the doctor."""
        # Check for overlapping time slots
        existing_time_slot = (
            db.query(AvailableTimeSlot)
            .filter(
                AvailableTimeSlot.doctor_id == doctor_id,
                ~(
                    (AvailableTimeSlot.start_time >= time_slot_data.end_time)
                    | (AvailableTimeSlot.end_time <= time_slot_data.start_time)
                ),
            )
            .first()
        )

        if existing_time_slot:
            raise HTTPException(
                status_code=400,
                detail="Time slot already exists or overlaps with another slot",
            )

        new_time_slot = AvailableTimeSlot(**time_slot_data.model_dump(), doctor_id=doctor_id)
        db.add(new_time_slot)
        db.commit()
        db.refresh(new_time_slot)

        return AvailableTimeSlotResponse.model_validate(new_time_slot).model_copy(
            update={"doctor_name": new_time_slot.doctor.full_name if new_time_slot.doctor else None}
        )

    @staticmethod
    def get_time_slot(db: Session, time_slot_id: int) -> AvailableTimeSlotResponse:
        """Get a single available time slot by id."""
        time_slot = db.query(AvailableTimeSlot).filter_by(id=time_slot_id).first()
        if not time_slot:
            raise HTTPException(
                status_code=404,
                detail="Time slot not found",
            )
        return AvailableTimeSlotResponse.model_validate(time_slot).model_copy(
            update={"doctor_name": time_slot.doctor.full_name if time_slot.doctor else None}
        )

    @staticmethod
    def delete_time_slot(db: Session, time_slot_id: int, doctor_id: int) -> None:
        """Delete an available time slot."""
        time_slot = (
            db.query(AvailableTimeSlot).filter_by(id=time_slot_id, doctor_id=doctor_id).first()
        )
        if not time_slot:
            raise HTTPException(
                status_code=404,
                detail="Time slot not found",
            )
        db.delete(time_slot)
        db.commit()

    @staticmethod
    def update_time_slot(
        db: Session,
        time_slot_id: int,
        doctor_id: int,
        time_slot_data: AvailableTimeSlotCreate,
    ) -> AvailableTimeSlotResponse:
        """Update an available time slot."""
        existing_time_slot = (
            db.query(AvailableTimeSlot).filter_by(id=time_slot_id, doctor_id=doctor_id).first()
        )
        if not existing_time_slot:
            raise HTTPException(
                status_code=404,
                detail="Time slot not found",
            )

        # Check for overlapping time slots (excluding current one)
        overlapping_slot = (
            db.query(AvailableTimeSlot)
            .filter(
                AvailableTimeSlot.doctor_id == doctor_id,
                AvailableTimeSlot.id != time_slot_id,
                ~(
                    (AvailableTimeSlot.start_time >= time_slot_data.end_time)
                    | (AvailableTimeSlot.end_time <= time_slot_data.start_time)
                ),
            )
            .first()
        )

        if overlapping_slot:
            raise HTTPException(
                status_code=400,
                detail="Updated time slot would overlap with another slot",
            )

        for key, value in time_slot_data.model_dump(exclude_unset=True).items():
            setattr(existing_time_slot, key, value)

        db.commit()
        db.refresh(existing_time_slot)
        return AvailableTimeSlotResponse.model_validate(existing_time_slot).model_copy(
            update={
                "doctor_name": (
                    existing_time_slot.doctor.full_name if existing_time_slot.doctor else None
                )
            }
        )

    @staticmethod
    def get_all_time_slots(db: Session) -> List[AvailableTimeSlotResponse]:
        """Get all available time slots."""
        time_slots = db.query(AvailableTimeSlot).order_by(AvailableTimeSlot.created_at.desc()).all()
        return [
            AvailableTimeSlotResponse.model_validate(time_slot).model_copy(
                update={"doctor_name": time_slot.doctor.full_name if time_slot.doctor else None}
            )
            for time_slot in time_slots
        ]

    @staticmethod
    def create_appointment(
        db: Session, patient_id: int, appointment_data: CreateAppointment
    ) -> AppointmentResponse:
        """Create a new appointment."""
        # Check if appointment already exists
        existing_appointment = (
            db.query(Appointment)
            .filter_by(
                available_time_slot_id=appointment_data.available_time_slot_id,
                doctor_id=appointment_data.doctor_id,
                status="scheduled",
            )
            .filter(Appointment.patient_id.isnot(None))
            .first()
        )

        if existing_appointment:
            raise HTTPException(
                status_code=400,
                detail="This time slot is already booked by another patient.",
            )

        new_appointment = Appointment(
            **appointment_data.model_dump(), patient_id=patient_id, status="scheduled"
        )
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)

        return AppointmentResponse.model_validate(new_appointment).model_copy(
            update={
                "patient_name": (
                    new_appointment.patient.full_name if new_appointment.patient else None
                ),
                "doctor_name": new_appointment.doctor.full_name if new_appointment.doctor else None,
            }
        )

    @staticmethod
    def complete_appointment(
        db: Session, appointment_id: int, doctor_id: int
    ) -> AppointmentResponse:
        """Complete an appointment."""
        appointment = (
            db.query(Appointment)
            .filter_by(id=appointment_id, doctor_id=doctor_id, status="scheduled")
            .first()
        )
        if not appointment:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found",
            )
        appointment.status = "completed"
        db.commit()
        db.refresh(appointment)
        return AppointmentResponse.model_validate(appointment).model_copy(
            update={
                "patient_name": appointment.patient.full_name if appointment.patient else None,
                "doctor_name": appointment.doctor.full_name if appointment.doctor else None,
            }
        )

    @staticmethod
    def cancel_appointment(
        db: Session, appointment_id: int, user_id: int, user_role: str
    ) -> AppointmentResponse:
        """Cancel an appointment."""
        if user_role == "patient":
            appointment = (
                db.query(Appointment)
                .filter_by(id=appointment_id, patient_id=user_id, status="scheduled")
                .first()
            )
        elif user_role == "doctor":
            appointment = (
                db.query(Appointment)
                .filter_by(id=appointment_id, doctor_id=user_id, status="scheduled")
                .first()
            )
        else:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to cancel appointments.",
            )

        if not appointment:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found or already completed/canceled",
            )

        appointment.status = "canceled"
        appointment.patient_id = None
        db.commit()
        db.refresh(appointment)
        return AppointmentResponse.model_validate(appointment).model_copy(
            update={
                "patient_name": appointment.patient.full_name if appointment.patient else None,
                "doctor_name": appointment.doctor.full_name if appointment.doctor else None,
            }
        )

    @staticmethod
    def get_all_appointments(
        db: Session, user_id: int, user_role: str
    ) -> List[AppointmentResponse]:
        """Get all appointments based on user role."""
        if user_role == "admin":
            appointments = db.query(Appointment).all()
        elif user_role == "doctor":
            appointments = db.query(Appointment).filter_by(doctor_id=user_id).all()
        elif user_role == "patient":
            appointments = db.query(Appointment).filter_by(patient_id=user_id).all()
        else:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view appointments.",
            )

        return [
            AppointmentResponse.model_validate(appointment).model_copy(
                update={
                    "patient_name": appointment.patient.full_name if appointment.patient else None,
                    "doctor_name": appointment.doctor.full_name if appointment.doctor else None,
                }
            )
            for appointment in appointments
        ]

    @staticmethod
    def get_appointment(db: Session, appointment_id: int) -> ApointmentDetail:
        """Get an appointment by id."""
        appointment = db.query(Appointment).get(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found",
            )
        return appointment
