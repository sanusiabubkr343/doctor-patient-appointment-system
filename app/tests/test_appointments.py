import pytest


@pytest.mark.parametrize("role", ["patient", "doctor", "admin"])
def test_time_slot_creation(mocked_authentication, client, role):
    """Test time slot creation permissions based on user roles."""
    print(auth_client, auth_client[1])
    auth_client, = mocked_authentication(role, client)
    payload = {"start_time": "2025-05-02T10:00:00Z", "end_time": "2025-05-02T11:00:00Z"}
    response = auth_client.post("/create-time-slot", json=payload)
    assert response.status_code == (201 if role == "doctor" else 403)  # 
