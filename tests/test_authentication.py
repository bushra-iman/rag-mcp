import asyncio

from mcp_integration.authentication import MCPAuthentication


def test_no_authentication_returns_empty_headers():
    assert asyncio.run(MCPAuthentication.get_headers(None)) == {}


def test_bearer_headers():
    headers = asyncio.run(
        MCPAuthentication.get_headers(
            {"type": "bearer", "token": "abc123"}
        )
    )
    assert headers == {"Authorization": "Bearer abc123"}


def test_bearer_requires_token():
    try:
        asyncio.run(MCPAuthentication.get_headers({"type": "bearer"}))
    except ValueError as exc:
        assert "Bearer token is required" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_unsupported_auth_type():
    try:
        asyncio.run(MCPAuthentication.get_headers({"type": "api_key"}))
    except ValueError as exc:
        assert "Unsupported authentication type" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_oauth2_headers(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"access_token": "mock-token"}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args, **kwargs):
            return None

        async def post(self, *args, **kwargs):
            return FakeResponse()

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)

    headers = asyncio.run(
        MCPAuthentication.get_headers(
            {
                "type": "oauth2",
                "token_endpoint": "http://localhost:7000/oauth/token",
                "client_id": "1234",
                "client_secret": "client-secret",
                "grant_type": "client_credentials",
            }
        )
    )
    assert headers == {"Authorization": "Bearer mock-token"}
