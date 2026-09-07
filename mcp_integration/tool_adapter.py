from typing import Any
from pydantic import (
    Field,
    create_model
)
from langchain_core.tools import (
    StructuredTool
)
# =========================================================
# JSON SCHEMA -> PYTHON TYPE
# =========================================================
def json_schema_to_type(schema):
    # Schema None / invalid ho
    if not isinstance(schema, dict):
        return Any
    # -----------------------------------------------------
    # Direct type
    # -----------------------------------------------------
    schema_type = schema.get("type")
    if schema_type == "string":
        return str
    if schema_type == "integer":
        return int
    if schema_type == "number":
        return float
    if schema_type == "boolean":
        return bool
    if schema_type == "array":
        return list[Any]
    if schema_type == "object":
        return dict[str, Any]
    # -----------------------------------------------------
    # anyOf
    # -----------------------------------------------------
    any_of = schema.get("anyOf")
    if isinstance(any_of, list):
        for option in any_of:
            if not isinstance(option, dict):
                continue
            option_type = option.get("type")
            if option_type == "null":
                continue
            result = json_schema_to_type(option)
            if result is not Any:
                return result
    # -----------------------------------------------------
    # oneOf
    # -----------------------------------------------------
    one_of = schema.get("oneOf")
    if isinstance(one_of, list):
        for option in one_of:
            if not isinstance(option, dict):
                continue
            option_type = option.get("type")
            if option_type == "null":
                continue
            result = json_schema_to_type(option)
            if result is not Any:
                return result
    # -----------------------------------------------------
    # allOf
    # -----------------------------------------------------
    all_of = schema.get("allOf")
    if isinstance(all_of, list):
        for option in all_of:
            if not isinstance(option, dict):
                continue
            result = json_schema_to_type(option)
            if result is not Any:
                return result
    # -----------------------------------------------------
    # Unknown schema
    # -----------------------------------------------------
    return Any
# =========================================================
# CREATE PYDANTIC ARGUMENT MODEL
# =========================================================
def create_args_model(
    tool_name: str,
    input_schema
):
    # -----------------------------------------------------
    # SAFETY: schema must be dictionary
    # -----------------------------------------------------
    if not isinstance(input_schema, dict):
        input_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
    # -----------------------------------------------------
    # PROPERTIES
    # -----------------------------------------------------
    properties = input_schema.get(
        "properties"
    )
    if not isinstance(properties, dict):
        properties = {}
    # -----------------------------------------------------
    # REQUIRED FIELDS
    # -----------------------------------------------------
    required_value = input_schema.get(
        "required",
        []
    )
    if not isinstance(
        required_value,
        list
    ):
        required_value = []
    required = set(
        required_value
    )
    # -----------------------------------------------------
    # CREATE PYDANTIC FIELDS
    # -----------------------------------------------------
    fields = {}
    for field_name, field_schema in properties.items():
        # Field name safety
        if not isinstance(
            field_name,
            str
        ):
            continue
        # Schema safety
        if not isinstance(
            field_schema,
            dict
        ):
            field_schema = {}
        python_type = json_schema_to_type(
            field_schema
        )
        description = field_schema.get(
            "description",
            ""
        )
        if not isinstance(
            description,
            str
        ):
            description = ""
        # -------------------------------------------------
        # REQUIRED
        # -------------------------------------------------
        if field_name in required:
            fields[field_name] = (
                python_type,
                Field(
                    ...,
                    description=description
                )
            )
        # -------------------------------------------------
        # OPTIONAL
        # -------------------------------------------------
        else:
            fields[field_name] = (
                python_type | None,
                Field(
                    default=None,
                    description=description
                )
            )
    # -----------------------------------------------------
    # SAFE PYDANTIC MODEL NAME
    # -----------------------------------------------------
    safe_model_name = "".join(
        character
        if character.isalnum()
        else "_"
        for character in tool_name
    )
    if not safe_model_name:
        safe_model_name = "MCPTool"
    model_name = (
        f"{safe_model_name}Arguments"
    )
    # -----------------------------------------------------
    # CREATE MODEL
    # -----------------------------------------------------
    return create_model(
        model_name,
        **fields
    )
# =========================================================
# CREATE MCP LANGCHAIN TOOL
# =========================================================
def create_mcp_langchain_tool(
    client_manager,
    tool_definition
):
    # -----------------------------------------------------
    # VALIDATE TOOL DEFINITION
    # -----------------------------------------------------
    if not isinstance(
        tool_definition,
        dict
    ):
        raise ValueError(
            "Invalid MCP tool definition."
        )
    # -----------------------------------------------------
    # TOOL INFORMATION
    # -----------------------------------------------------
    exposed_name = tool_definition.get(
        "exposed_name"
    )
    original_name = tool_definition.get(
        "name"
    )
    server_id = tool_definition.get(
        "server_id"
    )
    description = tool_definition.get(
        "description"
    )
    # -----------------------------------------------------
    # VALIDATE NAMES
    # -----------------------------------------------------
    if not exposed_name:
        raise ValueError(
            "MCP tool is missing exposed_name."
        )
    if not original_name:
        raise ValueError(
            f"MCP tool '{exposed_name}' "
            "is missing original name."
        )

    if not server_id:

        raise ValueError(
            f"MCP tool '{exposed_name}' "
            "is missing server_id."
        )

    # -----------------------------------------------------
    # DESCRIPTION
    # -----------------------------------------------------

    if not isinstance(
        description,
        str
    ) or not description.strip():

        description = (
            f"MCP tool: {original_name}"
        )

    # -----------------------------------------------------
    # INPUT SCHEMA
    # -----------------------------------------------------

    input_schema = tool_definition.get(
        "input_schema"
    )

    if not isinstance(
        input_schema,
        dict
    ):

        input_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }

    # -----------------------------------------------------
    # PYDANTIC ARGUMENT MODEL
    # -----------------------------------------------------

    args_model = create_args_model(
        exposed_name,
        input_schema
    )

    # =====================================================
    # ACTUAL MCP EXECUTION
    # =====================================================

    def execute_mcp_tool(
        **kwargs
    ):

        # -------------------------------------------------
        # Remove None arguments
        # -------------------------------------------------

        clean_arguments = {}

        for key, value in kwargs.items():

            if value is not None:

                clean_arguments[key] = value

        # -------------------------------------------------
        # CALL MCP SERVER
        # -------------------------------------------------

        result = client_manager.call_tool(
            server_id=server_id,
            tool_name=original_name,
            arguments=clean_arguments
        )

        # -------------------------------------------------
        # NEVER RETURN NONE
        # -------------------------------------------------

        if result is None:

            return (
                f"MCP tool '{original_name}' "
                "returned no result."
            )

        # -------------------------------------------------
        # RETURN MCP RESULT
        # -------------------------------------------------

        if isinstance(
            result,
            str
        ):

            return result

        try:

            return str(result)

        except Exception:

            return (
                f"MCP tool '{original_name}' "
                "returned an unreadable result."
            )

    # =====================================================
    # CREATE LANGCHAIN TOOL
    # =====================================================

    return StructuredTool.from_function(
        func=execute_mcp_tool,
        name=exposed_name,
        description=description,
        args_schema=args_model
    )
