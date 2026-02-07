"""Tests for project config load/save and find_project_root."""

from pathlib import Path

import pytest

from forge.core.models import ProjectConfig, RegistryConfig
from forge.core.project import find_project_root, load_config, save_config


def test_find_project_root_not_found(tmp_path: Path) -> None:
    assert find_project_root(tmp_path) is None


def test_find_project_root_found(project_root: Path) -> None:
    assert find_project_root(project_root) == project_root
    assert find_project_root(project_root / "subdir") == project_root


def test_load_config_missing(tmp_path: Path) -> None:
    assert load_config(tmp_path) is None


def test_load_config(project_root: Path) -> None:
    config = load_config(project_root)
    assert config is not None
    assert config.project_types == ["backend"]
    assert config.registry.url == "https://example.com/registry.git"
    assert config.registry.ref == "main"
    assert config.installed == []


def test_save_config(tmp_path: Path) -> None:
    forge_dir = tmp_path / ".forge"
    forge_dir.mkdir()
    config = ProjectConfig(
        project_types=["data"],
        registry=RegistryConfig(url="https://y.git", ref="v1"),
        installed=[],
    )
    save_config(tmp_path, config)
    loaded = load_config(tmp_path)
    assert loaded is not None
    assert loaded.project_types == ["data"]
    assert loaded.registry.ref == "v1"


def test_load_config_legacy_project_type(tmp_path: Path) -> None:
    forge_dir = tmp_path / ".forge"
    forge_dir.mkdir()
    (forge_dir / "config.yaml").write_text(
        "project_type: data\nregistry:\n  url: https://x.git\n  ref: main\ninstalled: []\n",
        encoding="utf-8",
    )
    loaded = load_config(tmp_path)
    assert loaded is not None
    assert loaded.project_types == ["data"]
