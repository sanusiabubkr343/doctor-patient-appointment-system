from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.dependencies.auth import get_auth_user
from app.dependencies.permissions import is_doctor, is_patient, is_patient_or_doctor
from app.models.appointments import Appointment, AvailableTimeSlot
from app.models.users import User
from app.schemas.appointment import ApointmentDetail, AppointmentResponse, AvailableTimeSlotCreate, AvailableTimeSlotResponse, CreateAppointment
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)


@router.post("/create-time-slot", response_model=AvailableTimeSlotResponse)
async def create_time_slot(
    time_slot: AvailableTimeSlotCreate,
    is_doctor: bool = Depends(is_doctor),
    db: Session = Depends(get_db),
):
    """Create a new available time slot for the doctor."""
    # check if time slot already exists, no overlapping time slots

    existing_time_slot = db.query(AvailableTimeSlot).filter(
      AvailableTimeSlot.doctor_id == is_doctor.id,
      ~(
        (AvailableTimeSlot.start_time >= time_slot.end_time) |
        (AvailableTimeSlot.end_time <= time_slot.start_time)
      )
    ).first()
    if existing_time_slot:
        raise HTTPException(
            status_code=400,
            detail="Time slot already exists",
        ) 
    new_time_slot = AvailableTimeSlot(**time_slot.model_dump(), doctor_id=is_doctor.id)
    db.add(new_time_slot)
    db.commit()
    db.refresh(new_time_slot)
    response = AvailableTimeSlotResponse.model_validate(new_time_slot).model_copy(
        update={"doctor_name": new_time_slot.doctor.full_name if new_time_slot.doctor else None}
    )

    return response


@router.get("/get-time-slot/{time_slot_id}", response_model=AvailableTimeSlotResponse)
async def get_time_slot(
    time_slot_id: int,
    db: Session = Depends(get_db),
):
    """Get a single available time slot by id."""
    time_slot = db.query(AvailableTimeSlot).filter_by(id=time_slot_id).first()
    if not time_slot:
        raise HTTPException(
            status_code=404,
            detail="Time slot not found",
        )
    response = AvailableTimeSlotResponse.model_validate(time_slot).model_copy(
        update={"doctor_name": time_slot.doctor.full_name if time_slot.doctor else None}
    )
    return response


# delete time slot
@router.delete("/delete-time-slot/{time_slot_id}", status_code=204)
async def delete_time_slot(
    time_slot_id: int,
    is_doctor: bool = Depends(is_doctor),
    db: Session = Depends(get_db),
):
    """Delete an available time slot."""
    time_slot = (
        db.query(AvailableTimeSlot).filter_by(id=time_slot_id, doctor_id=is_doctor.id).first()
    )
    if not time_slot:
        raise HTTPException(
            status_code=404,
            detail="Time slot not found",
        )
    db.delete(time_slot)
    db.commit()
    return {"detail": "Time slot deleted successfully"}


# update time slot
@router.put("/update-time-slot/{time_slot_id}", response_model=AvailableTimeSlotResponse)
async def update_time_slot(
    time_slot_id: int,
    time_slot: AvailableTimeSlotCreate,
    is_doctor: User = Depends(is_doctor),
    db: Session = Depends(get_db),
):
    """Update an available time slot."""
    existing_time_slot = db.query(AvailableTimeSlot).filter_by(id=time_slot_id,doctor_id=is_doctor.id).first()
    if not existing_time_slot:
        raise HTTPException(
            status_code=404,
            detail="Time slot not found",
        )
    for key, value in time_slot.model_dump(exclude_unset=True).items():
        setattr(existing_time_slot, key, value)
    db.commit()
    db.refresh(existing_time_slot)
    response = AvailableTimeSlotResponse.model_validate(existing_time_slot).model_copy(
        update={"doctor_name": existing_time_slot.doctor.full_name if existing_time_slot.doctor else None}
    )
    return response


@router.get("/get-all-time-slots", response_model=list[AvailableTimeSlotResponse])
async def get_all_time_slots(
    auth_user: int = Depends(get_auth_user),
    db: Session = Depends(get_db),
):
    """Get all available time slots."""
    time_slots = db.query(AvailableTimeSlot).order_by(AvailableTimeSlot.created_at.desc()).all()
    time_slots_response = [
        AvailableTimeSlotResponse.model_validate(time_slot).model_copy(
            update={"doctor_name": time_slot.doctor.full_name if time_slot.doctor else None}
        )
        for time_slot in time_slots
    ]
    return time_slots_response


# create appointment
@router.post("/book-appointment", response_model=AppointmentResponse)
async def create_appointment(
    appointment: CreateAppointment,
    is_patient:  User= Depends(is_patient),
    db: Session = Depends(get_db),
):
    """Create a new appointment."""

    # check if appointment already exists
    existing_appointment = db.query(Appointment).filter_by(
      available_time_slot_id=appointment.available_time_slot_id,
      doctor_id=appointment.doctor_id,
      status="scheduled",
    ).filter(Appointment.patient_id.isnot(None)).first()

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="This time slot is already booked by another patient.",
        )
    new_appointment = Appointment(**appointment.model_dump(), patient_id=is_patient.id,status="scheduled")
    

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    response = AppointmentResponse.model_validate(new_appointment).model_copy(
      update={
        "patient_name": new_appointment.patient.full_name if new_appointment.patient else None,
        "doctor_name": new_appointment.doctor.full_name if new_appointment.doctor else None,
      }
    )
    return response


# set appointment status as completed
@router.post("/complete-appointment/{appointment_id}", response_model=AppointmentResponse)
async def complete_appointment(
    appointment_id: int,
    is_doctor:User= Depends(is_doctor),
    db: Session = Depends(get_db),
):
    """Complete an appointment."""
    appointment = db.query(Appointment).filter_by(id=appointment_id, doctor_id=is_doctor.id,status="scheduled").first()
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found",
        )
    appointment.status = "completed"
    db.commit()
    db.refresh(appointment)
    response = AppointmentResponse.model_validate(appointment).model_copy(
        update={
            "patient_name": appointment.patient.full_name if appointment.patient else None,
            "doctor_name": appointment.doctor.full_name if appointment.doctor else None,
        }
    )
    return response


# cancel appointment
@router.post("/cancel-appointment/{appointment_id}", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: int,
    user: User = Depends(is_patient_or_doctor),
    db: Session = Depends(get_db),
):
    """Cancel an appointment."""

    if user.role == "patient":
        appointment = (
            db.query(Appointment)
            .filter_by(id=appointment_id, patient_id=user.id, status="scheduled")
            .first()
        )
        if not appointment:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found or already completed/canceled",
            )

    elif user.role == "doctor":
        appointment = (
            db.query(Appointment)
            .filter_by(id=appointment_id, doctor_id=user.id, status="scheduled")
            .first()
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
    response = AppointmentResponse.model_validate(appointment).model_copy(
        update={
            "patient_name": appointment.patient.full_name if appointment.patient else None,
            "doctor_name": appointment.doctor.full_name if appointment.doctor else None,
        }
    )
    return response


# get all appointments
@router.get("/get-all-appointments", response_model=list[AppointmentResponse])
async def get_all_appointments(
    auth_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db),
):
    """Get all appointments."""
    if auth_user.role == "admin":
        appointments = db.query(Appointment).all()
    elif auth_user.role == "doctor":
        appointments = db.query(Appointment).filter_by(doctor_id=auth_user.id).all()
    elif auth_user.role == "patient":
        appointments = db.query(Appointment).filter_by(patient_id=auth_user.id).all()
    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view appointments.",
        )
    response = [
    AppointmentResponse.model_validate(appointment).model_copy(
        update={
            "patient_name": appointment.patient.full_name if appointment.patient else None,
            "doctor_name": appointment.doctor.full_name if appointment.doctor else None,
        }
    )
    for appointment in appointments
]
    return response


# get appointment by id
@router.get("/get-appointment/{appointment_id}", response_model=ApointmentDetail)
async def get_appointment(
    appointment_id: int,
    auth_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db),
):
    """Get an appointment by id."""
    appointment = db.query(Appointment).get(appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found",
        )
    return appointment
