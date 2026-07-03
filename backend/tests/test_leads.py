import io
from pathlib import Path

from app.config import settings


def _submit_lead(client, email="prospect@example.com"):
    return client.post(
        "/api/leads",
        data={"first_name": "Ada", "last_name": "Lovelace", "email": email},
        files={"resume": ("resume.pdf", io.BytesIO(b"%PDF-1.4 fake pdf contents"), "application/pdf")},
    )


def test_create_lead_is_public_and_starts_pending(client):
    response = _submit_lead(client)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PENDING"
    assert body["email"] == "prospect@example.com"


def test_create_lead_rejects_bad_file_type(client):
    response = client.post(
        "/api/leads",
        data={"first_name": "Ada", "last_name": "Lovelace", "email": "a@example.com"},
        files={"resume": ("resume.exe", io.BytesIO(b"not a resume"), "application/octet-stream")},
    )
    assert response.status_code == 400


def test_list_leads_requires_auth(client):
    _submit_lead(client)
    response = client.get("/api/leads")
    assert response.status_code == 401  # no Authorization header supplied


def test_list_leads_with_auth_returns_submitted_lead(client, auth_headers):
    _submit_lead(client)
    response = client.get("/api/leads", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_mark_reached_out_transition(client, auth_headers):
    _submit_lead(client)
    lead_id = client.get("/api/leads", headers=auth_headers).json()[0]["id"]

    response = client.patch(
        f"/api/leads/{lead_id}/status", json={"status": "REACHED_OUT"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "REACHED_OUT"


def test_cannot_transition_reached_out_lead_again(client, auth_headers):
    _submit_lead(client)
    lead_id = client.get("/api/leads", headers=auth_headers).json()[0]["id"]
    client.patch(f"/api/leads/{lead_id}/status", json={"status": "REACHED_OUT"}, headers=auth_headers)

    response = client.patch(
        f"/api/leads/{lead_id}/status", json={"status": "REACHED_OUT"}, headers=auth_headers
    )
    assert response.status_code == 409


def test_login_rejects_wrong_password(client):
    response = client.post(
        "/api/auth/login", json={"email": "attorney@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_lead_notification_goes_to_every_registered_attorney(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "second-attorney@example.com",
            "password": "s3cret-pass",
            "signup_code": settings.attorney_signup_code,
        },
    )

    _submit_lead(client)

    email_files = list(Path(settings.fallback_email_dir).glob("*.txt"))
    notified = {f.read_text().splitlines()[0] for f in email_files}
    assert "To: attorney@example.com" in notified
    assert "To: second-attorney@example.com" in notified
    assert "To: prospect@example.com" in notified
