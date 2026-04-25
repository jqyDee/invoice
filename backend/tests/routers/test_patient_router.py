PATIENT_PAYLOAD = {
    "label": "TEST",
    "first_name": "Max",
    "last_name": "Mustermann",
    "gender": "MALE",
    "street": "Musterstraße",
    "street_number": "1",
    "postal_code": "12345",
    "city": "Berlin",
    "birthday": "1990-01-01",
    "kilometers_to_travel": 10.0,
}


def test_get_patients_empty(client, auth_headers):
    resp = client.get("/patients/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == {"items": [], "total": 0}


def test_create_patient(client, auth_headers):
    resp = client.post("/patients/", json=PATIENT_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "patient_id" in body
    assert body["first_name"] == "Max"
    assert body["last_name"] == "Mustermann"


def test_get_patient(client, auth_headers):
    pid = client.post("/patients/", json=PATIENT_PAYLOAD, headers=auth_headers).json()["patient_id"]
    resp = client.get(f"/patients/{pid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["patient_id"] == pid


def test_get_patient_not_found(client, auth_headers):
    resp = client.get("/patients/99999", headers=auth_headers)
    assert resp.status_code == 404


def test_update_patient(client, auth_headers):
    pid = client.post("/patients/", json=PATIENT_PAYLOAD, headers=auth_headers).json()["patient_id"]
    resp = client.put(f"/patients/{pid}", json={**PATIENT_PAYLOAD, "first_name": "Moritz"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Moritz"


def test_delete_patient(client, auth_headers):
    pid = client.post("/patients/", json=PATIENT_PAYLOAD, headers=auth_headers).json()["patient_id"]
    resp = client.delete(f"/patients/{pid}", headers=auth_headers)
    assert resp.status_code == 200
    assert client.get(f"/patients/{pid}", headers=auth_headers).status_code == 404


def test_get_patients_search(client, auth_headers):
    client.post("/patients/", json=PATIENT_PAYLOAD, headers=auth_headers)
    client.post("/patients/", json={**PATIENT_PAYLOAD, "first_name": "Anna", "last_name": "Schmidt"}, headers=auth_headers)
    resp = client.get("/patients/?search=Schmidt", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["last_name"] == "Schmidt"


def test_get_patients_pagination(client, auth_headers):
    for i in range(5):
        client.post("/patients/", json={**PATIENT_PAYLOAD, "label": f"P{i}"}, headers=auth_headers)
    resp = client.get("/patients/?page=1&size=2", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


def test_patients_require_auth(client):
    assert client.get("/patients/").status_code == 401
