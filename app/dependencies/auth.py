from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Header,status
from app.core.config import settings
from jose import JWTError, jwt
from app.core.database import get_db
from app.models.users import User


async def get_token(auth_header: Annotated[str, Header(example="Bearer access-token",description="set header as auth-header")]) -> str:

    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    return auth_header.split(" ")[1]


async def get_auth_user(
    token: str = Depends(get_token), db: Session = Depends(get_db)
) -> User:

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(payload)
        user_id = payload.get("sub")
        if user_id is None:
            raise  HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
        )

    user = db.query(User).get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
