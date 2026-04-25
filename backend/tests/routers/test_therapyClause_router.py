CLAUSE_PAYLOAD = {
    "number": 1,
    "title": "Behandlungsvertrag",
    "description": "Dieser Vertrag regelt die Behandlung.",
}


def test_get_clauses_empty(client, auth_headers):
    resp = client.get("/therapy-clauses/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_clause(client, auth_headers):
    resp = client.post("/therapy-clauses/", json=CLAUSE_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert "clause_id" in body
    assert body["title"] == "Behandlungsvertrag"
    assert body["number"] == 1


def test_update_clause(client, auth_headers):
    cid = client.post("/therapy-clauses/", json=CLAUSE_PAYLOAD, headers=auth_headers).json()["clause_id"]
    resp = client.patch(f"/therapy-clauses/{cid}", json={"title": "Updated"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


def test_delete_clause(client, auth_headers):
    cid = client.post("/therapy-clauses/", json=CLAUSE_PAYLOAD, headers=auth_headers).json()["clause_id"]
    assert client.delete(f"/therapy-clauses/{cid}", headers=auth_headers).status_code == 204
    clauses = client.get("/therapy-clauses/", headers=auth_headers).json()
    assert not any(c["clause_id"] == cid for c in clauses)


def test_delete_clause_not_found(client, auth_headers):
    assert client.delete("/therapy-clauses/99999", headers=auth_headers).status_code == 404


def test_clauses_require_auth(client):
    assert client.get("/therapy-clauses/").status_code == 401
