"""
Memory management CLI commands for nanobot.

Provides commands to manage Mem0 memories, including listing,
searching, exporting, and importing.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from nanobot.memory.mem0_client import Mem0Client
from nanobot.memory.migration import Mem0Importer, save_export_file, load_export_file

memory_app = typer.Typer(help="Manage persistent memory")
console = Console()


@memory_app.command("list")
def memory_list(
    user_id: str = typer.Option(..., "--user", "-u", help="User ID to list memories for"),
    url: str = typer.Option("http://localhost:8000", "--url", help="Mem0 server URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Mem0 API key"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum number of memories"),
):
    """
    List all memories for a user.

    Example:
        nanobot memory list --user user123

        With custom server:
        nanobot memory list --user user123 --url http://localhost:8000
    """

    async def run_list():
        client = Mem0Client(server_url=url, api_key=api_key)

        try:
            memories = await client.list_user_memories(user_id=user_id, limit=limit)
            await client.close()
            return memories
        except Exception as e:
            await client.close()
            raise

    try:
        memories = asyncio.run(run_list())

        if not memories:
            console.print("[dim]No memories found.[/dim]")
            return

        table = Table(title=f"Memories for {user_id}")
        table.add_column("#", style="cyan", width=6)
        table.add_column("Content", style="white")
        table.add_column("Score", style="yellow", width=8)

        for idx, memory in enumerate(memories[:limit], 1):
            content = memory.get("content", "")[:60]
            if len(memory.get("content", "")) > 60:
                content += "..."
            score = memory.get("score", 0)
            table.add_row(str(idx), content, f"{score:.2f}" if score else "N/A")

        console.print(table)
        console.print(f"\n[dim]Total: {len(memories)} memories[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Failed to list memories: {e}[/red]")
        raise typer.Exit(1)


@memory_app.command("search")
def memory_search(
    user_id: str = typer.Option(..., "--user", "-u", help="User ID to search memories for"),
    query: str = typer.Argument(..., help="Search query"),
    url: str = typer.Option("http://localhost:8000", "--url", help="Mem0 server URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Mem0 API key"),
    limit: int = typer.Option(5, "--limit", "-l", help="Maximum number of results"),
):
    """
    Search memories by semantic similarity.

    Example:
        nanobot memory search --user user123 "Python programming"

        With more results:
        nanobot memory search --user user123 "favorite food" --limit 10
    """

    async def run_search():
        client = Mem0Client(server_url=url, api_key=api_key)

        try:
            memories = await client.search_memories(user_id=user_id, query=query, limit=limit)
            await client.close()
            return memories
        except Exception as e:
            await client.close()
            raise

    try:
        memories = asyncio.run(run_search())

        if not memories:
            console.print(f"[dim]No memories found for query: '{query}'[/dim]")
            return

        table = Table(title=f"Search Results: '{query}'")
        table.add_column("#", style="cyan", width=6)
        table.add_column("Content", style="white")
        table.add_column("Score", style="yellow", width=8)

        for idx, memory in enumerate(memories, 1):
            content = memory.get("content", "")[:80]
            if len(memory.get("content", "")) > 80:
                content += "..."
            score = memory.get("score", 0)
            table.add_row(str(idx), content, f"{score:.2f}")

        console.print(table)
        console.print(f"\n[dim]Found: {len(memories)} memories[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Search failed: {e}[/red]")
        raise typer.Exit(1)


@memory_app.command("export")
def memory_export(
    user_id: str = typer.Option(..., "--user", "-u", help="User ID to export memories for"),
    output: Path = typer.Option(..., "--output", "-o", help="Output JSON file path"),
    url: str = typer.Option("http://localhost:8000", "--url", help="Mem0 server URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Mem0 API key"),
    limit: int = typer.Option(1000, "--limit", "-l", help="Maximum number of memories"),
):
    """
    Export memories to a JSON file for backup.

    Example:
        nanobot memory export --user user123 --output memories.json

        Export with limit:
        nanobot memory export --user user123 --output recent.json --limit 100
    """

    async def run_export():
        client = Mem0Client(server_url=url, api_key=api_key)

        try:
            memories = await client.list_user_memories(user_id=user_id, limit=limit)
            await client.close()
            return memories
        except Exception as e:
            await client.close()
            raise

    try:
        memories = asyncio.run(run_export())

        if not memories:
            console.print("[dim]No memories to export.[/dim]")
            return

        save_export_file(memories, output)

        console.print(f"[green]✓ Exported {len(memories)} memories to {output}[/green]")

    except Exception as e:
        console.print(f"[red]✗ Export failed: {e}[/red]")
        raise typer.Exit(1)


@memory_app.command("import")
def memory_import(
    input: Path = typer.Option(..., "--input", "-i", help="Input JSON file path"),
    user_id: str = typer.Option(..., "--user", "-u", help="User ID to import memories for"),
    url: str = typer.Option("http://localhost:8000", "--url", help="Mem0 server URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Mem0 API key"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Validate without importing"),
):
    """
    Import memories from a JSON export file.

    Example:
        nanobot memory import --input memories.json --user user123

        Dry run (validate only):
        nanobot memory import --input memories.json --user user123 --dry-run
    """
    if not input.exists():
        console.print(f"[red]✗ Export file not found: {input}[/red]")
        raise typer.Exit(1)

    try:
        memories = load_export_file(input)
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ Invalid JSON file: {e}[/red]")
        raise typer.Exit(1)

    async def run_import():
        importer = Mem0Importer(server_url=url, api_key=api_key)

        try:
            results = await importer.import_memories(
                memories=memories, user_id=user_id, dry_run=dry_run
            )
            await importer.close()
            return results
        except Exception as e:
            await importer.close()
            raise

    try:
        results = asyncio.run(run_import())

        if dry_run:
            console.print(f"[cyan]Dry run results:[/cyan]")
        else:
            console.print(f"[green]✓ Import complete[/green]")

        console.print(f"  Total: {results['total']}")
        console.print(f"  Success: {results['success']}")
        console.print(f"  Skipped: {results['skipped']}")

        if results["errors"]:
            console.print(f"  Errors: {len(results['errors'])}")
            for error in results["errors"][:5]:
                console.print(f"    [red]✗[/red] {error}")
            if len(results["errors"]) > 5:
                console.print(f"    [dim]... and {len(results['errors']) - 5} more[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Import failed: {e}[/red]")
        raise typer.Exit(1)


@memory_app.command("health")
def memory_health(
    url: str = typer.Option("http://localhost:8000", "--url", help="Mem0 server URL"),
):
    """
    Check if Mem0 server is healthy and accessible.

    Example:
        nanobot memory health

        With custom URL:
        nanobot memory health --url http://localhost:8000
    """

    async def run_health():
        client = Mem0Client(server_url=url)

        try:
            healthy = await client.health_check()
            await client.close()
            return healthy
        except Exception:
            await client.close()
            return False

    try:
        healthy = asyncio.run(run_health())

        if healthy:
            console.print(f"[green]✓ Mem0 server is healthy at {url}[/green]")
        else:
            console.print(f"[red]✗ Mem0 server is not accessible at {url}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Health check failed: {e}[/red]")
        raise typer.Exit(1)
