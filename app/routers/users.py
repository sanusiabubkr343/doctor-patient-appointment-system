import enum
from fastapi import APIRouter, Body, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_auth_user
from app.dependencies.permissions import is_doctor
from app.utils.auth import create_access_token, get_password_hash, verify_password
from app.models.users import DoctorProfile, User
from app.schemas.user import (
    CreateDoctorProfile,
    LoginUser,
    Token,
    UserResponse,
    UpdateDoctorProfile,
    CreateUser,
    DoctorProfileResponse,
    UserRole,
)
from datetime import timedelta
from app.core.config import settings
from typing import Annotated, Optional
from fastapi import Query


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/login", response_model=Token)
async def login(form_data: LoginUser, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=form_data.email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@router.post("/register", response_model=UserResponse)
async def register_user(user: Annotated[CreateUser, Form()], db: Session = Depends(get_db)):
    existing_user = db.query(User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/doctor_profile", response_model=DoctorProfileResponse)
async def create_doctor_profile(
    profile: CreateDoctorProfile,
    is_doctor: bool = Depends(is_doctor),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter_by(id=is_doctor.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    doctor_profile = DoctorProfile(user_id=is_doctor.id, **profile.model_dump())
    db.add(doctor_profile)
    db.commit()
    db.refresh(doctor_profile)
    return doctor_profile


@router.put("/doctor_profile", response_model=DoctorProfileResponse)
async def update_doctor_profile(
    profile: UpdateDoctorProfile,
    is_doctor: bool = Depends(is_doctor),
    db: Session = Depends(get_db),
):
    doctor_profile = db.query(DoctorProfile).filter_by(user_id=is_doctor.id).first()
    if not doctor_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )

    for key, value in profile.model_dump(exclude_unset=True).items():
        setattr(doctor_profile, key, value)

    db.commit()
    db.refresh(doctor_profile)
    return doctor_profile


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    db.delete(user)
    db.commit()


@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    is_authenticated: User = Depends(get_auth_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    search: Optional[str] = None,
    role: Optional[str] = None,
    sort_by: Optional[str] = Query("created_at", regex="^(name|email|created_at|updated_at)$"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
):
    query = db.query(User)

    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )

    if role:
        query = query.filter(User.role == role)

    if sort_order == "asc":
        query = query.order_by(getattr(User, sort_by).asc())
    else:
        query = query.order_by(getattr(User, sort_by).desc())

    users = query.offset(skip).limit(limit).all()
    return users
