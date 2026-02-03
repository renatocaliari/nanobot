"""Mem0 client for nanobot memory module.

Compatible with SupermemoryMCPClient interface.
Drop-in replacement for Supermemory.
"""

import asyncio
import httpx
import json
from typing import Optional, Dict, Any, List
import os


class Mem0Client:
    """
    Client for Mem0 memory server.

    Drop-in replacement for SupermemoryMCPClient.
    Uses Mem0's HTTP API for persistent memory with semantic search.
    """

    def __init__(
        self,
        server_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        collection_name: str = "nanobot",
    ):
        """
        Initialize Mem0 client.

        Args:
            server_url: Mem0 server URL (default: env MEM0_URL or http://localhost:8000)
            api_key: API key for authentication (default: env MEM0_API_KEY)
            timeout: Request timeout in seconds
            collection_name: Name of the collection to use (default: nanobot)
        """
        self.server_url = server_url or os.getenv("MEM0_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("MEM0_API_KEY")
        self.timeout = timeout
        self.collection_name = collection_name

        self.client = httpx.AsyncClient(
            base_url=self.server_url,
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Token {self.api_key}"} if self.api_key else {}),
            },
            timeout=timeout,
        )

    async def store_memory(
        self, user_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a memory in Mem0.

        Args:
            user_id: User identifier for memory isolation
            content: Memory content to store
            metadata: Optional metadata (tags, source, etc.)

        Returns:
            Response with memory ID and status
        """
        payload = {
            "messages": [{"role": "user", "content": content}],
            "user_id": user_id,
            "metadata": metadata or {},
        }

        response = await self.client.post(f"/v1/memories", json=payload)
        response.raise_for_status()

        result = response.json()

        # Mem0 returns {'results': [{...}]}
        if "results" in result and len(result["results"]) > 0:
            return {"id": result["results"][0].get("id"), "status": "stored", "memory": content}

        return {"status": "stored", "memory": content}

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
        payload = {
            "query": query,
            "user_id": user_id,
            "limit": limit,
        }

        response = await self.client.post("/v1/memories/search", json=payload)
        response.raise_for_status()

        result = response.json()

        # Mem0 returns {'results': [{memory, score, metadata}]}
        memories = []
        if "results" in result:
            for item in result["results"]:
                memory_text = item.get("memory", "")
                # Extract actual text content if it's in message format
                if isinstance(memory_text, list) and len(memory_text) > 0:
                    memory_text = memory_text[0].get("content", str(memory_text))

                memories.append(
                    {
                        "content": memory_text,
                        "score": item.get("score", 0.0),
                        "metadata": item.get("metadata", {}),
                        "id": item.get("id", ""),
                    }
                )

        return memories

    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory data or None if not found
        """
        response = await self.client.get(f"/v1/memories/{memory_id}")

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
            payload["memory"] = content
        if metadata:
            payload["metadata"] = metadata

        if not payload:
            raise ValueError("Must provide content or metadata")

        response = await self.client.patch(f"/v1/memories/{memory_id}", json=payload)
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
        response = await self.client.delete(f"/v1/memories/{memory_id}")
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
        # Mem0 search with empty query returns all
        return await self.search_memories(user_id, query="", limit=limit)

    async def store_memories_batch(
        self,
        memories: List[Dict[str, Any]],
        user_id: str,
        batch_size: int = 10,
        parallel: bool = True,
        progress_callback=None,
    ) -> Dict[str, Any]:
        """
        Store multiple memories with optional parallel processing.

        Args:
            memories: List of memory dicts with 'content' and optional 'metadata'
            user_id: User identifier for memory isolation
            batch_size: Number of memories to process per batch
            parallel: If True, process batches in parallel using asyncio.gather
            progress_callback: Optional callback(current, total)

        Returns:
            Dict with success_count, errors, skipped_count
        """
        results = {"success": 0, "errors": [], "skipped": 0}
        total = len(memories)

        async def import_batch(batch: List[Dict[str, Any]], start_idx: int):
            batch_results = {"success": 0, "errors": []}
            tasks = []

            for idx, memory in enumerate(batch):
                content = memory.get("content", "")
                metadata = memory.get("metadata", {})

                if not content or not content.strip():
                    batch_results["skipped"] = batch_results.get("skipped", 0) + 1
                    continue

                tasks.append(self.store_memory(user_id=user_id, content=content, metadata=metadata))

            if tasks:
                responses = await asyncio.gather(*tasks, return_exceptions=True)

                for i, response in enumerate(responses):
                    global_idx = start_idx + i
                    if isinstance(response, Exception):
                        batch_results["errors"].append(
                            {"index": global_idx, "error": str(response)}
                        )
                    else:
                        batch_results["success"] += 1

                    if progress_callback:
                        progress_callback(global_idx + 1, total)

            return batch_results

        if parallel and batch_size > 1:
            batches = [memories[i : i + batch_size] for i in range(0, len(memories), batch_size)]
            batch_results = await asyncio.gather(
                *[import_batch(batch, i * batch_size) for i, batch in enumerate(batches)],
                return_exceptions=True,
            )

            for result in batch_results:
                if isinstance(result, Exception):
                    results["errors"].append({"batch_error": str(result)})
                else:
                    results["success"] += result["success"]
                    results["errors"].extend(result["errors"])
                    results["skipped"] += result.get("skipped", 0)
        else:
            batch_results = await import_batch(memories, 0)
            results["success"] = batch_results["success"]
            results["errors"] = batch_results["errors"]
            results["skipped"] = batch_results.get("skipped", 0)

        return results

    async def health_check(self) -> bool:
        """
        Check if the Mem0 server is accessible.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            response = await self.client.get("/v1/health")
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


class Mem0ClientSync:
    """
    Synchronous wrapper for Mem0Client.

    Provides the same interface as Mem0Client but with blocking calls.
    Compatible with SupermemoryMCPClientSync interface.
    """

    def __init__(self, *args, **kwargs):
        self.async_client = Mem0Client(*args, **kwargs)

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

    def health_check(self) -> bool:
        """Synchronous health_check."""
        import asyncio

        return asyncio.run(self.async_client.health_check())

    def close(self):
        """Close the client."""
        import asyncio

        asyncio.run(self.async_client.close())


# Backward compatibility aliases
SupermemoryMCPClient = Mem0Client
SupermemoryMCPClientSync = Mem0ClientSync
