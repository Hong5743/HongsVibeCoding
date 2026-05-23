import pytest
from httpx import AsyncClient

BASE = "/api/auth"


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    res = await client.post(f"{BASE}/signup", json={"email": "test@example.com", "password": "password123"})
    assert res.status_code == 201
    body = res.json()
    assert body["success"] is True
    assert "debug_token" in body["data"]


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    await client.post(f"{BASE}/signup", json={"email": "dup@example.com", "password": "password123"})
    res = await client.post(f"{BASE}/signup", json={"email": "dup@example.com", "password": "password123"})
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_signup_weak_password(client: AsyncClient):
    res = await client.post(f"{BASE}/signup", json={"email": "weak@example.com", "password": "short"})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_verify_email_success(client: AsyncClient):
    res = await client.post(f"{BASE}/signup", json={"email": "verify@example.com", "password": "password123"})
    token = res.json()["data"]["debug_token"]

    res = await client.get(f"{BASE}/verify-email", params={"token": token})
    assert res.status_code == 200
    assert res.json()["success"] is True


@pytest.mark.asyncio
async def test_verify_email_invalid_token(client: AsyncClient):
    res = await client.get(f"{BASE}/verify-email", params={"token": "invalid-token"})
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_login_before_verification(client: AsyncClient):
    await client.post(f"{BASE}/signup", json={"email": "unverified@example.com", "password": "password123"})
    res = await client.post(f"{BASE}/login", json={"email": "unverified@example.com", "password": "password123"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    signup_res = await client.post(f"{BASE}/signup", json={"email": "login@example.com", "password": "password123"})
    token = signup_res.json()["data"]["debug_token"]
    await client.get(f"{BASE}/verify-email", params={"token": token})

    res = await client.post(f"{BASE}/login", json={"email": "login@example.com", "password": "password123"})
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert "refresh_token" in body


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    signup_res = await client.post(f"{BASE}/signup", json={"email": "wrongpw@example.com", "password": "password123"})
    token = signup_res.json()["data"]["debug_token"]
    await client.get(f"{BASE}/verify-email", params={"token": token})

    res = await client.post(f"{BASE}/login", json={"email": "wrongpw@example.com", "password": "wrongpassword"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    signup_res = await client.post(f"{BASE}/signup", json={"email": "refresh@example.com", "password": "password123"})
    token = signup_res.json()["data"]["debug_token"]
    await client.get(f"{BASE}/verify-email", params={"token": token})
    login_res = await client.post(f"{BASE}/login", json={"email": "refresh@example.com", "password": "password123"})
    refresh_token = login_res.json()["refresh_token"]

    res = await client.post(f"{BASE}/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    assert "access_token" in res.json()["data"]


@pytest.mark.asyncio
async def test_me_endpoint(client: AsyncClient):
    signup_res = await client.post(f"{BASE}/signup", json={"email": "me@example.com", "password": "password123"})
    vtoken = signup_res.json()["data"]["debug_token"]
    await client.get(f"{BASE}/verify-email", params={"token": vtoken})
    login_res = await client.post(f"{BASE}/login", json={"email": "me@example.com", "password": "password123"})
    access_token = login_res.json()["access_token"]

    res = await client.get(f"{BASE}/me", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    assert res.json()["data"]["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_forgot_password(client: AsyncClient):
    signup_res = await client.post(f"{BASE}/signup", json={"email": "forgot@example.com", "password": "password123"})
    vtoken = signup_res.json()["data"]["debug_token"]
    await client.get(f"{BASE}/verify-email", params={"token": vtoken})

    res = await client.post(f"{BASE}/forgot-password", json={"email": "forgot@example.com"})
    assert res.status_code == 200
    assert "debug_token" in res.json()["data"]


@pytest.mark.asyncio
async def test_forgot_password_unknown_email(client: AsyncClient):
    res = await client.post(f"{BASE}/forgot-password", json={"email": "nobody@example.com"})
    assert res.status_code == 200  # no enumeration
