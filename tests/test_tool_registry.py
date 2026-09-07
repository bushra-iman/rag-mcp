from mcp_integration.tool_registry import MCPToolRegistry


class FakeTool:
    def __init__(self, name, description="", input_schema=None):
        self.name = name
        self.description = description
        self.input_schema = input_schema or {
            "type": "object",
            "properties": {},
        }


def test_register_tools_creates_prefixed_exposed_names():
    registry = MCPToolRegistry()
    registry.register_server(
        "srv-1",
        "Postman Server",
        "http://localhost:8000/mcp",
    )
    registry.register_tools(
        "srv-1",
        "Postman Server",
        [FakeTool("get_air_quality")],
    )
    tools = registry.get_all_tools()
    assert len(tools) == 1
    assert tools[0]["exposed_name"] == "mcp_postman_server_get_air_quality"


def test_collision_handling_between_servers():
    registry = MCPToolRegistry()
    registry.register_server("srv-1", "Server A", "http://localhost:8000/mcp")
    registry.register_server("srv-2", "Server A", "http://localhost:8001/mcp")
    registry.register_tools("srv-1", "Server A", [FakeTool("common_tool")])
    registry.register_tools("srv-2", "Server A", [FakeTool("common_tool")])
    tools = registry.get_all_tools()
    assert len(tools) == 2
    names = {tool["exposed_name"] for tool in tools}
    assert len(names) == 2


def test_remove_server_removes_its_tools():
    registry = MCPToolRegistry()
    registry.register_server("srv-1", "Server A", "http://localhost:8000/mcp")
    registry.register_tools(
        "srv-1",
        "Server A",
        [FakeTool("tool_a"), FakeTool("tool_b")],
    )
    registry.remove_server("srv-1")
    assert registry.count() == 0


def test_get_server_tools_filters_by_server():
    registry = MCPToolRegistry()
    registry.register_server("srv-1", "Server A", "http://localhost:8000/mcp")
    registry.register_server("srv-2", "Server B", "http://localhost:8001/mcp")
    registry.register_tools("srv-1", "Server A", [FakeTool("tool_a")])
    registry.register_tools("srv-2", "Server B", [FakeTool("tool_b")])
    assert len(registry.get_server_tools("srv-1")) == 1
    assert len(registry.get_server_tools("srv-2")) == 1
