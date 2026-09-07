from flask import (
    Blueprint,
    current_app,
    request,
    jsonify
)
import uuid
from mcp_integration.client_manager import (
    mcp_client_manager
)
from mcp_integration.tool_registry import (
    mcp_tool_registry
)
mcp_bp = Blueprint(
    "mcp",
    __name__,
    url_prefix="/api/mcp"
)
# =========================================================
# REGISTER MCP SERVER
# =========================================================
# =========================================================
# REGISTER MCP SERVER
# =========================================================
@mcp_bp.route(
    "/servers",
    methods=["POST"]
)
def register_mcp_server():

    data = request.get_json(
        silent=True
    )

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body is required."
        }), 400

    name = data.get("name")
    url = data.get("url")
    authentication = data.get("authentication")

    if not name:
        return jsonify({
            "status": "error",
            "message": "Server name is required."
        }), 400

    if not url:
        return jsonify({
            "status": "error",
            "message": "Server URL is required."
        }), 400

    server_id = str(
        uuid.uuid4()
    )

    try:
        tools = mcp_client_manager.register_server(
            server_id=server_id,
            name=name,
            url=url,
            authentication=authentication
        )

        mcp_tool_registry.register_server(
            server_id=server_id,
            name=name,
            url=url
        )

        mcp_tool_registry.register_tools(
            server_id=server_id,
            server_name=name,
            tools=tools
        )

        registered_tools = (
            mcp_tool_registry.get_server_tools(
                server_id
            )
        )

        return jsonify({
            "status": "success",
            "message": "MCP server registered successfully.",
            "server_id": server_id,
            "server_name": name,
            "url": url,
            "status_detail": "connected",
            "tools_discovered": len(registered_tools),
            "tools": [
                {
                    "name": tool["exposed_name"],
                    "original_name": tool["name"],
                    "description": tool["description"]
                }
                for tool in registered_tools
            ]
        }), 201

    except Exception as exc:

        current_app.logger.exception(
            "Unable to register MCP server: %s",
            exc
        )

        return jsonify({
            "status": "error",
            "message": "Unable to connect to MCP server.",
            "server_name": name,
            "url": url,
            "error_type": type(exc).__name__
        }), 502
# =========================================================
# LIST MCP SERVERS
# =========================================================
@mcp_bp.route(
    "/servers",
    methods=["GET"]
)
def list_mcp_servers():
    return jsonify({
        "status":
            "success",
        "servers":
            mcp_client_manager.list_servers()
    }), 200
# =========================================================
# DELETE MCP SERVER
# =========================================================
@mcp_bp.route(
    "/servers/<server_id>",
    methods=["DELETE"]
)
def delete_mcp_server(
    server_id
):
    try:
        mcp_client_manager.remove_server(
            server_id
        )
        mcp_tool_registry.remove_server(
            server_id
        )
        return jsonify({
            "status":
                "success",
            "message":
                "MCP server removed successfully."
        }), 200
    except Exception as exc:
        return jsonify({
            "status":
                "error",
            "message":
                str(exc)
        }), 404
# =========================================================
# LIST SERVER TOOLS
# =========================================================
@mcp_bp.route(
    "/servers/<server_id>/tools",
    methods=["GET"]
)
def list_server_tools(
    server_id
):
    try:
        mcp_client_manager.get_server(
            server_id
        )
        tools = (
            mcp_tool_registry
            .get_server_tools(
                server_id
            )
        )
        return jsonify({
            "status":
                "success",
            "server_id":
                server_id,
            "tools": [
                {
                    "name":
                        tool["exposed_name"],
                    "original_name":
                        tool["name"],
                    "description":
                        tool["description"],
                    "input_schema":
                        tool["input_schema"],
                    "source":
                        "mcp",
                    "server_id":
                        tool["server_id"],
                    "server_name":
                        tool["server_name"]
                }
                for tool
                in tools
            ]
        }), 200
    except Exception as exc:
        return jsonify({
            "status":
                "error",
            "message":
                str(exc)
        }), 404
# =========================================================
# REFRESH TOOLS
# =========================================================
@mcp_bp.route(
    "/servers/<server_id>/refresh",
    methods=["POST"]
)
def refresh_server(
    server_id
):
    try:
        server = (
            mcp_client_manager
            .get_server(
                server_id
            )
        )
        tools = (
            mcp_client_manager
            .refresh_server(
                server_id
            )
        )
        mcp_tool_registry.register_tools(
            server_id=server_id,
            server_name=server["name"],
            tools=tools
        )
        registered_tools = (
            mcp_tool_registry
            .get_server_tools(
                server_id
            )
        )
        return jsonify({
            "status":
                "success",
            "message":
                "MCP tools refreshed.",
            "tools_discovered":
                len(registered_tools),
            "tools": [
                {
                    "name":
                        tool["exposed_name"],
                    "original_name":
                        tool["name"]
                }
                for tool
                in registered_tools
            ]
        }), 200
    except Exception as exc:
        return jsonify({
            "status":
                "error",
            "message":
                str(exc)
        }), 502
# =========================================================
# ALL AVAILABLE TOOLS
# =========================================================
@mcp_bp.route(
    "/tools",
    methods=["GET"]
)
def list_all_tools():
    local_tools = [
        {
            "name":
                "search_knowledge_base",
            "source":
                "local"
        },
        {
            "name":
                "search_web_tool",

            "source":
                "local"
        }
    ]
    mcp_tools = []
    for tool in (
        mcp_tool_registry
        .get_all_tools()
    ):
        mcp_tools.append({
            "name":
                tool["exposed_name"],
            "original_name":
                tool["name"],
            "source":
                "mcp",
            "server_id":
                tool["server_id"],
            "server_name":
                tool["server_name"],
            "description":
                tool["description"],
            "input_schema":
                tool["input_schema"]
        })
    return jsonify({
        "status":
            "success",
        "local_tools":
            local_tools,
        "mcp_tools":
            mcp_tools,
        "total_tools":
            len(local_tools)
            + len(mcp_tools)

    }), 200
