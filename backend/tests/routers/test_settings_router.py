SETTINGS_PAYLOAD = {
    "iban": "DE12345678901234567890",
    "bic": "TESTDE11",
    "tax_id": "12345678901",
    "price_from": 100.0,
    "price_to": 110.0,
}


def test_get_settings_empty(client, auth_headers):
    resp = client.get("/settings/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() is None


def test_create_settings(client, auth_headers):
    resp = client.patch("/settings/", json=SETTINGS_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "settings_id" in body
    assert body["bic"] == "TESTDE11"


def test_update_settings_keeps_same_id(client, auth_headers):
    first = client.patch("/settings/", json=SETTINGS_PAYLOAD, headers=auth_headers).json()
    second = client.patch("/settings/", json={**SETTINGS_PAYLOAD, "price_from": 120.0}, headers=auth_headers).json()
    assert second["settings_id"] == first["settings_id"]
    assert second["price_from"] == 120.0


def test_get_settings_after_create(client, auth_headers):
    client.patch("/settings/", json=SETTINGS_PAYLOAD, headers=auth_headers)
    resp = client.get("/settings/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["bic"] == "TESTDE11"


def test_settings_invalid_iban(client, auth_headers):
    resp = client.patch("/settings/", json={**SETTINGS_PAYLOAD, "iban": "INVALID"}, headers=auth_headers)
    assert resp.status_code == 422


def test_settings_invalid_bic(client, auth_headers):
    resp = client.patch("/settings/", json={**SETTINGS_PAYLOAD, "bic": "X"}, headers=auth_headers)
    assert resp.status_code == 422


def test_settings_invalid_tax_id(client, auth_headers):
    resp = client.patch("/settings/", json={**SETTINGS_PAYLOAD, "tax_id": "123"}, headers=auth_headers)
    assert resp.status_code == 422


def test_settings_require_auth(client):
    assert client.get("/settings/").status_code == 401
