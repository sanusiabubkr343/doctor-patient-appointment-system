# app/services/users.py

from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.users import DoctorProfile, User
from app.schemas.user import (
    CreateDoctorProfile,
    LoginUser,
    UserResponse,
    UpdateDoctorProfile,
    CreateUser,
    DoctorProfileResponse,
)
from app.utils.auth import create_access_token, get_password_hash, verify_password
from fastapi import HTTPException, status


class UserService:
    @staticmethod
    def login(db: Session, form_data: LoginUser):
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

    @staticmethod
    def register_user(db: Session, user_data: CreateUser):
        existing_user = db.query(User).filter_by(email=user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def create_doctor_profile(db: Session, user_id: int, profile_data: CreateDoctorProfile):
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        doctor_profile = DoctorProfile(user_id=user_id, **profile_data.model_dump())
        db.add(doctor_profile)
        db.commit()
        db.refresh(doctor_profile)
        return doctor_profile

    @staticmethod
    def update_doctor_profile(db: Session, user_id: int, profile_data: UpdateDoctorProfile):
        doctor_profile = db.query(DoctorProfile).filter_by(user_id=user_id).first()
        if not doctor_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found",
            )

        for key, value in profile_data.model_dump(exclude_unset=True).items():
            setattr(doctor_profile, key, value)

        db.commit()
        db.refresh(doctor_profile)
        return doctor_profile

    @staticmethod
    def get_user(db: Session, user_id: int):
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        db.delete(user)
        db.commit()

    @staticmethod
    def get_all_users(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        role: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "asc",
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

        return query.offset(skip).limit(limit).all()
