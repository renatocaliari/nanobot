"""Tests for tool parameter validation."""

import pytest

from nanobot.agent.tools.base import Tool


class DummyTool(Tool):
    """Dummy tool for testing."""

    @property
    def name(self) -> str:
        return "dummy_tool"

    @property
    def description(self) -> str:
        return "A dummy tool for testing"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Message to process"},
                "count": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Number of times to repeat",
                },
                "nested": {
                    "type": "object",
                    "properties": {"key": {"type": "string"}},
                    "required": ["key"],
                },
            },
            "required": ["message"],
            "additionalProperties": True,  # Allow extra fields
        }

    async def execute(self, **kwargs) -> str:
        return f"Executed with: {kwargs}"


class TestToolValidation:
    """Test suite for tool parameter validation."""

    @pytest.mark.asyncio
    async def test_valid_params(self):
        """Tool should accept valid parameters."""
        tool = DummyTool()

        is_valid, error = tool.validate_params({"message": "hello"})
        assert is_valid
        assert error is None

        result = await tool.execute_safe(message="hello")
        assert "Executed with:" in result

    @pytest.mark.asyncio
    async def test_missing_required_param(self):
        """Tool should reject missing required parameters."""
        tool = DummyTool()

        is_valid, error = tool.validate_params({})
        assert not is_valid
        assert "message" in error.lower()
        assert "required" in error.lower()

    @pytest.mark.asyncio
    async def test_wrong_type(self):
        """Tool should reject wrong parameter type."""
        tool = DummyTool()

        is_valid, error = tool.validate_params({"message": 123})
        assert not is_valid
        assert "message" in error.lower()
        assert "string" in error.lower()

    @pytest.mark.asyncio
    async def test_out_of_range(self):
        """Tool should reject out-of-range integer."""
        tool = DummyTool()

        is_valid, error = tool.validate_params({"message": "test", "count": 15})
        assert not is_valid
        assert "count" in error.lower()

    @pytest.mark.asyncio
    async def test_invalid_nested_object(self):
        """Tool should validate nested objects."""
        tool = DummyTool()

        is_valid, error = tool.validate_params(
            {
                "message": "test",
                "nested": {},  # missing required 'key'
            }
        )
        assert not is_valid
        assert "nested" in error.lower()
        assert "key" in error.lower()

    @pytest.mark.asyncio
    async def test_extra_fields_allowed(self):
        """Tool should allow extra fields (additionalProperties=True)."""
        tool = DummyTool()

        is_valid, error = tool.validate_params({"message": "test", "extra_field": "some value"})
        assert is_valid
        assert error is None

    @pytest.mark.asyncio
    async def test_execute_safe_returns_error_on_invalid(self):
        """execute_safe should return clear error for invalid params."""
        tool = DummyTool()

        result = await tool.execute_safe(message=123)
        assert "Error:" in result
        assert "message" in result

    @pytest.mark.asyncio
    async def test_execute_safe_calls_execute_on_valid(self):
        """execute_safe should call execute for valid params."""
        tool = DummyTool()

        result = await tool.execute_safe(message="hello", count=3)
        assert "Executed with:" in result
        assert "message" in result
        assert "count" in result
