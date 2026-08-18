from mcp_integration.client_manager import (
    mcp_client_manager
)


# =========================================================
# SIMPLE MCP CLIENT TEST
# =========================================================

MCP_SERVER_URL = (
    "http://localhost:8000/mcp"
)


def main():

    server_id = (
        "local-test-server"
    )

    print(
        "Connecting to MCP server..."
    )

    try:

        tools = (
            mcp_client_manager.register_server(

                server_id=server_id,

                name="local_test",

                url=MCP_SERVER_URL

            )
        )

        print(
            "\nMCP connection successful."
        )

        print(
            "\nDiscovered tools:"
        )

        for tool in tools:

            print(
                f"- {tool.name}"
            )

            print(
                f"  Description: "
                f"{tool.description}"
            )

            print(
                f"  Input Schema: "
                f"{tool.input_schema}"
            )

    except Exception as exc:

        print(
            "\nMCP connection failed:"
        )

        print(
            exc
        )


if __name__ == "__main__":

    main()