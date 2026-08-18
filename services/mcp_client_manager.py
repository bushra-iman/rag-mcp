import asyncio
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class MCPClientManager:
    """
    Manages connections to multiple external MCP servers.

    Responsibilities:
    - Connect to MCP servers
    - Initialize MCP sessions
    - Discover tools
    - Refresh tools
    - Execute MCP tools
    - Disconnect from servers
    """

    def __init__(self):
        self.servers = {}

    async def connect(self, server_id: str, url: str):
        """
        Connect to an external MCP server and initialize its session.
        """

        if server_id in self.servers:
            return self.servers[server_id]

        transport = await streamable_http_client(url).__aenter__()

        read_stream = transport[0]
        write_stream = transport[1]
        session = ClientSession(
            read_stream,
            write_stream
        )

        await session.__aenter__()
        await session.initialize()

        self.servers[server_id] = {
            "url": url,
            "transport": transport,
            "session": session
        }

        return self.servers[server_id]

    async def disconnect(self, server_id: str):
        """
        Disconnect an MCP server.
        """

        server = self.servers.get(server_id)

        if not server:
            return

        session = server["session"]
        transport = server["transport"]

        try:
            await session.__aexit__(
                None,
                None,
                None
            )
        finally:
            await streamable_http_client(url=server["url"]).__aexit__(
                None,
                None,
                None
            )

        del self.servers[server_id]

    async def list_tools(self, server_id: str):
        """
        Discover tools exposed by an MCP server.
        """

        server = self.servers.get(server_id)

        if not server:
            raise ValueError(
                f"MCP server '{server_id}' is not connected."
            )

        session = server["session"]

        response = await session.list_tools()

        return response.tools

    async def refresh_tools(self, server_id: str):
        """
        Re-discover tools from an MCP server.
        """

        return await self.list_tools(server_id)

    async def call_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: dict[str, Any]
    ):
        """
        Execute an MCP tool.
        """

        server = self.servers.get(server_id)

        if not server:
            raise ValueError(
                f"MCP server '{server_id}' is not connected."
            )

        session = server["session"]

        result = await session.call_tool(
            tool_name,
            arguments=arguments
        )

        return result

    def get_servers(self):
        """
        Return currently connected MCP servers.
        """

        return {
            server_id: {
                "url": server["url"]
            }
            for server_id, server in self.servers.items()
        }


# Global MCP client manager
mcp_client_manager = MCPClientManager()