from datetime import datetime
import enum
from pydantic import BaseModel, Field, model_validator

from app.schemas.user import UserResponse


class AvailableTimeSlotBase(BaseModel):
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    @classmethod
    def check_time_order(cls, model):
        if model.end_time <= model.start_time:
            raise ValueError("end_time must be greater than start_time")
        return model


class AvailableTimeSlotCreate(AvailableTimeSlotBase):
    pass


class AvailableTimeSlotUpdate(AvailableTimeSlotBase):
    pass


class AvailableTimeSlotResponse(BaseModel):
    id: int
    doctor_id: int
    created_at: datetime
    updated_at: datetime
    doctor_name: str | None = None

    @model_validator(mode="after")
    def add_doctor_name(self):
        # If doctor is available in the model, add the doctor name
        if hasattr(self, "doctor") and self.doctor:
            self.doctor_name = self.doctor.full_name
        return self

    class Config:
        from_attributes = True


class StatusEnum(str, enum.Enum):
    """Enum for appointment status."""

    scheduled = "scheduled"
    completed = "completed"
    canceled = "canceled"


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int | None = None
    doctor_id: int
    available_time_slot_id: int
    status: StatusEnum = Field(default=StatusEnum.scheduled)
    created_at: datetime
    updated_at: datetime
    patient_name: str | None = None
    doctor_name: str | None = None

    class Config:
        from_attributes = True


class ApointmentDetail(AppointmentResponse):
    patient: UserResponse | None = None
    doctor: UserResponse | None = None
    patient_name: str | None = Field(default=None, exclude=True)
    doctor_name: str | None = Field(default=None, exclude=True)
    available_time_slot: AvailableTimeSlotResponse | None = None


class CreateAppointment(BaseModel):
    doctor_id: int
    available_time_slot_id: int
