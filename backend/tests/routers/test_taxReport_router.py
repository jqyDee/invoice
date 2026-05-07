PATIENT_PAYLOAD = {
    "label": "TAX",
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


def _create_paid_invoice(client, auth_headers):
    patient = client.post("/patients/", json=PATIENT_PAYLOAD, headers=auth_headers).json()
    inv = client.post(
        "/invoices/",
        json={
            "patient_id": patient["patient_id"],
            "invoice_date": "2026-03-01",
            "type": "HP",
            "dates": [
                {"date": "2026-02-10", "items": [{"description": "Behandlung", "amount": 50.0, "number": "GÖÄ 1"}]}
            ],
            "default_item_ids": [],
            "save_as_draft": False,
        },
        headers=auth_headers,
    ).json()
    client.post(f"/invoices/{inv['invoice_id']}/payment-due", headers=auth_headers)
    client.post(f"/invoices/{inv['invoice_id']}/paid", json={"paid_at": "2026-03-15"}, headers=auth_headers)
    return inv


def test_get_available_years_empty(client, auth_headers):
    resp = client.get("/tax-report/available-years", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_tax_report_empty_year(client, auth_headers):
    resp = client.get("/tax-report/2026", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_tax_report_csv_empty(client, auth_headers):
    resp = client.get("/tax-report/2026/csv", headers=auth_headers)
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]


def test_available_years_includes_paid_invoice_year(client, auth_headers):
    _create_paid_invoice(client, auth_headers)
    resp = client.get("/tax-report/available-years", headers=auth_headers)
    assert 2026 in resp.json()


def test_tax_report_row_for_paid_invoice(client, auth_headers):
    _create_paid_invoice(client, auth_headers)
    resp = client.get("/tax-report/2026", headers=auth_headers)
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 1
    assert rows[0]["invoice_total"] == 50.0


def test_tax_report_csv_with_data(client, auth_headers):
    _create_paid_invoice(client, auth_headers)
    resp = client.get("/tax-report/2026/csv", headers=auth_headers)
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert "50.0" in resp.text


def test_tax_report_require_auth(client):
    assert client.get("/tax-report/available-years").status_code == 401
