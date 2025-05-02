import pytest


@pytest.mark.parametrize(
    "role, expected_status",
    [
        ("doctor", 201),
        ("patient", 403),
        ("admin", 403),
    ],
)
def test_time_slot_creation(client, mock_authenticated_user, role, expected_status):
    """Test time slot creation permissions based on user roles."""
    token = mock_authenticated_user(role=role)

    # Set the correct authorization header
    client.headers.update({"auth-header": f"Bearer {token}"})

    payload = {"start_time": "2025-05-02T10:00:00Z", "end_time": "2025-05-02T11:00:00Z"}
    response = client.post("/appointments/create-time-slot", json=payload)

    assert response.status_code == expected_status
