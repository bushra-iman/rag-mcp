from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from services.rag_engine import (
    search_knowledge_base,
    search_web_tool
)


# =========================================================
# MCP SERVER
# =========================================================

mcp = FastMCP(
    "Student Assistant MCP",
    host="0.0.0.0",
    port=8000,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


# =========================================================
# MCP TOOL 1
# =========================================================

@mcp.tool()
def search_uploaded_documents(
    question: Annotated[
        str,
        "Question or keywords to search in uploaded documents."
    ]
) -> str:
    """
    Search uploaded documents through MCP.
    """
    return search_knowledge_base(question)


# =========================================================
# MCP TOOL 2
# =========================================================

@mcp.tool()
def search_web(
    question: Annotated[
        str,
        "Search the web for current information."
    ]
) -> str:
    """
    Search the web through MCP.
    """
    return search_web_tool(question)


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http"
    )


# from typing import Annotated
# from mcp.server.fastmcp import FastMCP

# from services.rag_engine import (
#     search_knowledge_base,
#     search_web_tool
# )


# # =========================================================
# # MCP SERVER
# # =========================================================

# mcp = FastMCP(
#     "Student Assistant MCP"
# )


# # =========================================================
# # MCP TOOL 1
# # =========================================================

# @mcp.tool()
# def search_uploaded_documents(
#     question: Annotated[
#         str,
#         "Question or keywords to search in uploaded documents."
#     ]
# ) -> str:
#     """
#     Search uploaded documents through MCP.
#     """
#     return search_knowledge_base(question)


# # =========================================================
# # MCP TOOL 2
# # =========================================================

# @mcp.tool()
# def search_web(
#     question: Annotated[
#         str,
#         "Search the web for current information."
#     ]
# ) -> str:
#     """
#     Search the web through MCP.
#     """
#     return search_web_tool(question)


# # =========================================================
# # MCP TOOL 3
# # =========================================================

# @mcp.tool()
# def mcp_server_status() -> str:
#     """
#     Returns a status message from the MCP server.
#     """
#     return "MCP SERVER IS WORKING SUCCESSFULLY"


# # =========================================================
# # START SERVER
# # =========================================================

# if __name__ == "__main__":

#     mcp.run(
#     transport="streamable-http"
# )