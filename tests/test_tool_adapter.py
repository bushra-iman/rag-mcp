from typing import Any

from mcp_integration.tool_adapter import (
    create_args_model,
    json_schema_to_type,
)


def test_json_schema_to_type_string():
    assert json_schema_to_type({"type": "string"}) is str


def test_json_schema_to_type_integer():
    assert json_schema_to_type({"type": "integer"}) is int


def test_json_schema_to_type_number():
    assert json_schema_to_type({"type": "number"}) is float


def test_json_schema_to_type_boolean():
    assert json_schema_to_type({"type": "boolean"}) is bool


def test_json_schema_to_type_any_of_skips_null():
    schema = {"anyOf": [{"type": "null"}, {"type": "string"}]}
    assert json_schema_to_type(schema) is str


def test_json_schema_to_type_unknown_returns_any():
    assert json_schema_to_type({"type": "unknown-thing"}) is Any


def test_create_args_model_required_and_optional_fields():
    schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"},
            "limit": {"type": "integer", "description": "Max results"},
        },
        "required": ["query"],
    }
    model = create_args_model("search_tool", schema)
    assert "query" in model.model_fields
    assert model.model_fields["query"].is_required()
    assert "limit" in model.model_fields
    assert not model.model_fields["limit"].is_required()


def test_create_args_model_handles_invalid_schema():
    model = create_args_model("broken_tool", None)
    assert model is not None
