from fastapi import HTTPException,status, Depends
from app.dependencies.auth import get_auth_user
from app.models.users import User


async def is_admin(user: User = Depends(get_auth_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin has the  permission to perform this action",
        )
    return user


async def is_doctor(user: User = Depends(get_auth_user)):
    if user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctor has the  permission to perform this action",
        )
    return user


async def is_patient(user: User = Depends(get_auth_user)):
    if user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patient has the  permission to perform this action",
        )
    return user


async def is_admin_or_doctor(user: User = Depends(get_auth_user)):
    if user.role not in ["admin", "doctor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or doctor has the  permission to perform this action",
        )
    return user


#is_patient or doctor

async def is_patient_or_doctor(user: User = Depends(get_auth_user)):
    if user.role not in ["patient", "doctor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patient or doctor has the  permission to perform this action",
        )
    return user
