"""MCP status checker tool for nanobot."""

import httpx
import json
from pathlib import Path
from typing import Any


def check_mcp_status() -> str:
    """
    Check status of all configured MCP servers.

    Returns:
        Formatted status report of all MCPs.
    """
    # Read MCP configuration
    mcp_config_path = Path.home() / ".nanobot" / "mcp.json"

    if not mcp_config_path.exists():
        return "❌ Nenhum MCP configurado. Crie ~/.nanobot/mcp.json"

    with open(mcp_config_path) as f:
        config_data = json.load(f)

    # Extract MCPs from config
    mcps = config_data.get("mcps", [])

    if not mcps:
        return "❌ Nenhum MCP configurado em mcp.json"

    # Check each MCP
    report_lines = ["# 📊 MCP Servers Status\n"]
    report_lines.append(f"## Configurados: {len(mcps)}\n")

    active_count = 0
    for i, mcp in enumerate(mcps, 1):
        name = mcp.get("name", "unknown")
        mcp_type = mcp.get("type", "unknown")
        description = mcp.get("description", "")

        # Check status
        if mcp_type == "http":
            status = check_http_mcp(mcp.get("url", ""), mcp.get("health_check_endpoint", "/health"))
            status_text = "✅ Ativo" if status else "❌ Inativo"
            if status:
                active_count += 1

            report_lines.append(f"### {i}. {name} {status_text}")
            report_lines.append(f"- **Tipo**: HTTP")
            report_lines.append(f"- **URL**: {mcp.get('url', 'N/A')}")
            report_lines.append(f"- **Descrição**: {description}")
            report_lines.append(f"- **Status**: {'Respondendo' if status else 'Não respondendo'}\n")

        elif mcp_type == "command":
            status = check_command_mcp(mcp.get("command", ""), mcp.get("args", []))
            status_text = "✅ Rodando" if status else "❌ Parado"
            if status:
                active_count += 1

            cmd_str = f"{mcp.get('command', '')} {' '.join(mcp.get('args', []))}"
            report_lines.append(f"### {i}. {name} {status_text}")
            report_lines.append(f"- **Tipo**: Command")
            report_lines.append(f"- **Comando**: {cmd_str}")
            report_lines.append(f"- **Descrição**: {description}")
            report_lines.append(
                f"- **Status**: {'Processo rodando' if status else 'Processo não encontrado'}\n"
            )

    # Summary
    report_lines.append(f"**Resumo**: {active_count}/{len(mcps)} MCPs ativos")

    return "\n".join(report_lines)


def check_http_mcp(url: str, health_endpoint: str = "/health") -> bool:
    """Check if HTTP MCP server is responding."""
    if not url:
        return False

    try:
        response = httpx.get(f"{url}{health_endpoint}", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def check_command_mcp(command: str, args: list[str]) -> bool:
    """Check if command MCP process is running."""
    if not command:
        return False

    try:
        import psutil

        # Check if any process matches the command
        for proc in psutil.process_iter(["cmdline"]):
            try:
                cmdline = proc.info.get("cmdline", [])
                if cmdline:
                    cmdline_str = " ".join(cmdline)
                    # Check if command is in the process command line
                    if command in cmdline_str:
                        # Also check args if provided
                        if args:
                            args_match = all(arg in cmdline_str for arg in args)
                            if args_match:
                                return True
                        else:
                            return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return False
    except ImportError:
        # psutil not available, can't check
        return None
    except Exception:
        return False


# Register as tool
def register_mcp_status_tools(tool_registry: dict[str, Any]) -> None:
    """Register MCP status checker tools."""
    tool_registry["check_mcp_status"] = {
        "function": check_mcp_status,
        "description": "Check status of all configured MCP servers",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }
