CLAUSE_PAYLOAD = {
    "number": 1,
    "title": "Datenschutz",
    "description": "Ihre Daten werden vertraulich behandelt.",
    "is_preamble": False,
}


def test_get_clauses_empty(client, auth_headers):
    resp = client.get("/privacy-clauses/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_clause(client, auth_headers):
    resp = client.post("/privacy-clauses/", json=CLAUSE_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert "clause_id" in body
    assert body["title"] == "Datenschutz"
    assert body["is_preamble"] is False


def test_update_clause(client, auth_headers):
    cid = client.post("/privacy-clauses/", json=CLAUSE_PAYLOAD, headers=auth_headers).json()["clause_id"]
    resp = client.patch(f"/privacy-clauses/{cid}", json={"is_preamble": True}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_preamble"] is True


def test_delete_clause(client, auth_headers):
    cid = client.post("/privacy-clauses/", json=CLAUSE_PAYLOAD, headers=auth_headers).json()["clause_id"]
    assert client.delete(f"/privacy-clauses/{cid}", headers=auth_headers).status_code == 204
    clauses = client.get("/privacy-clauses/", headers=auth_headers).json()
    assert not any(c["clause_id"] == cid for c in clauses)


def test_delete_clause_not_found(client, auth_headers):
    assert client.delete("/privacy-clauses/99999", headers=auth_headers).status_code == 404


def test_clauses_require_auth(client):
    assert client.get("/privacy-clauses/").status_code == 401
