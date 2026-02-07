"""Tests for forge list CLI (registry and --installed)."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from forge.cli.main import app
from forge.core.models import InstalledItem
from forge.core.project import load_config, save_config

runner = CliRunner()


def test_list_installed_shows_installed_items(project_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = load_config(project_root)
    assert config is not None
    config.installed = [
        InstalledItem(kind="rule", id="my-rule", version="1.0.0", source_registry_ref="main"),
        InstalledItem(kind="agent", id="my-agent", version="2.0.0", source_registry_ref="main"),
    ]
    save_config(project_root, config)

    monkeypatch.chdir(project_root)
    result = runner.invoke(app, ["list", "--installed"])
    assert result.exit_code == 0
    assert "my-rule" in result.output
    assert "my-agent" in result.output
    assert "1.0.0" in result.output
    assert "2.0.0" in result.output
    assert "main" in result.output


def test_list_installed_empty(project_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(project_root)
    result = runner.invoke(app, ["list", "--installed"])
    assert result.exit_code == 0
    assert "No installed items" in result.output


def test_list_installed_filtered_by_category(project_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = load_config(project_root)
    assert config is not None
    config.installed = [
        InstalledItem(kind="rule", id="r1", version="1.0.0", source_registry_ref="main"),
        InstalledItem(kind="agent", id="a1", version="1.0.0", source_registry_ref="main"),
    ]
    save_config(project_root, config)

    monkeypatch.chdir(project_root)
    result = runner.invoke(app, ["list", "--installed", "--category", "rule"])
    assert result.exit_code == 0
    assert "r1" in result.output
    assert "a1" not in result.output
