import pytest

from app.tests.factories import UserFactory


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        ({"email": "test@example.com", "full_name": "Test User", "password": "string123", "role": "patient"}, 201),
        ({"email": "test@example.com", "full_name": "Test User", "password": "string123", "role": "none"}, 422),
        ({"email": "test@example.com", "full_name": "Test User", "password": "string123"}, 422),
        ({"email": "test@example.com", "password": "string123", "role": "doctor"}, 422),
        ({"full_name": "Test User", "password": "string123", "role": "admin"}, 422),
        ({}, 422),
    ],
)
def test_register_user(client, payload, expected_status):
    response = client.post("/users/register", data=payload)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "user_data, expected_status, expected_token",
    [
        ({"email": "test@example.com", "password": "string123"}, 200, True),
        ({"email": "wrong@example.com", "password": "string123"}, 401, False),
        ({"email": "test@example.com", "password": "wrongpass"}, 401, False),
        ({"email": "", "password": "string123"}, 422, False),
        ({"email": "test@example.com", "password": ""}, 422, False),
        ({}, 422, False),
    ],
)
def test_login_user(client, user_data, db, expected_status, expected_token):
    # Create a factory instance with the db session
    factory = UserFactory()

    factory.create(db=db, email="test@example.com", password="string123", role="patient")

    response = client.post("/users/login", json=user_data)
    assert (
        response.status_code == expected_status
    ), f"Expected {expected_status}, got {response.status_code}"
    if expected_token:
        assert "access_token" in response.json()
    else:
        assert "access_token" not in response.json()
