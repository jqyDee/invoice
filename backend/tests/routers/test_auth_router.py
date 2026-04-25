def test_login_success(client):
    resp = client.post("/auth/token", data={"username": "testuser", "password": "testpass"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password(client):
    resp = client.post("/auth/token", data={"username": "testuser", "password": "wrong"})
    assert resp.status_code == 401


def test_login_wrong_username(client):
    resp = client.post("/auth/token", data={"username": "nobody", "password": "testpass"})
    assert resp.status_code == 401


def test_refresh_token(client, auth_headers):
    resp = client.post("/auth/refresh", headers=auth_headers)
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_get_me(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


def test_get_me_unauthenticated(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401
