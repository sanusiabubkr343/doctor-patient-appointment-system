from datetime import timedelta
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse
import psycopg2
import pytest
from copy import deepcopy
from datetime import timedelta

from app.tests.factories import UserFactory
from app.utils.auth import create_access_token

sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import Base, get_db
from app.main import app
import os

# Create a sanitized test DB name from your original DB
DATABASE_URL = os.getenv("DATABASE_URL")
parsed_url = urlparse(DATABASE_URL)
original_db_name = parsed_url.path[1:]  # remove leading "/"
safe_test_db_name = f"{original_db_name}_test".replace("-", "_")

# Construct a test database URL using the safe test DB name
SQLALCHEMY_DATABASE_URL = DATABASE_URL.replace(f"/{original_db_name}", f"/{safe_test_db_name}")


# Create the test DB if it doesn't exist
def create_test_db():
    default_url = DATABASE_URL.replace(f"/{original_db_name}", "/postgres")
    conn = psycopg2.connect(default_url)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (safe_test_db_name,))
    exists = cur.fetchone()
    if not exists:
        cur.execute(f'CREATE DATABASE "{safe_test_db_name}"')

    cur.close()
    conn.close()


create_test_db()

# Setup SQLAlchemy session for testing
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Fixture to provide a fresh DB for each test function
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    yield db

    transaction.rollback()
    connection.close()
    Base.metadata.drop_all(bind=engine)


# Fixture to provide a test client with the overridden DB session
@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture()
def mock_authenticated_user(db):
    """Mock authenticated user with specified role for testing."""

    def _user(role: str):
        user_factory = UserFactory()

        if role == "admin":
            user_data = user_factory.create(
                db,
                email=f"{role}_{user_factory.autogeneterate_email()}@app.com",
                full_name=f"{role.capitalize()} User",
                role=role,
            )

        elif role == "doctor":
            user_data = user_factory.create(
                db,
                email=f"{role}_{user_factory.autogeneterate_email()}@app.com",
                full_name=f"{role.capitalize()} User",
                role="doctor",
            )
        elif role == "patient":
            user_data = user_factory.create(
                db,
                email=f"{role}_{user_factory.autogeneterate_email()}@app.com",
                full_name=f"{role.capitalize()} User",
                role="patient",
            )

        return (
            create_access_token(
                data={
                    "sub": str(user_data.id),
                    "email": user_data.email,
                    "role": user_data.role,
                },
                expires_delta=timedelta(minutes=15),
            ),
            user_data,
        )

    return _user


# Authenticated test client fixture
@pytest.fixture
def client_with_auth(client, mock_authenticated_user):
    """Test client with authentication headers."""
    client.headers.update({"Authorization": f"Bearer {mock_authenticated_user}"})
    return client
