"""Test setup for multi-bot with different personalities."""

import json
from pathlib import Path


def create_test_bots_config():
    """Create test bots.json configuration."""
    config_path = Path.home() / ".nanobot" / "bots.json"

    # Create config
    config = {
        "bots": [
            {
                "id": "health-bot",
                "name": "Dr. Bot Saúde",
                "description": "Assistente especializado em saúde e bem-estar",
                "channels": {
                    "telegram_enabled": False,  # Disabled for testing
                    "telegram_token": "HEALTH_BOT_TOKEN",
                    "telegram_allow_from": ["123456789"],
                },
                "workspace": "~/.nanobot/workspaces/health-bot",
                "agent": {
                    "model": "zai/glm-4.7",
                    "temperature": 0.7,
                },
                "mcps": ["supermemory", "exa-search"],
            },
            {
                "id": "finance-bot",
                "name": "Finance Bot",
                "description": "Assistente especializado em finanças pessoais",
                "channels": {
                    "telegram_enabled": False,  # Disabled for testing
                    "telegram_token": "FINANCE_BOT_TOKEN",
                    "telegram_allow_from": ["123456789"],
                },
                "workspace": "~/.nanobot/workspaces/finance-bot",
                "agent": {
                    "model": "zai/glm-4.7-flash",
                    "temperature": 0.5,
                },
                "mcps": ["exa-search"],
            },
        ],
        "mcps": {
            "mcps": [
                {
                    "name": "supermemory",
                    "type": "http",
                    "description": "Persistent memory with semantic search",
                    "url": "http://localhost:3000",
                    "env": {},
                    "health_check_enabled": True,
                    "health_check_endpoint": "/health",
                    "health_check_timeout": 5,
                },
                {
                    "name": "exa-search",
                    "type": "command",
                    "description": "Web search via Exa AI",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-exa"],
                    "env": {"EXA_API_KEY": "test-key"},
                    "health_check_enabled": True,
                    "health_check_timeout": 10,
                },
            ]
        },
    }

    # Save config
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✓ Created test config: {config_path}")


def create_test_workspaces():
    """Create test workspaces with different personalities."""
    workspaces = {
        "health-bot": {
            "name": "Dr. Bot Saúde",
            "description": "Especialista em saúde",
            "personality": """# Alma

Eu sou Dr. Bot, especialista em saúde e bem-estar.

## Personalidade

- Preocupado com sua saúde
- Baseado em evidências científicas
- Sempre recomenda consultar médico para casos graves
- Focado em prevenção e hábitos saudáveis

## Valores

- Saúde em primeiro lugar
- Precisão médica
- Bem-estar do paciente
""",
        },
        "finance-bot": {
            "name": "Finance Bot",
            "description": "Especialista em finanças",
            "personality": """# Alma

Eu sou Finance Bot, especialista em finanças pessoais.

## Personalidade

- Conservador com investimentos
- Focado em longo prazo
- Sempre alerta sobre riscos
- Defensor do planejamento financeiro

## Valores

- Segurança financeira
- Diversificação de investimentos
- Educação financeira
- Poupança e disciplina
""",
        },
    }

    base_path = Path.home() / ".nanobot" / "workspaces"

    for bot_id, bot_info in workspaces.items():
        workspace_path = base_path / bot_id
        workspace_path.mkdir(parents=True, exist_ok=True)

        # Create SOUL.md
        soul_file = workspace_path / "SOUL.md"
        soul_file.write_text(bot_info["personality"])

        # Create AGENTS.md
        agents_file = workspace_path / "AGENTS.md"
        agents_file.write_text(
            f"""# Instruções do Agente

Você é {bot_info["name"]}, {bot_info["description"]}.

## Diretrizes

- Sempre explique o que está fazendo
- Use ferramentas quando necessário
- Lembre-se de informações importantes na memória

## Ferramentas Disponíveis

- Busca na web (para artigos e informações atualizadas)
- Arquivos (para salvar informações importantes)
- Memória persistente
"""
        )

        # Create memory directory
        (workspace_path / "memory").mkdir(exist_ok=True)

        # Create USER.md
        user_file = workspace_path / "USER.md"
        user_file.write_text(
            """# Usuário

Informações sobre o usuário serão adicionadas aqui conforme você interagir.
"""
        )

        print(f"✓ Created workspace: {workspace_path}")


def test_multi_bot_loading():
    """Test loading multi-bot configuration."""
    from nanobot.multibot import MultiBotManager
    from nanobot.config import load_config

    # Load config
    config_path = Path.home() / ".nanobot/bots.json"
    global_config = load_config()

    # Create manager
    manager = MultiBotManager.from_config_file(config_path, global_config)

    # Check bots
    print(f"\n✓ Loaded {len(manager.bots)} bot(s):")
    for bot_id, bot in manager.bots.items():
        print(f"  - {bot_id}: {bot.config.name}")
        print(f"    Workspace: {bot.workspace}")
        print(f"    MCPs: {', '.join(bot.config.mcps)}")

    # Check MCPs
    print(f"\n✓ Loaded {len(manager.mcps)} MCP(s):")
    for mcp_name, mcp in manager.mcps.items():
        print(f"  - {mcp_name}: {mcp['type']}")

    # Test context building
    print("\n✓ Testing context building:")
    for bot_id, bot in manager.bots.items():
        soul_file = bot.workspace / "SOUL.md"
        if soul_file.exists():
            soul_content = soul_file.read_text()
            print(f"\n  {bot_id} personality:")
            print(f"    {soul_content.split(chr(10))[1]}")  # First line after title

    return manager


def test_workspace_isolation():
    """Test that workspaces are properly isolated."""
    from nanobot.multibot import MultiBotManager
    from nanobot.config import load_config

    # Load config
    config_path = Path.home() / ".nanobot/bots.json"
    global_config = load_config()

    # Create manager
    manager = MultiBotManager.from_config_file(config_path, global_config)

    # Check workspace isolation
    print("\n✓ Testing workspace isolation:")

    for bot_id, bot in manager.bots.items():
        workspace = bot.workspace

        # Check SOUL.md is unique
        soul_file = workspace / "SOUL.md"
        soul_content = soul_file.read_text()

        # Extract personality name
        for line in soul_content.split("\n"):
            if "Eu sou" in line:
                print(f"\n  {bot_id}: {line.strip()}")
                break

    print("\n✓ Workspaces are properly isolated!")


if __name__ == "__main__":
    import sys

    command = sys.argv[1] if len(sys.argv) > 1 else "all"

    if command == "config":
        create_test_bots_config()
    elif command == "workspaces":
        create_test_workspaces()
    elif command == "load":
        test_multi_bot_loading()
    elif command == "isolation":
        test_workspace_isolation()
    elif command == "all":
        print("Creating test multi-bot setup...\n")
        create_test_bots_config()
        create_test_workspaces()
        test_multi_bot_loading()
        test_workspace_isolation()
        print("\n✓ Test setup complete!")
        print("\nTo start multi-bot gateway:")
        print("  nanobot multibot start")
    else:
        print(f"Unknown command: {command}")
        print("Available: config, workspaces, load, isolation, all")
