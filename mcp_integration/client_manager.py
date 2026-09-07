import asyncio
import threading
from typing import Any
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp_integration.authentication import ( MCPAuthentication )
class MCPClientManager:
    """
    Manages multiple external MCP servers.
    Responsibilities:
    - Register MCP servers
    - Connect to MCP servers
    - Discover MCP tools
    - Refresh MCP tools
    - Execute MCP tools
    - Handle authentication
    - Handle unavailable servers
    """
    def __init__(self):
        self.servers: dict[str, dict[str, Any]] = {}
    # =========================================================
    # ASYNCIO HELPER
    # =========================================================
    def _run_async(self, coroutine):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coroutine)
        result = []
        error = []
        def runner():
            try:
                result.append(
                    asyncio.run(coroutine)
                )
            except Exception as exc:
                error.append(exc)
        thread = threading.Thread(
            target=runner,
            daemon=True
        )
        thread.start()
        thread.join()
        if error:
            raise error[0]
        if not result:
            raise RuntimeError(
                "Async MCP operation returned no result."
            )
        return result[0]
    # =========================================================
    # REGISTER SERVER
    # =========================================================
    def register_server(
        self,
        server_id: str,
        name: str,
        url: str,
        authentication: dict | None = None
    ):
        server = {
            "id": server_id,
            "name": name,
            "url": url,
            "authentication": authentication or {},
            "status": "registered"
        }
        self.servers[server_id] = server
        try:
            tools = self.discover_tools(
                server_id
            )
            server["status"] = "connected"
            return tools
        except Exception as exc:
            server["status"] = "unavailable"
            raise RuntimeError(
                f"Unable to register MCP server "
                f"'{name}': {type(exc).__name__}: {exc}"
            ) from exc
    # =========================================================
    # REMOVE SERVER
    # =========================================================
    def remove_server(
        self,
        server_id: str
    ):
        if server_id not in self.servers:
            raise ValueError(
                f"MCP server '{server_id}' is not registered."
            )
        del self.servers[server_id]
    # =========================================================
    # GET SERVER
    # =========================================================
    def get_server(
        self,
        server_id: str
    ):
        server = self.servers.get(
            server_id
        )
        if server is None:
            raise ValueError(
                f"MCP server '{server_id}' is not registered."
            )
        return server

        # =====================================================
    # AUTHENTICATION HEADERS
    # =====================================================
    async def _get_headers_async(
        self,
        server: dict
    ) -> dict[str, str]:
        if not isinstance(
            server,
            dict
        ):
            return {}
        authentication = server.get(
            "authentication"
        )
        if not isinstance(
            authentication,
            dict
        ):
            return {}
        return await MCPAuthentication.get_headers(
            authentication
        )
    # =========================================================
    # DISCOVER TOOLS - ASYNC
    # =========================================================
    async def _discover_tools_async(
        self,
        server: dict
    ):
        if not isinstance(
            server,
            dict
        ):
            raise ValueError(
                "Invalid MCP server configuration."
            )

        url = server.get(
            "url"
        )
        if not url:
            raise ValueError(
                "MCP server URL is missing."
            )
        headers = await self._get_headers_async(
            server
        )
        async with httpx.AsyncClient(
            headers=headers,
            timeout=30,
            follow_redirects=True
        ) as http_client:
            async with streamable_http_client(
                url,
                http_client=http_client
            ) as streams:
                if not streams or len(streams) < 2:
                    raise RuntimeError(
                        "MCP server did not return "
                        "valid communication streams."
                    )
                read_stream = streams[0]
                write_stream = streams[1]
                async with ClientSession(
                    read_stream,
                    write_stream
                ) as session:
                    await session.initialize()
                    response = await session.list_tools()
                    if response is None:
                        return []
                    discovered_tools = getattr(
                        response,
                        "tools",
                        None
                    )
                    if discovered_tools is None:
                        return []
                    return list(
                        discovered_tools
                    )
    # =========================================================
    # DISCOVER TOOLS
    # =========================================================
    def discover_tools(
        self,
        server_id: str
    ):
        server = self.get_server(
            server_id
        )
        try:
            tools = self._run_async(
                self._discover_tools_async(
                    server
                )
            )
            if tools is None:
                tools = []
            server["status"] = "connected"
            return tools
        except Exception as exc:
            server["status"] = "unavailable"
            import traceback
            traceback.print_exc()
            raise RuntimeError(
                "Unable to connect to MCP server "
                f"'{server.get('name', server_id)}': "
                f"{type(exc).__name__}: {exc}"
            ) from exc
    # =========================================================
    # CALL MCP TOOL - ASYNC
    # =========================================================
    async def _call_tool_async(
        self,
        server: dict,
        tool_name: str,
        arguments: dict | None
    ):
        if not isinstance(
            server,
            dict
        ):
            raise ValueError(
                "Invalid MCP server configuration."
            )
        url = server.get(
            "url"
        )
        if not url:
            raise ValueError(
                "MCP server URL is missing."
            )
        if not tool_name:
            raise ValueError(
                "MCP tool name is missing."
            )
        if arguments is None:
            arguments = {}
        if not isinstance(
            arguments,
            dict
        ):
            raise ValueError(
                "MCP tool arguments must be a dictionary."
            )
        headers = await self._get_headers_async(
            server
        )
        async with httpx.AsyncClient(
            headers=headers,
            timeout=60,
            follow_redirects=True
        ) as http_client:
            async with streamable_http_client(
                url,
                http_client=http_client
            ) as streams:
                if not streams or len(streams) < 2:
                    raise RuntimeError(
                        "MCP server did not return "
                        "valid communication streams."
                    )
                read_stream = streams[0]
                write_stream = streams[1]
                async with ClientSession(
                    read_stream,
                    write_stream
                ) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        tool_name,
                        arguments=arguments
                    )
                    if result is None:
                        raise RuntimeError(
                            "MCP server returned no result."
                        )
                    return result
    # =========================================================
    # CALL MCP TOOL
    # =========================================================
    def call_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: dict | None = None
    ):
        server = self.get_server(
            server_id
        )
        if arguments is None:
            arguments = {}
        try:
            result = self._run_async(
                self._call_tool_async(
                    server,
                    tool_name,
                    arguments
                )
            )
            server["status"] = "connected"
            return self._format_result(
                result
            )
        except Exception as exc:
            server["status"] = "unavailable"
            server_name = server.get(
                "name",
                server_id
            )
            return (
                "MCP tool execution failed. "
                f"Server: {server_name}. "
                f"Tool: {tool_name}. "
                f"Error: {type(exc).__name__}: {exc}"
            )
    # =========================================================
    # FORMAT MCP RESULT
    # =========================================================
    def _format_result(
        self,
        result
    ):
        if result is None:
            return (
                "MCP tool returned no result."
            )
        # -----------------------------------------------------
        # Structured content
        # -----------------------------------------------------
        structured_content = getattr(
            result,
            "structured_content",
            None
        )
        if structured_content is not None:
            return str(
                structured_content
            )
        # -----------------------------------------------------
        # Alternative SDK naming
        # -----------------------------------------------------
        structured_content = getattr(
            result,
            "structuredContent",
            None
        )
        if structured_content is not None:
            return str(
                structured_content
            )
        # -----------------------------------------------------
        # Normal MCP content blocks
        # -----------------------------------------------------
        content = getattr(
            result,
            "content",
            None
        )
        if content is None:
            return str(
                result
            )
        output = []
        for block in content:
            if block is None:
                continue
            text = getattr(
                block,
                "text",
                None
            )
            if text is not None:
                output.append(
                    str(text)
                )
        if output:
            return "\n".join(
                output
            )
        return str(
            result
        )
    # =========================================================
    # REFRESH TOOLS
    # =========================================================
    def refresh_server(
        self,
        server_id: str
    ):
        return self.discover_tools(
            server_id
        )
    # =========================================================
    # LIST SERVERS
    # =========================================================
    def list_servers(self):
        return [
            {
                "id":
                    server.get(
                        "id"
                    ),

                "name":
                    server.get(
                        "name"
                    ),

                "url":
                    server.get(
                        "url"
                    ),

                "status":
                    server.get(
                        "status",
                        "unknown"
                    )
            }
            for server
            in self.servers.values()
        ]
# =========================================================
# GLOBAL MCP CLIENT MANAGER
# =========================================================
mcp_client_manager = MCPClientManager()
