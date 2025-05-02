from sqlalchemy.orm import Session

from app.models.appointments import Appointment, AvailableTimeSlot
from app.models.users import User
from app.utils.auth import get_password_hash
import random
from datetime import datetime, timedelta


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

    def random_string(self, length=8):
        """Generate a random string of fixed length"""
        import string

        return ''.join(random.choices(string.ascii_letters + string.digits, k=length)).lower()

    def autogeneterate_email(self):
        """Generate a random email address for the user"""
        return f"{self.random_string(8)}"

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


class AvailableTimeSlotFactory:
    def __init__(self, **defaults):
        """Initialize with default attributes that will be used for all created time slots"""
        start_time = datetime.now() + timedelta(days=random.randint(1, 30))
        end_time = start_time + timedelta(minutes=random.randint(30, 120))

        self.defaults = {
            "doctor_id": 1,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }
        self.defaults.update(defaults)

    def create(self, db: Session, **kwargs):
        """Create and persist a test available time slot to the database"""
        # Start with factory defaults, override with method kwargs
        time_slot_data = {**self.defaults, **kwargs}
        time_slot = AvailableTimeSlot(**time_slot_data)
        db.add(time_slot)
        db.commit()
        db.refresh(time_slot)
        return time_slot

    def create_batch(self, db: Session, count: int = 5, **kwargs):
        """Create and persist a batch of test available time slots to the database"""
        time_slots = []
        for _ in range(count):
            time_slot_data = {**self.defaults, **kwargs}
            time_slot = AvailableTimeSlot(**time_slot_data)
            db.add(time_slot)
            time_slots.append(time_slot)
        db.commit()
        for time_slot in time_slots:
            db.refresh(time_slot)
        return time_slots


class AppointmentFactory:
    def __init__(self, **defaults):
        """Initialize with default attributes that will be used for all created appointments"""
        self.defaults = {
            "patient_id": 1,
            "doctor_id": 2,
            "status": "scheduled",
            "available_time_slot_id": 1,
        }
        self.defaults.update(defaults)

    def create(self, db: Session, **kwargs):
        """Create and persist a test appointment to the database"""
        # Start with factory defaults, override with method kwargs
        appointment_data = {**self.defaults, **kwargs}
        appointment = Appointment(**appointment_data)
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment

    def create_batch(self, db: Session, count: int = 5, **kwargs):
        """Create and persist a batch of test appointments to the database"""
        appointments = []
        for _ in range(count):
            # Create a new available time slot for each appointment
            available_time_slot_factory = AvailableTimeSlotFactory()
            available_time_slot = available_time_slot_factory.create(db)

            # Update the defaults with the newly created available time slot ID
            appointment_data = {
                **self.defaults,
                "available_time_slot_id": available_time_slot.id,
                **kwargs,
            }
            appointment = Appointment(**appointment_data)
            db.add(appointment)
            appointments.append(appointment)
        db.commit()
        for appointment in appointments:
            db.refresh(appointment)
        return appointments
