import pytest

pytestmark = pytest.mark.asyncio

TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User",
}


async def test_register(client):
    response = await client.post("/api/v1/auth/register", json=TEST_USER)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == TEST_USER["email"]
    assert data["username"] == TEST_USER["username"]
    assert "password" not in data


async def test_register_duplicate_email(client):
    await client.post("/api/v1/auth/register", json=TEST_USER)
    response = await client.post("/api/v1/auth/register", json=TEST_USER)
    assert response.status_code == 409


async def test_login(client):
    await client.post("/api/v1/auth/register", json={**TEST_USER, "username": "logintest", "email": "login@example.com"})
    response = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": TEST_USER["password"],
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_login_wrong_password(client):
    response = await client.post("/api/v1/auth/login", json={
        "email": TEST_USER["email"],
        "password": "wrongpassword",
    })
    assert response.status_code == 401


async def test_get_profile(client):
    # Register and login
    await client.post("/api/v1/auth/register", json={**TEST_USER, "username": "profiletest", "email": "profile@example.com"})
    login = await client.post("/api/v1/auth/login", json={"email": "profile@example.com", "password": TEST_USER["password"]})
    token = login.json()["access_token"]

    response = await client.get("/api/v1/auth/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "profile@example.com"


async def test_profile_unauthorized(client):
    response = await client.get("/api/v1/auth/profile")
    assert response.status_code == 403  # HTTPBearer returns 403 when no credentials
