HP_ITEM_PAYLOAD = {
    "description": "Fahrtkosten",
    "amount": 10.0,
    "type": "HP",
    "position": "APPEND",
    "is_active_global": True,
    "quantity": None,
    "number": "GÖÄ 1",
}


def test_get_default_items_empty(client, auth_headers):
    resp = client.get("/invoice_items/defaults", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_default_item(client, auth_headers):
    resp = client.post("/invoice_items/defaults", json=HP_ITEM_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "default_item_id" in body
    assert body["description"] == "Fahrtkosten"
    assert body["type"] == "HP"


def test_get_default_items_all(client, auth_headers):
    client.post("/invoice_items/defaults", json=HP_ITEM_PAYLOAD, headers=auth_headers)
    client.post("/invoice_items/defaults", json={**HP_ITEM_PAYLOAD, "type": "KG"}, headers=auth_headers)
    resp = client.get("/invoice_items/defaults", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_default_items_filtered_by_type(client, auth_headers):
    client.post("/invoice_items/defaults", json=HP_ITEM_PAYLOAD, headers=auth_headers)
    client.post("/invoice_items/defaults", json={**HP_ITEM_PAYLOAD, "type": "KG"}, headers=auth_headers)
    resp = client.get("/invoice_items/defaults?invoice_type=HP", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["type"] == "HP"


def test_toggle_active_state_off(client, auth_headers):
    iid = client.post("/invoice_items/defaults", json=HP_ITEM_PAYLOAD, headers=auth_headers).json()["default_item_id"]
    resp = client.patch(f"/invoice_items/defaults/{iid}?item_active=false", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active_global"] is False


def test_toggle_active_state_on(client, auth_headers):
    iid = client.post("/invoice_items/defaults", json={**HP_ITEM_PAYLOAD, "is_active_global": False}, headers=auth_headers).json()["default_item_id"]
    resp = client.patch(f"/invoice_items/defaults/{iid}?item_active=true", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_active_global"] is True


def test_toggle_not_found(client, auth_headers):
    assert client.patch("/invoice_items/defaults/99999?item_active=false", headers=auth_headers).status_code == 404


def test_invoice_items_require_auth(client):
    assert client.get("/invoice_items/defaults").status_code == 401
