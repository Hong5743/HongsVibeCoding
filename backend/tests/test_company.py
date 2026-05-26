import io
import os
import pytest
from httpx import AsyncClient

BASE_AUTH = "/api/auth"
BASE = "/api/companies"


async def _verified_token(client: AsyncClient, email: str, password: str = "password123") -> str:
    signup = await client.post(f"{BASE_AUTH}/signup", json={"email": email, "password": password})
    vtoken = signup.json()["data"]["debug_token"]
    await client.get(f"{BASE_AUTH}/verify-email", params={"token": vtoken})
    login = await client.post(f"{BASE_AUTH}/login", json={"email": email, "password": password})
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_get_profile_unauthenticated(client: AsyncClient):
    res = await client.get(f"{BASE}/me")
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_get_profile_authenticated(client: AsyncClient):
    token = await _verified_token(client, "getprofile@test.com")
    res = await client.get(f"{BASE}/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["email"] == "getprofile@test.com"
    assert body["data"]["status"] == "pending"
    assert body["data"]["name"] is None


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient):
    token = await _verified_token(client, "update@test.com")
    res = await client.put(
        f"{BASE}/me",
        json={"name": "Test Corp", "industry": "Tech", "founded_year": 2020},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["name"] == "Test Corp"
    assert data["industry"] == "Tech"
    assert data["founded_year"] == 2020


@pytest.mark.asyncio
async def test_update_profile_partial(client: AsyncClient):
    token = await _verified_token(client, "partial@test.com")
    await client.put(
        f"{BASE}/me",
        json={"name": "First Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    res = await client.put(
        f"{BASE}/me",
        json={"industry": "Finance"},
        headers={"Authorization": f"Bearer {token}"},
    )
    data = res.json()["data"]
    assert data["name"] == "First Name"  # not overwritten
    assert data["industry"] == "Finance"


@pytest.mark.asyncio
async def test_update_profile_unauthenticated(client: AsyncClient):
    res = await client.put(f"{BASE}/me", json={"name": "No Auth"})
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_upload_image(client: AsyncClient):
    os.makedirs("uploads", exist_ok=True)
    token = await _verified_token(client, "upload@test.com")

    fake_img = b"\xff\xd8\xff\xe0" + b"\x00" * 16
    res = await client.post(
        f"{BASE}/me/upload",
        files={"files": ("photo.jpg", io.BytesIO(fake_img), "image/jpeg")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data["urls"]) == 1
    assert data["urls"][0].startswith("/uploads/")
    assert data["urls"][0].endswith(".jpg")
    assert data["all_image_urls"] == data["urls"]

    # cleanup
    for url in data["urls"]:
        path = url.lstrip("/")
        if os.path.exists(path):
            os.remove(path)


@pytest.mark.asyncio
async def test_upload_multiple_images(client: AsyncClient):
    os.makedirs("uploads", exist_ok=True)
    token = await _verified_token(client, "multi_upload@test.com")

    fake_img = b"\xff\xd8\xff\xe0" + b"\x00" * 16
    res = await client.post(
        f"{BASE}/me/upload",
        files=[
            ("files", ("a.jpg", io.BytesIO(fake_img), "image/jpeg")),
            ("files", ("b.png", io.BytesIO(fake_img), "image/png")),
        ],
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data["urls"]) == 2
    assert len(data["all_image_urls"]) == 2

    # cleanup
    for url in data["urls"]:
        path = url.lstrip("/")
        if os.path.exists(path):
            os.remove(path)


@pytest.mark.asyncio
async def test_upload_invalid_content_type(client: AsyncClient):
    token = await _verified_token(client, "badtype@test.com")
    res = await client.post(
        f"{BASE}/me/upload",
        files={"files": ("doc.txt", io.BytesIO(b"hello"), "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "Unsupported file type" in res.json()["detail"]["error"]


@pytest.mark.asyncio
async def test_upload_unauthenticated(client: AsyncClient):
    fake_img = b"\xff\xd8\xff\xe0" + b"\x00" * 16
    res = await client.post(
        f"{BASE}/me/upload",
        files={"files": ("photo.jpg", io.BytesIO(fake_img), "image/jpeg")},
    )
    assert res.status_code == 403
