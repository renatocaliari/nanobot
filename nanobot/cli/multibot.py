"""Multi-bot gateway entry point."""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from nanobot.config import load_config
from nanobot.multibot import MultiBotManager, MultiTelegramChannel

app = typer.Typer(help="Multi-bot gateway commands")
console = Console()


@app.command()
def start(
    config: str = typer.Option(
        "~/.nanobot/bots.json",
        "--config",
        "-c",
        help="Path to multi-bot configuration file",
    ),
):
    """Start multiple bot instances."""
    from loguru import logger

    # Load configuration
    config_path = Path(config).expanduser()

    if not config_path.exists():
        console.print(f"[red]Configuration file not found: {config_path}[/red]")
        console.print("\n[yellow]Create a configuration file first:[/yellow]")
        console.print("  cp bots.json.example ~/.nanobot/bots.json")
        console.print("  nano ~/.nanobot/bots.json")
        raise typer.Exit(1)

    # Load global config
    global_config = load_config()

    # Create multi-bot manager
    multi_bot_manager = MultiBotManager.from_config_file(config_path, global_config)

    # Show bots to be started
    table = Table(title="Multi-Bot Gateway")
    table.add_column("Bot ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Workspace", style="blue")
    table.add_column("MCPs", style="yellow")

    for bot in multi_bot_manager.config.bots:
        table.add_row(
            bot.id,
            bot.name,
            str(bot.workspace_path),
            ", ".join(bot.mcps) if bot.mcps else "None",
        )

    console.print(table)
    console.print(f"\n[green]Starting {len(multi_bot_manager.bots)} bot(s)...[/green]\n")

    # Create multi-Telegram channel
    telegram_channel = MultiTelegramChannel(multi_bot_manager, multi_bot_manager.bus)

    # Start everything
    try:
        # Start bots
        asyncio.run(multi_bot_manager.start_all())

        # Start Telegram channel
        asyncio.run(telegram_channel.start())

        # Keep running
        console.print("[green]✓ All bots started successfully![/green]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")

        # Run forever
        loop = asyncio.get_event_loop()
        loop.run_forever()

    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping all bots...[/yellow]")

        # Stop Telegram channel
        asyncio.run(telegram_channel.stop())

        # Stop bots
        asyncio.run(multi_bot_manager.stop_all())

        console.print("[green]✓ All bots stopped[/green]")


@app.command()
def status(
    config: str = typer.Option(
        "~/.nanobot/bots.json",
        "--config",
        "-c",
        help="Path to multi-bot configuration file",
    ),
):
    """Show status of configured bots."""
    from loguru import logger

    # Load configuration
    config_path = Path(config).expanduser()

    if not config_path.exists():
        console.print(f"[red]Configuration file not found: {config_path}[/red]")
        raise typer.Exit(1)

    # Load global config
    global_config = load_config()

    # Create multi-bot manager (won't start bots)
    multi_bot_manager = MultiBotManager.from_config_file(config_path, global_config)

    # Show status
    table = Table(title="Multi-Bot Configuration")
    table.add_column("Bot ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Telegram Enabled", style="yellow")
    table.add_column("Workspace", style="blue")
    table.add_column("MCPs", style="magenta")

    for bot in multi_bot_manager.config.bots:
        telegram_status = "✓" if bot.channels.telegram_enabled else "✗"
        workspace_exists = "✓" if bot.workspace_path.exists() else "✗"

        table.add_row(
            bot.id,
            bot.name,
            telegram_status,
            f"{str(bot.workspace_path)} [{workspace_exists}]",
            ", ".join(bot.mcps) if bot.mcps else "None",
        )

    console.print(table)

    # Show MCPs
    if multi_bot_manager.config.mcps.mcps:
        console.print("\n[bold]Configured MCPs:[/bold]")
        mcp_table = Table()
        mcp_table.add_column("Name", style="cyan")
        mcp_table.add_column("Type", style="green")
        mcp_table.add_column("Description", style="blue")

        for mcp in multi_bot_manager.config.mcps.mcps:
            mcp_table.add_row(mcp.name, mcp.type, mcp.description)

        console.print(mcp_table)


if __name__ == "__main__":
    app()
