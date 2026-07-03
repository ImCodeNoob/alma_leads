import io


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
