"""Integration tests for /auth/register and /auth/login routes."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_register_returns_201_and_user(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "alice@test.com", "password": "supersecret1"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@test.com"
    assert "id" in body


def test_register_duplicate_returns_409(client: TestClient) -> None:
    payload = {"email": "dup@test.com", "password": "supersecret1"}
    first = client.post("/auth/register", json=payload)
    assert first.status_code == 201
    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409


def test_login_returns_token_on_valid_credentials(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={"email": "bob@test.com", "password": "supersecret1"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "bob@test.com", "password": "supersecret1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={"email": "carol@test.com", "password": "supersecret1"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "carol@test.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_login_unknown_email_returns_401(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "nobody@test.com", "password": "whatever1"},
    )
    assert response.status_code == 401


def test_protected_route_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_protected_route_with_valid_token_returns_200(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={"email": "dan@test.com", "password": "supersecret1"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "dan@test.com", "password": "supersecret1"},
    )
    token = login.json()["access_token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "dan@test.com"
