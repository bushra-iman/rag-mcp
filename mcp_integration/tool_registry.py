import re
class MCPToolRegistry:
    def __init__(self):
        # Exposed tool name -> tool definition
        self.tools = {}
        # Server ID -> server information
        self.servers = {}
    # =========================================================
    # REGISTER SERVER
    # =========================================================
    def register_server(
        self,
        server_id: str,
        name: str,
        url: str
    ):
        self.servers[server_id] = {
            "id": server_id,
            "name": name,
            "url": url
        }
    # =========================================================
    # REMOVE SERVER
    # =========================================================
    def remove_server(
        self,
        server_id: str
    ):
        self.servers.pop(
            server_id,
            None
        )
        self.tools = {
            exposed_name: definition
            for exposed_name, definition
            in self.tools.items()
            if definition.get("server_id")
            != server_id
        }
    # =========================================================
    # SAFE SERVER NAME
    # =========================================================
    def _safe_name(
        self,
        name: str
    ):
        if not name:
            return "server"
        name = str(name).lower()
        name = re.sub(
            r"[^a-zA-Z0-9_]+",
            "_",
            name
        )
        name = name.strip("_")
        return name or "server"
    # =========================================================
    # REGISTER DISCOVERED TOOLS
    # =========================================================
    def register_tools(
        self,
        server_id: str,
        server_name: str,
        tools
    ):
        # -----------------------------------------------------
        # Remove old tools belonging to this server
        # -----------------------------------------------------
        self.tools = {
            exposed_name: definition
            for exposed_name, definition
            in self.tools.items()
            if definition.get("server_id")
            != server_id
        }
        safe_server_name = self._safe_name(
            server_name
        )
        # -----------------------------------------------------
        # Make sure tools is iterable
        # -----------------------------------------------------
        if tools is None:
            tools = []
        # -----------------------------------------------------
        # Register every discovered MCP tool
        # -----------------------------------------------------
        for tool in tools:
            # -------------------------------------------------
            # Original MCP tool name
            # -------------------------------------------------
            original_name = getattr(
                tool,
                "name",
                None
            )
            if not original_name:
                continue
            # -------------------------------------------------
            # Exposed name
            #
            # Example:
            # openmeteo_get_air_quality
            #
            # becomes:
            # mcp_postman_server_d_openmeteo_get_air_quality
            # -------------------------------------------------
            exposed_name = (
                f"mcp_{safe_server_name}_"
                f"{original_name}"
            )
            # -------------------------------------------------
            # Collision handling
            # -------------------------------------------------
            if exposed_name in self.tools:
                exposed_name = (
                    f"mcp_{safe_server_name}_"
                    f"{server_id[:8]}_"
                    f"{original_name}"
                )
            # -------------------------------------------------
            # INPUT SCHEMA
            # -------------------------------------------------
            input_schema = getattr(
                tool,
                "input_schema",
                None
            )
            # Some MCP SDK objects may expose
            # inputSchema instead.
            if not isinstance(
                input_schema,
                dict
            ):
                input_schema = getattr(
                    tool,
                    "inputSchema",
                    None
                )
            # Final safe fallback
            if not isinstance(
                input_schema,
                dict
            ):
                input_schema = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            # -------------------------------------------------
            # DESCRIPTION
            # -------------------------------------------------
            description = getattr(
                tool,
                "description",
                None
            )
            if not description:
                description = (
                    f"MCP tool: {original_name}"
                )
            # -------------------------------------------------
            # STORE TOOL DEFINITION
            # -------------------------------------------------
            self.tools[
                exposed_name
            ] = {
                "name":
                    original_name,
                "exposed_name":
                    exposed_name,
                "description":
                    description,
                "input_schema":
                    input_schema,
                "server_id":
                    server_id,
                "server_name":
                    server_name
            }
    # =========================================================
    # ALL TOOLS
    # =========================================================
    def get_all_tools(self):
        return list(
            self.tools.values()
        )
    # =========================================================
    # GET TOOL
    # =========================================================
    def get_tool(
        self,
        exposed_name: str
    ):
        return self.tools.get(
            exposed_name
        )
    # =========================================================
    # SERVER TOOLS
    # =========================================================
    def get_server_tools(
        self,
        server_id: str
    ):
        return [
            tool
            for tool
            in self.tools.values()
            if tool.get("server_id")
            == server_id
        ]
    # =========================================================
    # COUNT
    # =========================================================
    def count(self):
        return len(
            self.tools
        )
# =========================================================
# GLOBAL REGISTRY
# =========================================================
mcp_tool_registry = MCPToolRegistry()
