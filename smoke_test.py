r"""
Smoke test for the Student Assistant RAG API.

Checks that all servers are up and responding so you can confirm
everything is ready to test in Postman.

Usage:
    venv\Scripts\python smoke_test.py
"""

import asyncio
import sys

import httpx

from config import Config


# Status codes that indicate a healthy, reachable endpoint.
# Some endpoints are expected to reject "empty/minimal" requests with
# 4xx (e.g. validation errors) - that still proves the server is up.
HEALTHY_STATUSES = {200, 201, 400, 401, 404, 405, 406, 422}


def check(name: str, url: str, method: str = "GET", **kwargs) -> None:
    """Perform a request and print PASS/FAIL with the status code."""
    try:
        response = httpx.request(method, url, timeout=10, **kwargs)
        status = response.status_code
        if status in HEALTHY_STATUSES:
            print(f"  [PASS] {name:<25} {method} {url} -> {status}")
            if kwargs.get("json"):
                print(f"         body -> {kwargs['json']}")
        else:
            print(f"  [FAIL] {name:<25} {method} {url} -> {status}")
    except Exception as exc:
        print(f"  [FAIL] {name:<25} {method} {url} -> {type(exc).__name__}: {exc}")


def check_mcp_tools(mcp_url: str) -> None:
    """Connect to the MCP server with the SDK and list its tools."""
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    async def _run() -> int:
        async with streamable_http_client(mcp_url) as streams:
            # SDK yields (read_stream, write_stream, get_session_id_callback)
            read_stream, write_stream = streams[0], streams[1]
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                response = await session.list_tools()
                tools = [t.name for t in response.tools]
                print(f"  [PASS] MCP tool list           {mcp_url}")
                print(f"         discovered tools -> {tools}")
                return len(tools)

    try:
        count = asyncio.run(_run())
        if count == 0:
            print("  [WARN] MCP server is reachable but returned no tools.")
    except Exception as exc:
        print(f"  [FAIL] MCP tool list           {mcp_url} -> {type(exc).__name__}: {exc}")


def main() -> None:
    base = f"http://127.0.0.1:{Config.PORT}"
    mcp_url = f"http://127.0.0.1:{Config.MCP_PORT}/mcp"
    oauth_url = f"http://127.0.0.1:{Config.OAUTH_PORT}"

    print("=" * 60)
    print(" Student Assistant RAG API - smoke test")
    print(f" RAG API : {base}")
    print(f" MCP     : {mcp_url}")
    print(f" OAuth   : {oauth_url}")
    print("=" * 60)

    headers = {}
    if Config.API_KEY:
        headers["X-API-Key"] = Config.API_KEY

    # -----------------------------------------------------------------
    # 1. RAG API
    # -----------------------------------------------------------------
    print("\n[1] RAG API")
    check("Home", f"{base}/")
    check("Health", f"{base}/health")
    check(
        "Query (empty body)",
        f"{base}/query",
        method="POST",
        json={},
        headers=headers,
    )
    check(
        "Threads",
        f"{base}/threads?tenant_id=test-tenant",
        headers=headers,
    )
    check(
        "MCP tools",
        f"{base}/api/mcp/tools",
        headers=headers,
    )

    # -----------------------------------------------------------------
    # 2. Standalone MCP server (proper SDK handshake)
    # -----------------------------------------------------------------
    print("\n[2] Standalone MCP server (streamable HTTP)")
    check_mcp_tools(mcp_url)

    # -----------------------------------------------------------------
    # 3. Mock OAuth server
    # -----------------------------------------------------------------
    print("\n[3] Mock OAuth server")
    check("OAuth health", oauth_url)

    print("\nIf any check FAILED, make sure all servers are running")
    print("(double-click run_all.bat) and ports in .env are correct.")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
