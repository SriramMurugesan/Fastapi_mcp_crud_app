import pytest
from fastapi import status

class TestAuth:
    def test_login_for_access_token_success(self, client, test_user):
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_for_access_token_invalid_credentials(self, client, test_user):
        login_data = {
            "username": test_user["username"],
            "password": "wrongpassword"
        }
        response = client.post("/token", data=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_read_users_me_success(self, client, auth_headers):
        response = client.get("/users/me/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert "email" in response.json()
        assert "username" in response.json()
        assert "id" in response.json()

    def test_read_users_me_unauthorized(self, client):
        response = client.get("/users/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json()["detail"]

    def test_create_user_success(self, client):
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == user_data["email"]
        assert response.json()["username"] == user_data["username"]
        assert "hashed_password" not in response.json()

    def test_create_user_duplicate_email(self, client, test_user):
        user_data = {
            "email": test_user["email"],
            "username": "differentuser",
            "password": "password123"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]
