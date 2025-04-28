import enum
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRole(str,enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class UserBase(BaseModel):
    id: int
    email: EmailStr
    full_name: str = Field(max_length=225)
    password: str = Field(min_length=8, max_length=128, exclude=True)
    role: UserRole = Field(default=UserRole.PATIENT)


class CreateUser(UserBase):
    pass

class UpdateUser(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(max_length=225, default=None)
    password: Optional[str] = Field(min_length=8, max_length=128, exclude=True, default=None)
    role: Optional[UserRole] = Field(default=None)


class LoginUser(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class CreateDoctorProfile(BaseModel):
    user_id: int
    specialization: str
    experience_years: int
    academic_history: dict  # Assuming this is a JSON field
    bio: str

class UpdateDoctorProfile(BaseModel):
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    academic_history: Optional[dict] = None  # Assuming this is a JSON field
    bio: Optional[str] = None

class DoctorProfileResponse(BaseModel):
    
    id: int
    user_id: int
    user: UserBase
    specialization: str
    experience_years: int
    academic_history: dict  # Assuming this is a JSON field
    bio: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id:int
    email: EmailStr 
    full_name: str = Field(max_length=225)
    password:str = Field(min_length=8, max_length=128,exclude=True)
    role: UserRole = Field(default=UserRole.PATIENT)  
    doctor_profile: Optional["DoctorProfileResponse"] = None   
    created_at: datetime 
    updated_at: datetime 

    class Config:
        orm_mode = True
        use_enum_values = True
