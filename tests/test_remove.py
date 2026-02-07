"""Tests for remove_item."""

from pathlib import Path

import pytest

from forge.core.install import install_item
from forge.core.project import load_config
from forge.core.registry import get_registry_items
from forge.core.remove import remove_item


def test_remove_item(registry_root: Path, project_root: Path) -> None:
    config = load_config(project_root)
    assert config is not None
    items = get_registry_items(registry_root)
    rule = next(i for i in items if i.kind == "rule" and i.id == "test-rule")
    install_item(registry_root, rule, project_root, config, "main")
    rule_path = project_root / ".cursor" / "rules" / "test-rule"
    assert rule_path.exists()
    config2 = load_config(project_root)
    assert config2 is not None
    ok = remove_item(project_root, config2, "rule", "test-rule")
    assert ok is True
    assert not rule_path.exists()
    config3 = load_config(project_root)
    assert config3 is not None
    assert len(config3.installed) == 0


def test_remove_item_not_installed(project_root: Path) -> None:
    config = load_config(project_root)
    assert config is not None
    ok = remove_item(project_root, config, "rule", "nonexistent")
    assert ok is False
