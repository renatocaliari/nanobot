"""
Supermemory MCP integration for Nanobot

This module provides a client for interacting with Supermemory MCP server,
enabling persistent memory capabilities for the Nanobot agent.
"""

import httpx
import json
from typing import Optional, Dict, Any, List
import os


class SupermemoryMCPClient:
    """
    Client for Supermemory MCP Server.

    Provides persistent memory capabilities through MCP protocol.
    """

    def __init__(
        self, server_url: Optional[str] = None, api_key: Optional[str] = None, timeout: float = 30.0
    ):
        """
        Initialize Supermemory MCP client.

        Args:
            server_url: MCP server URL (default: env SUPERMEMORY_MCP_URL)
            api_key: API key for authentication (default: env SUPERMEMORY_API_KEY)
            timeout: Request timeout in seconds
        """
        self.server_url = server_url or os.getenv("SUPERMEMORY_MCP_URL", "http://localhost:3000")
        self.api_key = api_key or os.getenv("SUPERMEMORY_API_KEY")
        self.timeout = timeout

        self.client = httpx.AsyncClient(
            base_url=self.server_url,
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
            },
            timeout=timeout,
        )

    async def store_memory(
        self, user_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a memory in Supermemory.

        Args:
            user_id: User identifier for memory isolation
            content: Memory content to store
            metadata: Optional metadata (tags, source, etc.)

        Returns:
            Response with memory ID and status
        """
        payload = {"user_id": user_id, "content": content, "metadata": metadata or {}}

        response = await self.client.post("/api/v1/memory/store", json=payload)
        response.raise_for_status()

        return response.json()

    async def search_memories(
        self, user_id: str, query: str, limit: int = 5, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memories for a user.

        Args:
            user_id: User identifier
            query: Search query (semantic search)
            limit: Maximum number of results
            filters: Optional filters (date range, tags, etc.)

        Returns:
            List of matching memories
        """
        payload = {"user_id": user_id, "query": query, "limit": limit, "filters": filters or {}}

        response = await self.client.post("/api/v1/memory/search", json=payload)
        response.raise_for_status()

        return response.json().get("memories", [])

    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory data or None if not found
        """
        response = await self.client.get(f"/api/v1/memory/{memory_id}")

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()

    async def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing memory.

        Args:
            memory_id: Memory identifier
            content: New content (optional)
            metadata: New metadata (optional)

        Returns:
            Updated memory data
        """
        payload = {}
        if content:
            payload["content"] = content
        if metadata:
            payload["metadata"] = metadata

        response = await self.client.patch(f"/api/v1/memory/{memory_id}", json=payload)
        response.raise_for_status()

        return response.json()

    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory.

        Args:
            memory_id: Memory identifier

        Returns:
            True if deleted successfully
        """
        response = await self.client.delete(f"/api/v1/memory/{memory_id}")
        return response.status_code == 204

    async def list_user_memories(
        self, user_id: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all memories for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of memories
        """
        response = await self.client.get(
            "/api/v1/memory/list", params={"user_id": user_id, "limit": limit, "offset": offset}
        )
        response.raise_for_status()

        return response.json().get("memories", [])

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Synchronous wrapper for convenience
class SupermemoryMCPClientSync:
    """
    Synchronous wrapper for SupermemoryMCPClient.

    Provides the same interface but with blocking calls.
    """

    def __init__(self, *args, **kwargs):
        self.async_client = SupermemoryMCPClient(*args, **kwargs)

    def store_memory(self, *args, **kwargs) -> Dict[str, Any]:
        """Synchronous store_memory."""
        import asyncio

        return asyncio.run(self.async_client.store_memory(*args, **kwargs))

    def search_memories(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """Synchronous search_memories."""
        import asyncio

        return asyncio.run(self.async_client.search_memories(*args, **kwargs))

    def get_memory(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """Synchronous get_memory."""
        import asyncio

        return asyncio.run(self.async_client.get_memory(*args, **kwargs))

    def update_memory(self, *args, **kwargs) -> Dict[str, Any]:
        """Synchronous update_memory."""
        import asyncio

        return asyncio.run(self.async_client.update_memory(*args, **kwargs))

    def delete_memory(self, *args, **kwargs) -> bool:
        """Synchronous delete_memory."""
        import asyncio

        return asyncio.run(self.async_client.delete_memory(*args, **kwargs))

    def list_user_memories(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """Synchronous list_user_memories."""
        import asyncio

        return asyncio.run(self.async_client.list_user_memories(*args, **kwargs))

    def close(self):
        """Close the client."""
        import asyncio

        asyncio.run(self.async_client.close())
