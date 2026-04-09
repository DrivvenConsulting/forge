"""Core logic for forge setup: detect, configure, and guide tool installation."""

import json
import platform
import shutil
from pathlib import Path
from typing import Any, Literal

from forge.core.models import HowToStep, SetupTool

CLAUDE_SETTINGS_PATH: Path = Path.home() / ".claude" / "settings.json"


def get_platform() -> Literal["macos", "linux", "windows"]:
    """Return the current OS as a catalog key."""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    if system == "Windows":
        return "windows"
    return "linux"


def load_claude_settings(settings_path: Path | None = None) -> dict[str, Any]:
    """Load ~/.claude/settings.json, returning {} if missing or malformed."""
    path = settings_path if settings_path is not None else CLAUDE_SETTINGS_PATH
    if not path.exists():
        return {}
    try:
        with path.open() as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_claude_settings(
    data: dict[str, Any], settings_path: Path | None = None
) -> None:
    """Write settings dict to settings_path atomically (tmp + rename).

    Creates parent directory if needed.
    """
    path = settings_path if settings_path is not None else CLAUDE_SETTINGS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".json.tmp")
    with tmp_path.open("w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    tmp_path.replace(path)


def is_mcp_configured(tool: SetupTool, settings_path: Path | None = None) -> bool:
    """Return True if tool.mcp_key already exists in settings mcpServers."""
    if tool.mcp_key is None:
        return False
    data = load_claude_settings(settings_path)
    return tool.mcp_key in data.get("mcpServers", {})


def configure_mcp(tool: SetupTool, settings_path: Path | None = None) -> None:
    """Add or overwrite the mcpServers entry for tool in settings.json.

    Idempotent. Preserves all other keys in the file.

    Raises:
        ValueError: If tool.kind != "mcp-server" or mcp_config is None.
    """
    if tool.kind != "mcp-server" or tool.mcp_config is None or tool.mcp_key is None:
        raise ValueError(f"Tool '{tool.id}' is not an MCP server tool.")
    data = load_claude_settings(settings_path)
    servers = data.setdefault("mcpServers", {})
    servers[tool.mcp_key] = {
        "command": tool.mcp_config.command,
        "args": tool.mcp_config.args,
        "env": dict(tool.mcp_config.env),
    }
    save_claude_settings(data, settings_path)


def is_cli_installed(tool: SetupTool) -> bool:
    """Return True if tool.check_command resolves on PATH via shutil.which."""
    if tool.kind != "cli" or tool.check_command is None:
        return False
    return shutil.which(tool.check_command[0]) is not None


def get_install_instructions(tool: SetupTool) -> list[str]:
    """Return platform-appropriate install command strings for display.

    Falls back to 'linux' commands if current platform has no entry.
    Returns [] if tool has no install_commands.
    """
    if not tool.install_commands:
        return []
    current = get_platform()
    return tool.install_commands.get(current) or tool.install_commands.get("linux") or []


def run_setup_for_tool(
    tool: SetupTool, settings_path: Path | None = None
) -> dict[str, Any]:
    """Run detection and configuration for a single tool.

    For CLI tools:
      - If installed: status="ok", already_done=True
      - If not installed: status="needs_action", install_instructions filled

    For MCP servers:
      - If already configured: status="ok", already_done=True
      - If not configured: calls configure_mcp(), status="configured", already_done=False
        (entry written with placeholder token — auth_steps shown to user)
    """
    result: dict[str, Any] = {
        "id": tool.id,
        "display_name": tool.display_name,
        "kind": tool.kind,
        "status": "ok",
        "already_done": False,
        "install_instructions": [],
        "auth_steps": tool.auth_steps,
        "post_install_steps": tool.post_install_steps,
        "env_vars_required": tool.env_vars_required,
    }

    if tool.kind == "cli":
        if is_cli_installed(tool):
            result["already_done"] = True
            result["status"] = "ok"
        else:
            result["status"] = "needs_action"
            result["install_instructions"] = get_install_instructions(tool)
    else:
        if is_mcp_configured(tool, settings_path):
            result["already_done"] = True
            result["status"] = "ok"
        else:
            configure_mcp(tool, settings_path)
            result["status"] = "configured"

    return result


def run_setup_all(settings_path: Path | None = None) -> list[dict[str, Any]]:
    """Run setup for every tool in the catalog."""
    from forge.core.setup_catalog import SETUP_TOOLS

    return [run_setup_for_tool(t, settings_path) for t in SETUP_TOOLS]
