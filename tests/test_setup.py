"""Tests for forge setup core logic and CLI."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from forge.cli.main import app
from forge.core.models import HowToStep, MCPServerConfig, SetupTool
from forge.core.setup import (
    configure_mcp,
    get_install_instructions,
    get_platform,
    is_cli_installed,
    is_mcp_configured,
    load_claude_settings,
    run_setup_all,
    run_setup_for_tool,
    save_claude_settings,
)
from forge.core.setup_catalog import SETUP_TOOLS, SETUP_TOOLS_BY_ID

runner = CliRunner()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mcp_tool() -> SetupTool:
    return SETUP_TOOLS_BY_ID["github-mcp"]


@pytest.fixture
def cli_tool() -> SetupTool:
    return SETUP_TOOLS_BY_ID["github-cli"]


@pytest.fixture
def settings_file(tmp_path: Path) -> Path:
    return tmp_path / ".claude" / "settings.json"


# ---------------------------------------------------------------------------
# load_claude_settings / save_claude_settings
# ---------------------------------------------------------------------------


def test_load_settings_missing_file_returns_empty_dict(tmp_path: Path) -> None:
    result = load_claude_settings(tmp_path / "nonexistent.json")
    assert result == {}


def test_load_settings_invalid_json_returns_empty_dict(tmp_path: Path) -> None:
    bad = tmp_path / "settings.json"
    bad.write_text("not json {{{")
    assert load_claude_settings(bad) == {}


def test_load_settings_non_dict_json_returns_empty_dict(tmp_path: Path) -> None:
    f = tmp_path / "settings.json"
    f.write_text('["a", "b"]')
    assert load_claude_settings(f) == {}


def test_save_and_reload_roundtrip(tmp_path: Path) -> None:
    f = tmp_path / "settings.json"
    data = {"mcpServers": {"github": {"command": "npx", "args": [], "env": {}}}}
    save_claude_settings(data, f)
    assert load_claude_settings(f) == data


def test_save_settings_creates_parent_directory(tmp_path: Path) -> None:
    f = tmp_path / "nested" / "dir" / "settings.json"
    save_claude_settings({"key": "value"}, f)
    assert f.exists()
    assert json.loads(f.read_text()) == {"key": "value"}


def test_save_settings_atomic_write_leaves_no_tmp(tmp_path: Path) -> None:
    f = tmp_path / "settings.json"
    save_claude_settings({"x": 1}, f)
    tmp = f.with_suffix(".json.tmp")
    assert not tmp.exists()


def test_save_settings_uses_indent_2(tmp_path: Path) -> None:
    f = tmp_path / "settings.json"
    save_claude_settings({"a": {"b": 1}}, f)
    content = f.read_text()
    assert '  "a"' in content  # indented with 2 spaces


# ---------------------------------------------------------------------------
# is_mcp_configured / configure_mcp
# ---------------------------------------------------------------------------


def test_is_mcp_configured_when_not_configured(mcp_tool: SetupTool, settings_file: Path) -> None:
    assert not is_mcp_configured(mcp_tool, settings_file)


def test_is_mcp_configured_when_already_configured(
    mcp_tool: SetupTool, settings_file: Path
) -> None:
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    settings_file.write_text(json.dumps({"mcpServers": {"github": {}}}))
    assert is_mcp_configured(mcp_tool, settings_file)


def test_configure_mcp_writes_correct_entry(mcp_tool: SetupTool, settings_file: Path) -> None:
    configure_mcp(mcp_tool, settings_file)
    data = load_claude_settings(settings_file)
    assert "mcpServers" in data
    entry = data["mcpServers"]["github"]
    assert entry["command"] == "npx"
    assert "-y" in entry["args"]
    assert "GITHUB_TOKEN" in entry["env"]


def test_configure_mcp_preserves_existing_keys(mcp_tool: SetupTool, settings_file: Path) -> None:
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    settings_file.write_text(json.dumps({"someOtherSetting": True}))
    configure_mcp(mcp_tool, settings_file)
    data = load_claude_settings(settings_file)
    assert data["someOtherSetting"] is True
    assert "mcpServers" in data


def test_configure_mcp_is_idempotent(mcp_tool: SetupTool, settings_file: Path) -> None:
    configure_mcp(mcp_tool, settings_file)
    configure_mcp(mcp_tool, settings_file)
    data = load_claude_settings(settings_file)
    assert len(data["mcpServers"]) == 1


def test_configure_mcp_raises_for_cli_tool(cli_tool: SetupTool, settings_file: Path) -> None:
    with pytest.raises(ValueError):
        configure_mcp(cli_tool, settings_file)


# ---------------------------------------------------------------------------
# is_cli_installed
# ---------------------------------------------------------------------------


def test_is_cli_installed_returns_true_when_which_finds_binary(
    monkeypatch: pytest.MonkeyPatch, cli_tool: SetupTool
) -> None:
    monkeypatch.setattr("forge.core.setup.shutil.which", lambda _: "/usr/bin/gh")
    assert is_cli_installed(cli_tool)


def test_is_cli_installed_returns_false_when_which_returns_none(
    monkeypatch: pytest.MonkeyPatch, cli_tool: SetupTool
) -> None:
    monkeypatch.setattr("forge.core.setup.shutil.which", lambda _: None)
    assert not is_cli_installed(cli_tool)


def test_is_cli_installed_returns_false_for_mcp_tool(mcp_tool: SetupTool) -> None:
    assert not is_cli_installed(mcp_tool)


# ---------------------------------------------------------------------------
# get_install_instructions
# ---------------------------------------------------------------------------


def test_get_install_instructions_macos(
    monkeypatch: pytest.MonkeyPatch, cli_tool: SetupTool
) -> None:
    monkeypatch.setattr("forge.core.setup.platform.system", lambda: "Darwin")
    instructions = get_install_instructions(cli_tool)
    assert any("brew" in cmd for cmd in instructions)


def test_get_install_instructions_linux(
    monkeypatch: pytest.MonkeyPatch, cli_tool: SetupTool
) -> None:
    monkeypatch.setattr("forge.core.setup.platform.system", lambda: "Linux")
    instructions = get_install_instructions(cli_tool)
    assert any("apt" in cmd or "dnf" in cmd for cmd in instructions)


def test_get_install_instructions_unknown_platform_falls_back_to_linux(
    monkeypatch: pytest.MonkeyPatch, cli_tool: SetupTool
) -> None:
    monkeypatch.setattr("forge.core.setup.platform.system", lambda: "FreeBSD")
    instructions = get_install_instructions(cli_tool)
    assert len(instructions) > 0  # falls back to linux


def test_get_install_instructions_returns_empty_for_mcp_tool(mcp_tool: SetupTool) -> None:
    assert get_install_instructions(mcp_tool) == []


# ---------------------------------------------------------------------------
# run_setup_for_tool
# ---------------------------------------------------------------------------


def test_run_setup_for_cli_tool_already_installed(
    monkeypatch: pytest.MonkeyPatch, cli_tool: SetupTool, settings_file: Path
) -> None:
    monkeypatch.setattr("forge.core.setup.shutil.which", lambda _: "/usr/bin/gh")
    result = run_setup_for_tool(cli_tool, settings_file)
    assert result["already_done"] is True
    assert result["status"] == "ok"
    assert result["install_instructions"] == []


def test_run_setup_for_cli_tool_not_installed(
    monkeypatch: pytest.MonkeyPatch, cli_tool: SetupTool, settings_file: Path
) -> None:
    monkeypatch.setattr("forge.core.setup.shutil.which", lambda _: None)
    result = run_setup_for_tool(cli_tool, settings_file)
    assert result["already_done"] is False
    assert result["status"] == "needs_action"
    assert len(result["install_instructions"]) > 0


def test_run_setup_for_mcp_tool_not_configured_writes_settings(
    mcp_tool: SetupTool, settings_file: Path
) -> None:
    result = run_setup_for_tool(mcp_tool, settings_file)
    assert result["already_done"] is False
    assert result["status"] == "configured"
    assert settings_file.exists()
    data = load_claude_settings(settings_file)
    assert "github" in data["mcpServers"]
    assert len(result["auth_steps"]) > 0


def test_run_setup_for_mcp_tool_already_configured(
    mcp_tool: SetupTool, settings_file: Path
) -> None:
    configure_mcp(mcp_tool, settings_file)
    result = run_setup_for_tool(mcp_tool, settings_file)
    assert result["already_done"] is True
    assert result["status"] == "ok"


# ---------------------------------------------------------------------------
# run_setup_all
# ---------------------------------------------------------------------------


def test_run_setup_all_returns_one_result_per_catalog_tool(
    monkeypatch: pytest.MonkeyPatch, settings_file: Path
) -> None:
    monkeypatch.setattr("forge.core.setup.shutil.which", lambda _: None)
    # Patch run_setup_all to use tmp settings path
    import forge.core.setup as setup_module

    original = setup_module.run_setup_all

    results = run_setup_all(settings_file)
    assert len(results) == len(SETUP_TOOLS)
    ids = [r["id"] for r in results]
    for tool in SETUP_TOOLS:
        assert tool.id in ids


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------


def test_setup_list_exits_zero() -> None:
    result = runner.invoke(app, ["setup", "list"])
    assert result.exit_code == 0


def test_setup_tool_unknown_exits_one() -> None:
    result = runner.invoke(app, ["setup", "tool", "nonexistent-tool"])
    assert result.exit_code == 1
    assert "Unknown tool" in result.output


def test_setup_tool_github_mcp_writes_settings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    settings_path = tmp_path / "settings.json"
    import forge.core.setup as setup_module

    monkeypatch.setattr(setup_module, "CLAUDE_SETTINGS_PATH", settings_path)

    result = runner.invoke(app, ["setup", "tool", "github-mcp"])
    assert result.exit_code == 0
    assert settings_path.exists()
    data = json.loads(settings_path.read_text())
    assert "github" in data["mcpServers"]


def test_setup_no_subcommand_runs_all_tools(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    settings_path = tmp_path / "settings.json"
    import forge.core.setup as setup_module

    monkeypatch.setattr(setup_module, "CLAUDE_SETTINGS_PATH", settings_path)
    monkeypatch.setattr("forge.core.setup.shutil.which", lambda _: None)

    result = runner.invoke(app, ["setup"])
    assert result.exit_code == 0
    # All tool display names should appear in the output
    for tool in SETUP_TOOLS:
        assert tool.display_name in result.output
