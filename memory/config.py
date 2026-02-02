"""
Configuration for Supermemory MCP integration
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class SupermemoryConfig:
    """Configuration for Supermemory MCP client."""

    server_url: str
    api_key: Optional[str] = None
    timeout: float = 30.0
    enabled: bool = True

    @classmethod
    def from_env(cls) -> "SupermemoryConfig":
        """
        Load configuration from environment variables.

        Environment variables:
            SUPERMEMORY_MCP_URL: MCP server URL (default: http://localhost:3000)
            SUPERMEMORY_API_KEY: API key for authentication (optional)
            SUPERMEMORY_TIMEOUT: Request timeout in seconds (default: 30)
            SUPERMEMORY_ENABLED: Enable/disable memory (default: true)

        Returns:
            SupermemoryConfig instance
        """
        return cls(
            server_url=os.getenv("SUPERMEMORY_MCP_URL", "http://localhost:3000"),
            api_key=os.getenv("SUPERMEMORY_API_KEY"),
            timeout=float(os.getenv("SUPERMEMORY_TIMEOUT", "30")),
            enabled=os.getenv("SUPERMEMORY_ENABLED", "true").lower() == "true",
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "server_url": self.server_url,
            "api_key": self.api_key,
            "timeout": self.timeout,
            "enabled": self.enabled,
        }
