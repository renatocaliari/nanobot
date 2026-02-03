"""Simple test for multi-bot configuration and workspaces."""

import json
from pathlib import Path


def test_config_created():
    """Test that config file was created."""
    config_path = Path.home() / ".nanobot" / "bots.json"

    if not config_path.exists():
        print("❌ Config file not created")
        return False

    print(f"✓ Config file exists: {config_path}")

    # Load and validate config
    with open(config_path) as f:
        config = json.load(f)

    # Check structure
    assert "bots" in config, "Missing 'bots' key"
    assert "mcps" in config, "Missing 'mcps' key"

    print(f"✓ Config has {len(config['bots'])} bot(s)")
    print(f"✓ Config has {len(config['mcps']['mcps'])} MCP(s)")

    # Show bot details
    for bot in config["bots"]:
        print(f"\n  Bot: {bot['id']}")
        print(f"    Name: {bot['name']}")
        print(f"    Workspace: {bot['workspace']}")
        print(f"    MCPs: {', '.join(bot['mcps'])}")

    # Show MCP details
    print(f"\n  MCPs:")
    for mcp in config["mcps"]["mcps"]:
        print(f"    - {mcp['name']}: {mcp['type']}")

    return True


def test_workspaces_created():
    """Test that workspaces were created with different personalities."""
    base_path = Path.home() / ".nanobot" / "workspaces"

    if not base_path.exists():
        print("❌ Workspaces directory not created")
        return False

    print(f"✓ Workspaces directory exists: {base_path}")

    # Check for expected bots
    expected_bots = ["health-bot", "finance-bot"]
    found_bots = []

    for bot_id in expected_bots:
        workspace = base_path / bot_id

        if not workspace.exists():
            print(f"❌ Workspace not found: {bot_id}")
            continue

        found_bots.append(bot_id)

        # Check SOUL.md
        soul_file = workspace / "SOUL.md"
        if not soul_file.exists():
            print(f"❌ SOUL.md not found for {bot_id}")
            continue

        print(f"\n✓ Workspace {bot_id}:")

        # Read and show personality
        soul_content = soul_file.read_text()

        # Extract first few lines
        lines = soul_content.split("\n")[:5]
        for line in lines:
            if line.strip():
                print(f"  {line}")

        # Check AGENTS.md
        agents_file = workspace / "AGENTS.md"
        if agents_file.exists():
            print(f"  ✓ AGENTS.md exists")
        else:
            print(f"  ⚠ AGENTS.md missing")

        # Check memory directory
        memory_dir = workspace / "memory"
        if memory_dir.exists():
            print(f"  ✓ memory/ directory exists")
        else:
            print(f"  ⚠ memory/ directory missing")

    print(f"\n✓ Found {len(found_bots)}/{len(expected_bots)} expected workspace(s)")

    return len(found_bots) == len(expected_bots)


def test_workspace_isolation():
    """Test that workspaces have different personalities."""
    base_path = Path.home() / ".nanobot" / "workspaces"

    personalities = {}

    for bot_id in ["health-bot", "finance-bot"]:
        workspace = base_path / bot_id
        soul_file = workspace / "SOUL.md"

        if soul_file.exists():
            soul_content = soul_file.read_text()
            personalities[bot_id] = soul_content

    if len(personalities) < 2:
        print("❌ Not enough workspaces to test isolation")
        return False

    print("\n✓ Testing workspace isolation:")

    # Check that personalities are different
    health = personalities.get("health-bot", "")
    finance = personalities.get("finance-bot", "")

    if health == finance:
        print("❌ Personalities are identical!")
        return False

    print("✓ Personalities are different:")
    print(f"  Health bot: {health.split(chr(10))[1] if health else 'N/A'}")
    print(f"  Finance bot: {finance.split(chr(10))[1] if finance else 'N/A'}")

    return True


def test_mcp_config():
    """Test MCP configuration."""
    config_path = Path.home() / ".nanobot" / "mcp.json"

    if not config_path.exists():
        print("⚠ mcp.json not created (using bots.json embedded config)")
        # Check bots.json instead
        config_path = Path.home() / ".nanobot" / "bots.json"

    with open(config_path) as f:
        config = json.load(f)

    # Extract MCPs from config
    if "mcps" in config and "mcps" in config["mcps"]:
        mcps = config["mcps"]["mcps"]
    else:
        print("❌ No MCPs found in config")
        return False

    print(f"\n✓ MCP configuration:")
    for mcp in mcps:
        print(f"  - {mcp['name']}")
        print(f"    Type: {mcp['type']}")
        print(f"    Description: {mcp['description']}")

        if mcp["type"] == "command":
            print(f"    Command: {mcp['command']} {' '.join(mcp['args'])}")
        elif mcp["type"] == "http":
            print(f"    URL: {mcp['url']}")

    return True


if __name__ == "__main__":
    import sys

    command = sys.argv[1] if len(sys.argv) > 1 else "all"

    print("=" * 60)
    print("Multi-Bot Test Suite")
    print("=" * 60)

    results = {}

    if command in ["all", "config"]:
        print("\n[1/4] Testing configuration...")
        results["config"] = test_config_created()

    if command in ["all", "workspaces"]:
        print("\n[2/4] Testing workspaces...")
        results["workspaces"] = test_workspaces_created()

    if command in ["all", "isolation"]:
        print("\n[3/4] Testing isolation...")
        results["isolation"] = test_workspace_isolation()

    if command in ["all", "mcps"]:
        print("\n[4/4] Testing MCP configuration...")
        results["mcps"] = test_mcp_config()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 60)

    sys.exit(0 if all_passed else 1)
