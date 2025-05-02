import pytest
from app.tests.factories import AppointmentFactory, AvailableTimeSlotFactory

class TestAppointment:
    @pytest.mark.parametrize(
        "role, expected_status",
        [
            ("doctor", 201),
            ("patient", 403),
            ("admin", 403),
        ],
    )
    def test_time_slot_creation(self, client, mock_authenticated_user, role, expected_status):
        """Test time slot creation permissions based on user roles."""
        token, _ = mock_authenticated_user(role=role)

        client.headers.update({"auth-header": f"Bearer {token}"})

        payload = {"start_time": "2025-05-02T10:00:00Z", "end_time": "2025-05-02T11:00:00Z"}
        response = client.post("/appointments/create-time-slot", json=payload)

        assert response.status_code == expected_status

    def test_deny_overlapping_time_slot_creation(self, client, mock_authenticated_user, db):
        """Test that overlapping time slots cannot be created."""
        token, auth_user = mock_authenticated_user(role="doctor")

        time_slot_factory = AvailableTimeSlotFactory()

        time_slot_factory.create(
            db=db,
            doctor_id=auth_user.id,
            start_time="2025-05-02T10:00:00Z",
            end_time="2025-05-02T11:00:00Z",
        )

        client.headers.update({"auth-header": f"Bearer {token}"})
        payload = {"start_time": "2025-05-02T10:00:00Z", "end_time": "2025-05-02T10:30:00Z"}

        response = client.post("/appointments/create-time-slot", json=payload)
        assert response.status_code == 400
        assert response.json() == {"detail": "Time slot already exists or overlaps with another slot"}

    def test_time_slot_creation_with_invalid_dates(self, client, mock_authenticated_user):
        """Test that invalid date formats are rejected."""
        token, _ = mock_authenticated_user(role="doctor")

        client.headers.update({"auth-header": f"Bearer {token}"})

        payload = {"start_time": "invalid-date", "end_time": "another-invalid-date"}
        response = client.post("/appointments/create-time-slot", json=payload)

        assert response.status_code == 422

    def test_get_time_slot_by_id(self, client, mock_authenticated_user, db):
        """Test fetching a time slot by its ID."""
        token, auth_user = mock_authenticated_user(role="doctor")

        time_slot_factory = AvailableTimeSlotFactory()
        time_slot = time_slot_factory.create(
            db=db,
            doctor_id=auth_user.id,
            start_time="2025-05-02T10:00:00Z",
            end_time="2025-05-02T11:00:00Z",
        )

        client.headers.update({"auth-header": f"Bearer {token}"})

        response = client.get(f"/appointments/get-time-slot/{time_slot.id}")
        assert response.status_code == 200
        assert response.json()["id"] == time_slot.id
        assert response.json()["doctor_id"] == auth_user.id

    def test_delete_time_slot(self, client, mock_authenticated_user, db):
        """Test deleting a time slot."""
        token, auth_user = mock_authenticated_user(role="doctor")

        time_slot_factory = AvailableTimeSlotFactory()
        time_slot = time_slot_factory.create(
            db=db,
            doctor_id=auth_user.id,
            start_time="2025-05-02T10:00:00Z",
            end_time="2025-05-02T11:00:00Z",
        )

        client.headers.update({"auth-header": f"Bearer {token}"})

        response = client.delete(f"/appointments/delete-time-slot/{time_slot.id}")
        assert response.status_code == 204

        response = client.get(f"/appointments/get-time-slot/{time_slot.id}")
        assert response.status_code == 404

    def test_update_time_slot(self, client, mock_authenticated_user, db):
        """Test updating a time slot."""
        token, auth_user = mock_authenticated_user(role="doctor")

        time_slot_factory = AvailableTimeSlotFactory()
        time_slot = time_slot_factory.create(
            db=db,
            doctor_id=auth_user.id,
            start_time="2025-05-02T10:00:00Z",
            end_time="2025-05-02T11:00:00Z",
        )

        client.headers.update({"auth-header": f"Bearer {token}"})

        payload = {"start_time": "2025-05-02T12:00:00Z", "end_time": "2025-05-02T13:00:00Z"}
        response = client.put(f"/appointments/update-time-slot/{time_slot.id}", json=payload)
        print(response.json())
        assert response.status_code == 200

    def test_get_all_time_slots(self, client, mock_authenticated_user, db):
        """Test fetching all time slots."""
        token, auth_user = mock_authenticated_user(role="doctor")

        time_slot_factory = AvailableTimeSlotFactory()
        time_slot_factory.create_batch(db=db, count=5, doctor_id=auth_user.id)

        client.headers.update({"auth-header": f"Bearer {token}"})

        response = client.get("/appointments/get-all-time-slots")
        assert response.status_code == 200
        assert len(response.json()) == 5

    @pytest.mark.parametrize(
        "role, expected_status",
        [
            ("patient", 201),
            ("doctor", 403),
            ("admin", 403),
        ],
    )
    def test_book_appointment(self, client, mock_authenticated_user, db, role, expected_status):
        """Test booking an appointment with different roles."""
        _, dcotor_data = mock_authenticated_user(role="doctor")

        token, _ = mock_authenticated_user(role=role)

        client.headers.update({"auth-header": f"Bearer {token}"})

        time_slot_factory = AvailableTimeSlotFactory()
        time_slot = time_slot_factory.create(
            db=db,
            doctor_id=dcotor_data.id,
            start_time="2025-05-02T10:00:00Z",
            end_time="2025-05-02T11:00:00Z",
        )

        payload = {
            "available_time_slot_id": time_slot.id,
            "doctor_id": time_slot.doctor_id,
        }
        response = client.post("/appointments/book-appointment", json=payload)
        assert response.status_code == expected_status
        if expected_status == 201:
            assert response.json()["doctor_id"] == dcotor_data.id
            assert response.json()["status"] == "scheduled"
        else:
            assert response.json() == {
                "detail": "Only patient has the  permission to perform this action"
            }

    @pytest.mark.parametrize(
        "role, expected_status",
        [
            ("doctor", 200),
            ("patient", 403),
            ("admin", 403),
        ],
    )
    def test_complete_appointment(self, client, mock_authenticated_user, db, role, expected_status):
        """Test completing an appointment with different roles."""
        token, auth_user = mock_authenticated_user(role=role)
        _, patient_data = mock_authenticated_user(role="patient")

        time_slot_factory = AvailableTimeSlotFactory()
        time_slot = time_slot_factory.create(
            db=db,
            doctor_id=auth_user.id,
            start_time="2025-05-02T10:00:00Z",
            end_time="2025-05-02T11:00:00Z",
        )

        appointment_factory = AppointmentFactory()
        appointment = appointment_factory.create(
            db=db,
            doctor_id=auth_user.id,
            patient_id=patient_data.id,
            available_time_slot_id=time_slot.id,
            status="scheduled",
        )

        client.headers.update({"auth-header": f"Bearer {token}"})

        response = client.post(f"/appointments/complete-appointment/{appointment.id}")
        assert response.status_code == expected_status
        if expected_status == 200:
            assert response.json()["status"] == "completed"
        else:
            assert response.json() == {
                "detail": "Only doctor has the  permission to perform this action"
            }

    @pytest.mark.parametrize(
        "initial_status, expected_status",
        [
            ("scheduled", 200),
            ("completed", 404),
            ("canceled", 404),
        ],
    )
    def test_cancel_appointment(self, client, mock_authenticated_user, db, initial_status, expected_status):
        """Test canceling an appointment with different initial statuses."""
        token, doctor_data = mock_authenticated_user(role="doctor")
        token, auth_user = mock_authenticated_user(role="patient")

        time_slot_factory = AvailableTimeSlotFactory()
        time_slot = time_slot_factory.create(
            db=db,
            doctor_id=doctor_data.id,
            start_time="2025-05-02T10:00:00Z",
            end_time="2025-05-02T11:00:00Z",
        )

        appointment_factory = AppointmentFactory()
        appointment = appointment_factory.create(
            db=db,
            doctor_id=doctor_data.id,
            patient_id=auth_user.id,
            available_time_slot_id=time_slot.id,
            status=initial_status,
        )

        client.headers.update({"auth-header": f"Bearer {token}"})

        response = client.post(f"/appointments/cancel-appointment/{appointment.id}")

        assert response.status_code == expected_status
        if expected_status == 200:
            assert response.json()["status"] == "canceled"
        else:
            assert response.json() == {"detail": "Appointment not found or already completed/canceled"}

    def test_get_all_appointments(self, client, mock_authenticated_user, db):
        """Test fetching all appointments."""
        token, auth_user = mock_authenticated_user(role="doctor")

        appointment_factory = AppointmentFactory()
        appointment_factory.create_batch(db=db, count=5, doctor_id=auth_user.id)

        client.headers.update({"auth-header": f"Bearer {token}"})

        response = client.get("/appointments/get-all-appointments")
        assert response.status_code == 200
        assert len(response.json()) == 5

    def test_get_appointment_by_id(self, client, mock_authenticated_user, db):
        """Test fetching an appointment by its ID."""
        token, auth_user = mock_authenticated_user(role="doctor")
        _, patient_data = mock_authenticated_user(role="patient")
        slot_factory = AvailableTimeSlotFactory()
        time_slot = slot_factory.create(
            db=db,
            doctor_id=auth_user.id,
            start_time="2025-05-02T10:00:00Z",
            end_time="2025-05-02T11:00:00Z",
        )

        appointment_factory = AppointmentFactory()
        appointment = appointment_factory.create(
            db=db,
            doctor_id=auth_user.id,
            patient_id=patient_data.id,
            available_time_slot_id=time_slot.id,
            status="scheduled",
        )

        client.headers.update({"auth-header": f"Bearer {token}"})

        response = client.get(f"/appointments/get-appointment/{appointment.id}")
        assert response.status_code == 200
        assert response.json()["id"] == appointment.id
        assert response.json()["doctor_id"] == auth_user.id
