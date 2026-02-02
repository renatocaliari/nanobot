"""Base class for agent tools."""

from abc import ABC, abstractmethod
from typing import Any

import jsonschema


class Tool(ABC):
    """
    Abstract base class for agent tools.

    Tools are capabilities that the agent can use to interact with
    the environment, such as reading files, executing commands, etc.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name used in function calls."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """JSON Schema for tool parameters."""
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> str:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters.

        Returns:
            String result of the tool execution.
        """
        pass

    def validate_params(self, params: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Validate tool parameters against JSON schema.

        Args:
            params: Parameters to validate.

        Returns:
            (is_valid, error_message)
            - is_valid: True if validation passes
            - error_message: Error description if validation fails, None otherwise
        """
        try:
            jsonschema.validate(
                instance=params,
                schema=self.parameters,
                # Allow extra fields (unknown params) for flexibility
                # Only validate fields defined in the schema
            )
            return True, None
        except jsonschema.ValidationError as e:
            # Create user-friendly error message
            error_path = " -> ".join(str(p) for p in e.path) if e.path else "params"
            return False, f"Invalid {error_path}: {e.message}"
        except Exception as e:
            return False, f"Validation error: {e}"

    async def execute_safe(self, **kwargs: Any) -> str:
        """
        Execute tool with parameter validation.

        Validates parameters before execution to provide clear error messages
        early in the workflow, avoiding late/inconsistent failures.

        Args:
            **kwargs: Tool-specific parameters.

        Returns:
            String result of the tool execution, or error message.
        """
        # Validate parameters
        is_valid, error_msg = self.validate_params(kwargs)
        if not is_valid:
            return f"Error: {error_msg}"

        # Execute tool
        return await self.execute(**kwargs)

    def to_schema(self) -> dict[str, Any]:
        """Convert tool to OpenAI function schema format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
