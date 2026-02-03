"""Memory status checker tool for nanobot."""

import asyncio
from typing import Any

from nanobot.memory.mem0_client import Mem0Client


async def check_mem0_status(url: str = "http://localhost:8000") -> str:
    """
    Check Mem0 memory server status.

    Args:
        url: Mem0 server URL (default: http://localhost:8000)

    Returns:
        Formatted status report of Mem0 server.
    """
    try:
        client = Mem0Client(server_url=url)
        is_healthy = await client.health_check()
        await client.close()

        if is_healthy:
            return f"✅ Mem0 is healthy and accessible at {url}"
        else:
            return f"❌ Mem0 is not responding at {url}"

    except Exception as e:
        return f"❌ Failed to connect to Mem0 at {url}: {e}"


def register_memory_status_tools(tool_registry: dict[str, Any]) -> None:
    """Register memory status checker tools."""
    tool_registry["check_mem0_status"] = {
        "function": check_mem0_status,
        "description": "Check Mem0 memory server status",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Mem0 server URL (default: http://localhost:8000)",
                }
            },
            "required": [],
        },
    }
