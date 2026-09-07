import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"


async def test_mcp_server():

    print("\nConnecting to MCP server...")
    print("URL:", MCP_SERVER_URL)

    async with streamable_http_client(
        MCP_SERVER_URL
    ) as (
        read_stream,
        write_stream
    ):

        async with ClientSession(
            read_stream,
            write_stream
        ) as session:

            print("\nInitializing MCP session...")

            await session.initialize()

            print(
                "MCP session initialized successfully."
            )

            print("\nDiscovering tools...")

            response = await session.list_tools()

            print(
                f"\nTotal tools discovered: "
                f"{len(response.tools)}"
            )

            print("\nAvailable MCP tools:")

            for tool in response.tools:

                print("\n----------------------------")

                print("Name:")
                print(tool.name)

                print("\nDescription:")
                print(tool.description)

                print("\nInput Schema:")
                print(tool.input_schema)

                print("----------------------------")


if __name__ == "__main__":

    asyncio.run(
        test_mcp_server()
    )
