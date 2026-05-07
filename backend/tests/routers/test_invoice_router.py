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


def _make_invoice_payload(patient_id: int, **kwargs):
    return {
        "patient_id": patient_id,
        "invoice_date": "2026-03-01",
        "type": "HP",
        "dates": [
            {
                "date": "2026-02-10",
                "items": [{"description": "Behandlung", "amount": 50.0, "number": "GÖÄ 1"}],
            }
        ],
        "default_item_ids": [],
        "save_as_draft": False,
        **kwargs,
    }


def _setup_patient(client, auth_headers):
    return client.post("/patients/", json=PATIENT_PAYLOAD, headers=auth_headers).json()


def _setup_invoice(client, auth_headers, **kwargs):
    patient = _setup_patient(client, auth_headers)
    resp = client.post("/invoices/", json=_make_invoice_payload(patient["patient_id"], **kwargs), headers=auth_headers)
    assert resp.status_code == 200
    return resp.json()


# ---------------------------------------------------------------------------
# list / get
# ---------------------------------------------------------------------------


def test_get_invoices_empty(client, auth_headers):
    resp = client.get("/invoices/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == {"items": [], "total": 0}


def test_get_invoice_not_found(client, auth_headers):
    assert client.get("/invoices/99999", headers=auth_headers).status_code == 404


def test_get_invoice(client, auth_headers):
    inv = _setup_invoice(client, auth_headers)
    resp = client.get(f"/invoices/{inv['invoice_id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["invoice_id"] == inv["invoice_id"]


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


def test_create_hp_invoice(client, auth_headers):
    inv = _setup_invoice(client, auth_headers)
    assert inv["type"] == "HP"
    assert inv["status"] == "SAVED"
    assert inv["invoice_number"] is not None


def test_create_draft_invoice(client, auth_headers):
    inv = _setup_invoice(client, auth_headers, save_as_draft=True)
    assert inv["status"] == "DRAFT"
    assert inv["invoice_number"] is None


def test_create_kg_invoice(client, auth_headers):
    patient = _setup_patient(client, auth_headers)
    payload = {
        "patient_id": patient["patient_id"],
        "invoice_date": "2026-03-01",
        "type": "KG",
        "dates": [
            {"date": "2026-02-05"},
            {"date": "2026-02-12"},
        ],
        "user_items": [{"description": "KG Behandlung", "amount": 30.0, "quantity": 2}],
        "default_item_ids": [],
        "save_as_draft": False,
    }
    resp = client.post("/invoices/", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["type"] == "KG"


def test_get_invoices_list_contains_created(client, auth_headers):
    inv = _setup_invoice(client, auth_headers)
    resp = client.get("/invoices/", headers=auth_headers)
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["invoice_id"] == inv["invoice_id"]


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


def test_update_invoice_diagnosis(client, auth_headers):
    inv = _setup_invoice(client, auth_headers)
    resp = client.patch(f"/invoices/{inv['invoice_id']}", json={"diagnosis": "Rückenschmerzen"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["diagnosis"] == "Rückenschmerzen"


# ---------------------------------------------------------------------------
# status transitions
# ---------------------------------------------------------------------------


def test_set_payment_due(client, auth_headers):
    inv = _setup_invoice(client, auth_headers)
    resp = client.post(f"/invoices/{inv['invoice_id']}/payment-due", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "PAYMENT_DUE"


def test_set_paid(client, auth_headers):
    inv = _setup_invoice(client, auth_headers)
    client.post(f"/invoices/{inv['invoice_id']}/payment-due", headers=auth_headers)
    resp = client.post(f"/invoices/{inv['invoice_id']}/paid", json={"paid_at": "2026-03-15"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "PAID"
    assert resp.json()["paid_at"] == "2026-03-15"


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


def test_delete_draft_invoice(client, auth_headers):
    inv = _setup_invoice(client, auth_headers, save_as_draft=True)
    resp = client.delete(f"/invoices/{inv['invoice_id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert client.get(f"/invoices/{inv['invoice_id']}", headers=auth_headers).status_code == 404


def test_delete_locked_invoice(client, auth_headers):
    inv = _setup_invoice(client, auth_headers)
    client.post(f"/invoices/{inv['invoice_id']}/payment-due", headers=auth_headers)
    resp = client.delete(f"/invoices/{inv['invoice_id']}", headers=auth_headers)
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# templates
# ---------------------------------------------------------------------------


def test_get_template_items_empty(client, auth_headers):
    resp = client.get("/invoices/template-items?invoice_type=HP", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_template_items_with_data(client, auth_headers):
    _setup_invoice(client, auth_headers)
    resp = client.get("/invoices/template-items?invoice_type=HP", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_get_template_diagnoses_empty(client, auth_headers):
    resp = client.get("/invoices/template-diagnoses", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_invoice_template(client, auth_headers):
    inv = _setup_invoice(client, auth_headers)
    resp = client.get(f"/invoices/{inv['invoice_id']}/template", headers=auth_headers)
    assert resp.status_code == 200
    assert "type" in resp.json()


# ---------------------------------------------------------------------------
# auth guard
# ---------------------------------------------------------------------------


def test_invoices_require_auth(client):
    assert client.get("/invoices/").status_code == 401
