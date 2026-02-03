"""
Tests for Mem0 memory utilities.

Tests cover:
- Mem0 import functionality
- Export/import file utilities
"""

import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from nanobot.memory.migration import Mem0Importer, save_export_file, load_export_file


@pytest.fixture
def sample_memories():
    """Sample Mem0-format memories for testing."""
    return [
        {
            "content": "User loves Python programming",
            "metadata": {"category": "preferences"},
        },
        {
            "content": "Prefers dark mode in IDEs",
            "metadata": {"category": "settings"},
        },
    ]


class TestMem0Importer:
    """Tests for Mem0 import functionality."""

    @pytest.mark.asyncio
    async def test_import_memories_success(self, sample_memories):
        """Test successful import to Mem0."""
        importer = Mem0Importer(server_url="http://localhost:8000", api_key="test-key")

        with patch.object(
            importer.client, "store_memory", return_value={"id": "new_id", "status": "stored"}
        ):
            result = await importer.import_memories(
                memories=sample_memories, user_id="user123", dry_run=False
            )

            assert result["total"] == 2
            assert result["success"] == 2
            assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_import_dry_run(self, sample_memories):
        """Test import with dry_run=True doesn't store memories."""
        importer = Mem0Importer(server_url="http://localhost:8000")

        with patch.object(importer.client, "store_memory") as mock_store:
            result = await importer.import_memories(
                memories=sample_memories, user_id="user123", dry_run=True
            )

            assert result["success"] == 2
            mock_store.assert_not_called()

    @pytest.mark.asyncio
    async def test_import_skips_empty_content(self):
        """Test import skips memories with empty content."""
        memories = [
            {"content": "Valid memory", "metadata": {}},
            {"content": "", "metadata": {}},
            {"content": "   ", "metadata": {}},
        ]

        importer = Mem0Importer(server_url="http://localhost:8000")

        with patch.object(importer.client, "store_memory", return_value={"status": "stored"}):
            result = await importer.import_memories(
                memories=memories, user_id="user123", dry_run=False
            )

            assert result["success"] == 1
            assert result["skipped"] == 2

    @pytest.mark.asyncio
    async def test_import_handles_errors(self):
        """Test import handles errors gracefully."""
        memories = [
            {"content": "Memory 1", "metadata": {}},
            {"content": "Memory 2", "metadata": {}},
        ]

        importer = Mem0Importer(server_url="http://localhost:8000")

        async def side_effect(*args, **kwargs):
            if kwargs.get("content") == "Memory 2":
                raise Exception("Import failed")
            return {"status": "stored"}

        with patch.object(importer.client, "store_memory", side_effect=side_effect):
            result = await importer.import_memories(
                memories=memories, user_id="user123", dry_run=False
            )

            assert result["success"] == 1
            assert len(result["errors"]) == 1

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test health check returns True for healthy server."""
        importer = Mem0Importer(server_url="http://localhost:8000")

        with patch.object(importer.client, "health_check", return_value=True):
            result = await importer.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_import_batch_default_size(self):
        """Test batch import with default batch size."""
        memories = [{"content": f"Memory {i}", "metadata": {"index": i}} for i in range(25)]

        importer = Mem0Importer(server_url="http://localhost:8000")

        with patch.object(
            importer.client, "store_memory", return_value={"status": "stored"}
        ) as mock_store:
            result = await importer.import_memories(
                memories=memories,
                user_id="user123",
                dry_run=False,
                batch_size=10,
                parallel=True,
            )

            assert result["success"] == 25
            assert mock_store.call_count == 25

    @pytest.mark.asyncio
    async def test_import_batch_custom_size(self):
        """Test batch import with custom batch size."""
        memories = [{"content": f"Memory {i}", "metadata": {}} for i in range(20)]

        importer = Mem0Importer(server_url="http://localhost:8000")

        with patch.object(importer.client, "store_memory", return_value={"status": "stored"}):
            result = await importer.import_memories(
                memories=memories,
                user_id="user123",
                dry_run=False,
                batch_size=5,
                parallel=True,
            )

            assert result["success"] == 20
            assert result["total"] == 20

    @pytest.mark.asyncio
    async def test_import_batch_single_item(self):
        """Test batch import with batch_size=1."""
        memories = [
            {"content": "Memory 1", "metadata": {}},
            {"content": "Memory 2", "metadata": {}},
        ]

        importer = Mem0Importer(server_url="http://localhost:8000")

        with patch.object(importer.client, "store_memory", return_value={"status": "stored"}):
            result = await importer.import_memories(
                memories=memories,
                user_id="user123",
                dry_run=False,
                batch_size=1,
                parallel=True,
            )

            assert result["success"] == 2

    @pytest.mark.asyncio
    async def test_import_batch_parallel_disabled(self):
        """Test batch import with parallel=False."""
        memories = [{"content": f"Memory {i}", "metadata": {}} for i in range(10)]

        importer = Mem0Importer(server_url="http://localhost:8000")

        with patch.object(importer.client, "store_memory", return_value={"status": "stored"}):
            result = await importer.import_memories(
                memories=memories,
                user_id="user123",
                dry_run=False,
                batch_size=5,
                parallel=False,
            )

            assert result["success"] == 10

    @pytest.mark.asyncio
    async def test_import_batch_with_empty_content(self):
        """Test batch import filters empty content."""
        memories = [
            {"content": "Valid memory 1", "metadata": {}},
            {"content": "", "metadata": {}},
            {"content": "Valid memory 2", "metadata": {}},
            {"content": "   ", "metadata": {}},
            {"content": "Valid memory 3", "metadata": {}},
        ]

        importer = Mem0Importer(server_url="http://localhost:8000")

        with patch.object(
            importer.client, "store_memory", return_value={"status": "stored"}
        ) as mock_store:
            result = await importer.import_memories(
                memories=memories,
                user_id="user123",
                dry_run=False,
                batch_size=2,
                parallel=True,
            )

            assert result["success"] == 3
            assert result["skipped"] == 2
            assert mock_store.call_count == 3

    @pytest.mark.asyncio
    async def test_import_batch_with_errors(self):
        """Test batch import handles partial failures."""
        memories = [
            {"content": "Valid 1", "metadata": {}},
            {"content": "Error", "metadata": {}},
            {"content": "Valid 2", "metadata": {}},
            {"content": "Error 2", "metadata": {}},
        ]

        importer = Mem0Importer(server_url="http://localhost:8000")

        async def side_effect(*args, **kwargs):
            content = kwargs.get("content", "")
            if "Error" in content:
                raise Exception(f"Failed to import: {content}")
            return {"status": "stored"}

        with patch.object(importer.client, "store_memory", side_effect=side_effect):
            result = await importer.import_memories(
                memories=memories,
                user_id="user123",
                dry_run=False,
                batch_size=2,
                parallel=True,
            )

            assert result["success"] == 2
            assert len(result["errors"]) == 2
            assert result["total"] == 4

    @pytest.mark.asyncio
    async def test_import_batch_progress_callback(self):
        """Test batch import invokes progress callback."""
        memories = [{"content": f"Memory {i}", "metadata": {}} for i in range(15)]

        importer = Mem0Importer(server_url="http://localhost:8000")

        progress_calls = []

        def track_progress(current: int, total: int):
            progress_calls.append((current, total))

        with patch.object(importer.client, "store_memory", return_value={"status": "stored"}):
            result = await importer.import_memories(
                memories=memories,
                user_id="user123",
                dry_run=False,
                batch_size=5,
                parallel=True,
                progress_callback=track_progress,
            )

            assert result["success"] == 15
            assert len(progress_calls) > 0

    @pytest.mark.asyncio
    async def test_import_batch_empty_list(self):
        """Test batch import with empty memory list."""
        importer = Mem0Importer(server_url="http://localhost:8000")

        with patch.object(importer.client, "store_memory", return_value={"status": "stored"}):
            result = await importer.import_memories(
                memories=[],
                user_id="user123",
                dry_run=False,
                batch_size=10,
                parallel=True,
            )

            assert result["total"] == 0
            assert result["success"] == 0
            assert result["skipped"] == 0


class TestExportImportFile:
    """Tests for export/import file utilities."""

    def test_save_export_file(self, tmp_path, sample_memories):
        """Test saving memories to export file."""
        output_file = tmp_path / "export.json"

        save_export_file(sample_memories, output_file)

        assert output_file.exists()

        data = json.loads(output_file.read_text())
        assert "exported_at" in data
        assert data["total_memories"] == 2
        assert len(data["memories"]) == 2

    def test_load_export_file(self, tmp_path, sample_memories):
        """Test loading memories from export file."""
        export_file = tmp_path / "export.json"

        export_data = {
            "exported_at": "2025-01-01T00:00:00Z",
            "total_memories": len(sample_memories),
            "memories": sample_memories,
        }

        export_file.write_text(json.dumps(export_data))

        memories = load_export_file(export_file)

        assert len(memories) == 2
        assert memories[0]["content"] == "User loves Python programming"

    def test_load_export_file_missing(self, tmp_path):
        """Test loading from missing file raises FileNotFoundError."""
        export_file = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            load_export_file(export_file)

    def test_load_export_file_invalid_json(self, tmp_path):
        """Test loading invalid JSON raises error."""
        export_file = tmp_path / "invalid.json"
        export_file.write_text("not valid json")

        with pytest.raises(json.JSONDecodeError):
            load_export_file(export_file)
