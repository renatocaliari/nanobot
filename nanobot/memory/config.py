"""
Configuration for Mem0 memory integration
Drop-in replacement for Supermemory - supports both env var names
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Mem0Config:
    """Configuration for Mem0 client."""

    server_url: str
    api_key: Optional[str] = None
    timeout: float = 30.0
    enabled: bool = True
    collection_name: str = "nanobot"

    @classmethod
    def from_env(cls) -> "Mem0Config":
        """
        Load configuration from environment variables.

        Environment variables:
            MEM0_URL: Mem0 server URL (default: http://localhost:8000)
            MEM0_API_KEY: API key for authentication (optional)
            MEM0_TIMEOUT: Request timeout in seconds (default: 30)
            MEM0_ENABLED: Enable/disable memory (default: true)
            MEM0_COLLECTION: Collection name (default: nanobot)

            # Backward compatibility - also support Supermemory env vars
            SUPERMEMORY_MCP_URL: Maps to MEM0_URL
            SUPERMEMORY_API_KEY: Maps to MEM0_API_KEY
            SUPERMEMORY_TIMEOUT: Maps to MEM0_TIMEOUT
            SUPERMEMORY_ENABLED: Maps to MEM0_ENABLED

        Returns:
            Mem0Config instance
        """
        # Support both new (MEM0_*) and old (SUPERMEMORY_*) env var names
        return cls(
            server_url=os.getenv("MEM0_URL")
            or os.getenv("SUPERMEMORY_MCP_URL", "http://localhost:8000"),
            api_key=os.getenv("MEM0_API_KEY") or os.getenv("SUPERMEMORY_API_KEY"),
            timeout=float(os.getenv("MEM0_TIMEOUT") or os.getenv("SUPERMEMORY_TIMEOUT", "30")),
            enabled=(
                os.getenv("MEM0_ENABLED", "true").lower() == "true"
                or os.getenv("SUPERMEMORY_ENABLED", "true").lower() == "true"
            ),
            collection_name=os.getenv("MEM0_COLLECTION", "nanobot"),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "server_url": self.server_url,
            "api_key": self.api_key,
            "timeout": self.timeout,
            "enabled": self.enabled,
            "collection_name": self.collection_name,
        }


# Backward compatibility - keep old class name
SupermemoryConfig = Mem0Config
