"""
Memory utilities for nanobot Mem0 integration.

Provides utilities to import, export, and manage Mem0 memories.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from nanobot.memory.mem0_client import Mem0Client


class Mem0Importer:
    """
    Import memories into Mem0 server.

    Provides async methods to import memories in Mem0 format.
    """

    def __init__(
        self,
        server_url: str,
        api_key: str | None = None,
        timeout: float = 30.0,
    ):
        """
        Initialize Mem0 importer.

        Args:
            server_url: Mem0 server URL
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.client = Mem0Client(server_url=server_url, api_key=api_key, timeout=timeout)

    async def import_memories(
        self,
        memories: List[Dict[str, Any]],
        user_id: str,
        progress_callback=None,
        dry_run: bool = False,
        batch_size: int = 10,
        parallel: bool = True,
    ) -> Dict[str, Any]:
        """
        Import memories into Mem0 with batch and parallel processing.

        Args:
            memories: List of memory dictionaries to import
            user_id: User identifier for memory isolation
            progress_callback: Optional callback for progress updates
            dry_run: If True, don't actually import (just validate)
            batch_size: Number of memories to process per batch (default: 10)
            parallel: If True, process batches in parallel (default: True)

        Returns:
            Dictionary with import results (success_count, errors, etc.)
        """
        results = {
            "total": len(memories),
            "success": 0,
            "errors": [],
            "skipped": 0,
        }

        if dry_run:
            for idx, memory in enumerate(memories):
                content = memory.get("content", "")

                if not content or not content.strip():
                    results["skipped"] += 1
                else:
                    results["success"] += 1

                if progress_callback:
                    progress_callback(idx + 1, len(memories))

            return results

        batch_results = await self.client.store_memories_batch(
            memories=memories,
            user_id=user_id,
            batch_size=batch_size,
            parallel=parallel,
            progress_callback=progress_callback,
        )

        results["success"] = batch_results["success"]
        results["errors"] = batch_results["errors"]
        results["skipped"] = batch_results.get("skipped", 0)

        return results

    async def health_check(self) -> bool:
        """
        Check if Mem0 server is accessible.

        Returns:
            True if server is healthy, False otherwise
        """
        return await self.client.health_check()

    async def close(self):
        """Close the Mem0 client."""
        await self.client.close()


def save_export_file(memories: List[Dict[str, Any]], output_path: Path) -> None:
    """
    Save exported memories to a JSON file.

    Args:
        memories: List of memory dictionaries
        output_path: Path to save the export file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "total_memories": len(memories),
        "memories": memories,
    }

    output_path.write_text(json.dumps(export_data, indent=2))


def load_export_file(input_path: Path) -> List[Dict[str, Any]]:
    """
    Load memories from a JSON export file.

    Args:
        input_path: Path to the export file

    Returns:
        List of memory dictionaries

    Raises:
        FileNotFoundError: If export file doesn't exist
        json.JSONDecodeError: If export file is invalid JSON
    """
    data = json.loads(input_path.read_text())
    return data.get("memories", [])
