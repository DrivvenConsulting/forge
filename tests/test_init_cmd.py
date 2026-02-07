"""Tests for forge init CLI (project init and registry init)."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from forge.cli.main import app
from forge.core.registry import REGISTRY_CATEGORIES

runner = CliRunner()


def test_init_registry_creates_four_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "--registry"])
    assert result.exit_code == 0
    assert "Initialized Forge registry" in result.output
    for category in REGISTRY_CATEGORIES:
        assert (tmp_path / category).is_dir()
        assert (tmp_path / category / ".gitkeep").exists()


def test_init_registry_with_examples_creates_example_items(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "--registry", "--with-examples"])
    assert result.exit_code == 0
    assert "Example items were added" in result.output
    assert (tmp_path / "agents" / "_example" / "manifest.yaml").exists()
    assert (tmp_path / "agents" / "_example" / "agent.md").exists()
    assert (tmp_path / "rules" / "_example" / "RULE.md").exists()
    assert (tmp_path / "skills" / "_example" / "SKILL.md").exists()
    assert (tmp_path / "bundles" / "_example" / "manifest.yaml").exists()


def test_init_registry_inside_project_root_exits_without_changes(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(project_root)
    result = runner.invoke(app, ["init", "--registry"])
    assert result.exit_code == 1
    assert "Cannot initialize registry inside a Forge project" in result.output
    for category in REGISTRY_CATEGORIES:
        assert not (project_root / category).exists()


def test_init_registry_when_layout_already_present_exits_without_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "agents").mkdir()
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "--registry"])
    assert result.exit_code == 1
    assert "Registry layout already present" in result.output
    assert not (tmp_path / "rules").exists()


def test_init_project_creates_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "--project-type", "backend"])
    assert result.exit_code == 0
    assert (tmp_path / ".forge" / "config.yaml").exists()
    assert "Initialized Forge in" in result.output
