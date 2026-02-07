"""Tests for install (single item and bundle)."""

from pathlib import Path

import pytest

from forge.core.install import install_bundle, install_item
from forge.core.models import ProjectConfig, RegistryConfig
from forge.core.project import load_config, save_config
from forge.core.registry import get_registry_items


def test_install_agent(registry_root: Path, project_root: Path) -> None:
    config = load_config(project_root)
    assert config is not None
    items = get_registry_items(registry_root)
    agent = next(i for i in items if i.kind == "agent" and i.id == "test-agent")
    install_item(registry_root, agent, project_root, config, "main")
    dest = project_root / ".cursor" / "agents" / "test-agent.md"
    assert dest.exists()
    assert "Test Agent" in dest.read_text()
    config2 = load_config(project_root)
    assert config2 is not None
    assert len(config2.installed) == 1
    assert config2.installed[0].kind == "agent" and config2.installed[0].id == "test-agent"


def test_install_rule(registry_root: Path, project_root: Path) -> None:
    config = load_config(project_root)
    assert config is not None
    items = get_registry_items(registry_root)
    rule = next(i for i in items if i.kind == "rule" and i.id == "test-rule")
    install_item(registry_root, rule, project_root, config, "main")
    dest = project_root / ".cursor" / "rules" / "test-rule" / "RULE.md"
    assert dest.exists()
    assert "Test Rule" in dest.read_text()


def test_install_skill(registry_root: Path, project_root: Path) -> None:
    config = load_config(project_root)
    assert config is not None
    items = get_registry_items(registry_root)
    skill = next(i for i in items if i.kind == "skill" and i.id == "test-skill")
    install_item(registry_root, skill, project_root, config, "main")
    dest = project_root / ".cursor" / "skills" / "test-skill" / "SKILL.md"
    assert dest.exists()


def test_install_bundle(registry_root: Path, project_root: Path) -> None:
    config = load_config(project_root)
    assert config is not None
    items = get_registry_items(registry_root)
    by_kind_id = {(i.kind, i.id): i for i in items}
    bundle = by_kind_id[("bundle", "test-bundle")]
    install_bundle(registry_root, bundle, by_kind_id, project_root, config, "main")
    assert (project_root / ".cursor" / "rules" / "test-rule" / "RULE.md").exists()
    assert (project_root / ".cursor" / "skills" / "test-skill" / "SKILL.md").exists()
    config2 = load_config(project_root)
    assert config2 is not None
    assert len(config2.installed) == 2
