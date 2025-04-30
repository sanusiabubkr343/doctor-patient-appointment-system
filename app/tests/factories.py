from sqlalchemy.orm import Session

from app.models.users import User
from app.utils.auth import get_password_hash


class UserFactory:
    def __init__(self, **defaults):
        """Initialize with default attributes that will be used for all created users"""
        self.defaults = {
            "email": "test@example.com",
            "full_name": "Test User",
            "hashed_password": get_password_hash("string123"),
            "role": "patient",
        }
        self.defaults.update(defaults)

    def create(self, db: Session, **kwargs):
        """Create and persist a test user to the database"""
        # Start with factory defaults, override with method kwargs
        user_data = {**self.defaults, **kwargs}

        # Handle password specially if provided
        if "password" in user_data:
            user_data["hashed_password"] = get_password_hash(user_data["password"])
            del user_data["password"]

        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
