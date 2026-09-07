def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Welcome to Student Assistant RAG API"
    assert data["version"] == "1.0"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "success"


def test_query_requires_body(client):
    response = client.post("/query")
    assert response.status_code == 400


def test_query_requires_question(client):
    response = client.post("/query", json={"tenant_id": "t1"})
    assert response.status_code == 400


def test_query_requires_tenant(client):
    response = client.post("/query", json={"question": "hello"})
    assert response.status_code == 400


def test_api_key_auth_blocks_unauthorized_requests(app):
    app.config["API_KEY"] = "secret-key"
    client = app.test_client()

    # No header -> rejected
    response = client.get("/query")
    assert response.status_code == 401

    # Valid header -> passes auth (405 because GET is not allowed on /query)
    response = client.get("/query", headers={"X-API-Key": "secret-key"})
    assert response.status_code == 405
