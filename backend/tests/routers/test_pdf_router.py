import pytest

PATIENT_PAYLOAD = {
    "label": "PDF",
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

SETTINGS_PAYLOAD = {
    "iban": "DE12345678901234567890",
    "bic": "TESTDE11",
    "tax_id": "12345678901",
    "price_from": 100.0,
    "price_to": 110.0,
}


@pytest.fixture
def pdf_mocks(tmp_path, monkeypatch):
    """Redirect all PDF writes to tmp_path and mock generation functions."""

    def mock_gen_invoice(inv):
        return tmp_path / f"{inv.invoice_number}.pdf"

    def mock_regen_invoice(inv, settings, pdf_path, db):
        pdf_path.write_bytes(b"%PDF-1.4 mock")

    def mock_gen_therapy(p):
        return tmp_path / f"{p.patient_id}-{p.label}-therapy.pdf"

    def mock_regen_therapy(p, settings, db):
        (tmp_path / f"{p.patient_id}-{p.label}-therapy.pdf").write_bytes(b"%PDF-1.4 mock")

    def mock_gen_privacy(p):
        return tmp_path / f"{p.patient_id}-{p.label}-privacy.pdf"

    def mock_regen_privacy(p, db):
        (tmp_path / f"{p.patient_id}-{p.label}-privacy.pdf").write_bytes(b"%PDF-1.4 mock")

    monkeypatch.setattr("app.routers.pdf_router.generate_invoice_path", mock_gen_invoice)
    monkeypatch.setattr("app.routers.pdf_router.check_and_regenerate_invoice_pdf", mock_regen_invoice)
    monkeypatch.setattr("app.routers.pdf_router.generate_therapy_path", mock_gen_therapy)
    monkeypatch.setattr("app.routers.pdf_router.check_and_regenerate_therapy_pdf", mock_regen_therapy)
    monkeypatch.setattr("app.routers.pdf_router.generate_privacy_path", mock_gen_privacy)
    monkeypatch.setattr("app.routers.pdf_router.check_and_regenerate_privacy_pdf", mock_regen_privacy)


@pytest.fixture
def pdf_setup(client, auth_headers, pdf_mocks):
    """Create settings + patient + HP invoice in the test DB."""
    client.patch("/settings/", json=SETTINGS_PAYLOAD, headers=auth_headers)
    patient = client.post("/patients/", json=PATIENT_PAYLOAD, headers=auth_headers).json()
    invoice = client.post("/invoices/", json={
        "patient_id": patient["patient_id"],
        "invoice_date": "2026-03-01",
        "type": "HP",
        "dates": [{"date": "2026-02-10", "items": [{"description": "Behandlung", "amount": 50.0, "number": "GÖÄ 1"}]}],
        "default_item_ids": [],
        "save_as_draft": False,
    }, headers=auth_headers).json()
    return {"patient": patient, "invoice": invoice}


# ---------------------------------------------------------------------------
# invoice PDF
# ---------------------------------------------------------------------------

def test_get_invoice_pdf_no_settings(client, auth_headers, pdf_mocks):
    patient = client.post("/patients/", json=PATIENT_PAYLOAD, headers=auth_headers).json()
    inv = client.post("/invoices/", json={
        "patient_id": patient["patient_id"],
        "invoice_date": "2026-03-01",
        "type": "HP",
        "dates": [{"date": "2026-02-10", "items": [{"description": "Behandlung", "amount": 50.0, "number": "GÖÄ 1"}]}],
        "default_item_ids": [],
        "save_as_draft": False,
    }, headers=auth_headers).json()
    resp = client.get(f"/pdf/invoice/{inv['invoice_id']}", headers=auth_headers)
    assert resp.status_code == 404


def test_get_invoice_pdf(client, auth_headers, pdf_setup):
    inv_id = pdf_setup["invoice"]["invoice_id"]
    resp = client.get(f"/pdf/invoice/{inv_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"


def test_get_invoice_pdf_not_found(client, auth_headers, pdf_mocks):
    client.patch("/settings/", json=SETTINGS_PAYLOAD, headers=auth_headers)
    resp = client.get("/pdf/invoice/99999", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# therapy PDF
# ---------------------------------------------------------------------------

def test_get_therapy_pdf_no_settings(client, auth_headers, pdf_mocks):
    patient = client.post("/patients/", json=PATIENT_PAYLOAD, headers=auth_headers).json()
    resp = client.get(f"/pdf/therapy/{patient['patient_id']}", headers=auth_headers)
    assert resp.status_code == 404


def test_get_therapy_pdf(client, auth_headers, pdf_setup):
    patient_id = pdf_setup["patient"]["patient_id"]
    resp = client.get(f"/pdf/therapy/{patient_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"


def test_get_therapy_pdf_patient_not_found(client, auth_headers, pdf_mocks):
    client.patch("/settings/", json=SETTINGS_PAYLOAD, headers=auth_headers)
    assert client.get("/pdf/therapy/99999", headers=auth_headers).status_code == 404


# ---------------------------------------------------------------------------
# privacy PDF
# ---------------------------------------------------------------------------

def test_get_privacy_pdf(client, auth_headers, pdf_setup):
    patient_id = pdf_setup["patient"]["patient_id"]
    resp = client.get(f"/pdf/privacy/{patient_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"


def test_get_privacy_pdf_patient_not_found(client, auth_headers, pdf_mocks):
    assert client.get("/pdf/privacy/99999", headers=auth_headers).status_code == 404


# ---------------------------------------------------------------------------
# auth guard
# ---------------------------------------------------------------------------

def test_pdf_require_auth(client):
    assert client.get("/pdf/invoice/1").status_code == 401
