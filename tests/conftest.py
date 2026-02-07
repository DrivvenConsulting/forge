"""Pytest fixtures: temp registry and project dirs."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_path_dir(tmp_path: Path) -> Path:
    """Return tmp_path as-is for use as project or registry root."""
    return tmp_path


@pytest.fixture
def registry_root(tmp_path: Path) -> Path:
    """Create a minimal registry layout under a temp dir (no git)."""
    root = tmp_path / "registry"
    root.mkdir()
    (root / "agents").mkdir()
    (root / "rules").mkdir()
    (root / "skills").mkdir()
    (root / "bundles").mkdir()

    agent_dir = root / "agents" / "test-agent"
    agent_dir.mkdir(parents=True)
    (agent_dir / "manifest.yaml").write_text(
        "version: '1.0.0'\nproject_types: [backend, data]\ndescription: Test agent\n",
        encoding="utf-8",
    )
    (agent_dir / "agent.md").write_text("# Test Agent\n", encoding="utf-8")

    rule_dir = root / "rules" / "test-rule"
    rule_dir.mkdir(parents=True)
    (rule_dir / "manifest.yaml").write_text(
        "version: '1.0.0'\nproject_types: [backend]\ndescription: Test rule\n",
        encoding="utf-8",
    )
    (rule_dir / "RULE.md").write_text("# Test Rule\n", encoding="utf-8")

    skill_dir = root / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "manifest.yaml").write_text(
        "version: '1.0.0'\nproject_types: [backend, frontend]\ndescription: Test skill\n",
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text("# Test Skill\n", encoding="utf-8")

    bundle_dir = root / "bundles" / "test-bundle"
    bundle_dir.mkdir(parents=True)
    (bundle_dir / "manifest.yaml").write_text(
        "version: '1.0.0'\nproject_types: [backend]\nitems:\n  - kind: rule\n    id: test-rule\n  - kind: skill\n    id: test-skill\n",
        encoding="utf-8",
    )

    return root


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Create a project dir with .forge/config.yaml."""
    root = tmp_path / "project"
    root.mkdir()
    forge_dir = root / ".forge"
    forge_dir.mkdir()
    (forge_dir / "config.yaml").write_text(
        "project_type: backend\nregistry:\n  url: https://example.com/registry.git\n  ref: main\ninstalled: []\n",
        encoding="utf-8",
    )
    return root
