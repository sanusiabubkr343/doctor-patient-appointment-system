# app/routers/appointments.py

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_auth_user
from app.dependencies.permissions import is_doctor, is_patient, is_patient_or_doctor
from app.models.users import User
from app.schemas.appointment import (
    ApointmentDetail,
    AppointmentResponse,
    AvailableTimeSlotCreate,
    AvailableTimeSlotResponse,
    CreateAppointment,
)
from fastapi import status

from app.services.appointments import AppointmentService

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
)


@router.post(
    "/create-time-slot",
    response_model=AvailableTimeSlotResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_time_slot(
    time_slot: AvailableTimeSlotCreate,
    current_user: User = Depends(is_doctor),
    db: Session = Depends(get_db),
):
    return AppointmentService.create_time_slot(db, current_user.id, time_slot)


@router.get(
    "/get-time-slot/{time_slot_id}",
    response_model=AvailableTimeSlotResponse,
    status_code=status.HTTP_200_OK,
)
async def get_time_slot(
    time_slot_id: int,
    db: Session = Depends(get_db),
):
    return AppointmentService.get_time_slot(db, time_slot_id)


@router.delete("/delete-time-slot/{time_slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_slot(
    time_slot_id: int,
    current_user: User = Depends(is_doctor),
    db: Session = Depends(get_db),
):
    AppointmentService.delete_time_slot(db, time_slot_id, current_user.id)


@router.put("/update-time-slot/{time_slot_id}", response_model=AvailableTimeSlotResponse, status_code=status.HTTP_200_OK)
async def update_time_slot(
    time_slot_id: int,
    time_slot: AvailableTimeSlotCreate,
    current_user: User = Depends(is_doctor),
    db: Session = Depends(get_db),
):
    return AppointmentService.update_time_slot(db, time_slot_id, current_user.id, time_slot)


@router.get("/get-all-time-slots", response_model=list[AvailableTimeSlotResponse], status_code=status.HTTP_200_OK)
async def get_all_time_slots(
    auth_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
):
    return AppointmentService.get_all_time_slots(db, skip=skip, limit=limit, sort_order=sort_order)


@router.post(
    "/book-appointment", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_appointment(
    appointment: CreateAppointment,
    current_user: User = Depends(is_patient),
    db: Session = Depends(get_db),
):
    return AppointmentService.create_appointment(db, current_user.id, appointment)


@router.post(
    "/complete-appointment/{appointment_id}",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
)
async def complete_appointment(
    appointment_id: int,
    current_user: User = Depends(is_doctor),
    db: Session = Depends(get_db),
):
    return AppointmentService.complete_appointment(db, appointment_id, current_user.id)


@router.post(
    "/cancel-appointment/{appointment_id}",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
)
async def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(is_patient_or_doctor),
    db: Session = Depends(get_db),
):
    return AppointmentService.cancel_appointment(
        db, appointment_id, current_user.id, current_user.role
    )


@router.get(
    "/get-all-appointments",
    response_model=list[AppointmentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_appointments(
    auth_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
):
    return AppointmentService.get_all_appointments(
        db, auth_user.id, auth_user.role, skip, limit, sort_order
    )


@router.get(
    "/get-appointment/{appointment_id}",
    response_model=ApointmentDetail,
    status_code=status.HTTP_200_OK,
)
async def get_appointment(
    appointment_id: int,
    auth_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db),
):
    return AppointmentService.get_appointment(db, appointment_id)
