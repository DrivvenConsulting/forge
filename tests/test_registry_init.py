"""Tests for registry scaffold (is_registry_root, scaffold_registry)."""

from pathlib import Path

import pytest
import yaml

from forge.core.registry import REGISTRY_CATEGORIES
from forge.core.registry_init import is_registry_root, scaffold_registry


def test_is_registry_root_false_for_empty_dir(tmp_path: Path) -> None:
    assert is_registry_root(tmp_path) is False


def test_is_registry_root_true_when_any_category_exists(tmp_path: Path) -> None:
    (tmp_path / "agents").mkdir()
    assert is_registry_root(tmp_path) is True


def test_is_registry_root_true_for_full_layout(tmp_path: Path) -> None:
    for cat in REGISTRY_CATEGORIES:
        (tmp_path / cat).mkdir()
    assert is_registry_root(tmp_path) is True


def test_scaffold_registry_creates_four_dirs(tmp_path: Path) -> None:
    scaffold_registry(tmp_path, with_examples=False)
    for category in REGISTRY_CATEGORIES:
        d = tmp_path / category
        assert d.is_dir()
        assert (d / ".gitkeep").exists()


def test_scaffold_registry_with_examples_creates_example_items(tmp_path: Path) -> None:
    scaffold_registry(tmp_path, with_examples=True)
    for category in REGISTRY_CATEGORIES:
        d = tmp_path / category
        assert d.is_dir()
        assert (d / ".gitkeep").exists()
    example_agent = tmp_path / "agents" / "_example"
    assert example_agent.is_dir()
    assert (example_agent / "manifest.yaml").exists()
    assert (example_agent / "agent.md").exists()
    example_rule = tmp_path / "rules" / "_example"
    assert (example_rule / "manifest.yaml").exists()
    assert (example_rule / "RULE.md").exists()
    example_skill = tmp_path / "skills" / "_example"
    assert (example_skill / "manifest.yaml").exists()
    assert (example_skill / "SKILL.md").exists()
    example_bundle = tmp_path / "bundles" / "_example"
    assert (example_bundle / "manifest.yaml").exists()


def test_scaffold_registry_example_manifests_valid(tmp_path: Path) -> None:
    scaffold_registry(tmp_path, with_examples=True)
    agent_manifest = yaml.safe_load((tmp_path / "agents" / "_example" / "manifest.yaml").read_text())
    assert agent_manifest["version"] == "1.0.0"
    assert "project_types" in agent_manifest
    assert agent_manifest["project_types"] == ["backend"]
    rule_manifest = yaml.safe_load((tmp_path / "rules" / "_example" / "manifest.yaml").read_text())
    assert rule_manifest["version"] == "1.0.0"
    skill_manifest = yaml.safe_load((tmp_path / "skills" / "_example" / "manifest.yaml").read_text())
    assert skill_manifest["version"] == "1.0.0"
    bundle_manifest = yaml.safe_load((tmp_path / "bundles" / "_example" / "manifest.yaml").read_text())
    assert bundle_manifest["version"] == "1.0.0"
    assert bundle_manifest["items"] == [{"kind": "rule", "id": "_example"}]
