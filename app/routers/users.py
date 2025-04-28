from fastapi import   APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from app.core import security
from app.utils.auth import create_access_token, verify_password
from app.models.users import User
from app.schemas.user import LoginUser, Token
from dependencies.auth import get_db
from datetime import timedelta
from app.core.config import settings


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
        data={"sub": int(user.id),"email":user.email,"role":user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "Bearer"}

