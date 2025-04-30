def test_register_user(client,user_data, db):
    response = client.post(
        "/users/register",
        data={
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "password": "string123",
            "role": user_data["role"],
        },
    )
    print(response.json())  
    assert response.status_code == 201
