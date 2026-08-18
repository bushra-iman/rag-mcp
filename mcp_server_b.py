from typing import Annotated
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings 
# mcp = FastMCP(
#     "MCP Server B"
# )
mcp = FastMCP(
    "MCP Server",
    host="0.0.0.0",
    port=8000,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "localhost",
            "127.0.0.1",
            "amuser-frown-passcode.ngrok-free.dev",
        ],
        allowed_origins=[
            "https://amuser-frown-passcode.ngrok-free.dev",
        ],
    ),
)
@mcp.tool()
def get_server_b_status() -> str:
    """
    Returns a status message from MCP Server B.
    """
    return "MCP SERVER B IS WORKING SUCCESSFULLY"


@mcp.tool()
def calculate_number(
    number: Annotated[
        int,
        "Number to calculate."
    ]
) -> str:
    """
    Performs a simple calculation on the supplied number.
    """
    result = number * 2

    return (
        f"Server B calculated {number} x 2 = {result}"
    )

# if __name__ == "__main__":
#     mcp.settings.host = "127.0.0.1"
#     mcp.settings.port = 8001

#     mcp.run(
#         transport="streamable-http"
#     )
if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000

    mcp.run(
        transport="streamable-http"
    )