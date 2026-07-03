from app.config import settings


def test_register_with_valid_invite_code_returns_token(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "new-attorney@example.com",
            "password": "s3cret-pass",
            "signup_code": settings.attorney_signup_code,
        },
    )
    assert response.status_code == 201
    assert "access_token" in response.json()


def test_register_rejects_wrong_invite_code(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "new-attorney@example.com",
            "password": "s3cret-pass",
            "signup_code": "wrong-code",
        },
    )
    assert response.status_code == 403


def test_register_rejects_duplicate_email(client):
    payload = {
        "email": "dup-attorney@example.com",
        "password": "s3cret-pass",
        "signup_code": settings.attorney_signup_code,
    }
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/auth/register", json=payload)
    assert second.status_code == 409


def test_newly_registered_attorney_can_log_in(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "login-check@example.com",
            "password": "s3cret-pass",
            "signup_code": settings.attorney_signup_code,
        },
    )
    response = client.post(
        "/api/auth/login", json={"email": "login-check@example.com", "password": "s3cret-pass"}
    )
    assert response.status_code == 200
