import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse
import psycopg2

sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

# Create a sanitized test DB name from your original DB
parsed_url = urlparse(settings.DATABASE_URL)
original_db_name = parsed_url.path[1:]  # remove leading "/"
safe_test_db_name = f"{original_db_name}_test".replace("-", "_")

# Construct a test database URL using the safe test DB name
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace(
    f"/{original_db_name}", f"/{safe_test_db_name}"
)


# Create the test DB if it doesn't exist
def create_test_db():
    default_url = settings.DATABASE_URL.replace(f"/{original_db_name}", "/postgres")
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
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
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


# Example user data fixture (customize as needed)
@pytest.fixture()
def user_data():
    return {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Test User",
        "role": "patient",
    }
