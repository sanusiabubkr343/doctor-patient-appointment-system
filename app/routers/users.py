# app/routers/users.py

import enum
from fastapi import APIRouter, Body, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_auth_user
from app.dependencies.permissions import is_doctor
from app.models.users import User
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
from typing import Annotated, Optional
from fastapi import Query
from app.services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(form_data: LoginUser, db: Session = Depends(get_db)):
    return UserService.login(db, form_data)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: Annotated[CreateUser, Form()], db: Session = Depends(get_db)):
    return UserService.register_user(db, user)


@router.post(
    "/doctor_profile", response_model=DoctorProfileResponse, status_code=status.HTTP_201_CREATED
)
async def create_doctor_profile(
    profile: CreateDoctorProfile,
    current_user: User = Depends(is_doctor),
    db: Session = Depends(get_db),
):
    return UserService.create_doctor_profile(db, current_user.id, profile)


@router.put("/doctor_profile", response_model=DoctorProfileResponse, status_code=status.HTTP_200_OK)
async def update_doctor_profile(
    profile: UpdateDoctorProfile,
    current_user: User = Depends(is_doctor),
    db: Session = Depends(get_db),
):
    return UserService.update_doctor_profile(db, current_user.id, profile)


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    return UserService.get_user(db, user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    UserService.delete_user(db, user_id)


@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
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
    return UserService.get_all_users(
        db,
        skip=skip,
        limit=limit,
        search=search,
        role=role,
        sort_by=sort_by,
        sort_order=sort_order,
    )
