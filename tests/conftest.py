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
    (root / "workflows").mkdir()
    (root / "hooks").mkdir()

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
        "version: '1.0.0'\nproject_types: [backend, data]\ndescription: Test rule\n",
        encoding="utf-8",
    )
    (rule_dir / "RULE.md").write_text("# Test Rule\n", encoding="utf-8")

    skill_dir = root / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "manifest.yaml").write_text(
        "version: '1.0.0'\nproject_types: [backend, frontend, data, product]\ndescription: Test skill\n",
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text("# Test Skill\n", encoding="utf-8")

    workflow_dir = root / "workflows" / "test-workflow"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "manifest.yaml").write_text(
        "version: '1.0.0'\nproject_types: [backend, data]\ndescription: Test workflow\n",
        encoding="utf-8",
    )
    (workflow_dir / "WORKFLOW.md").write_text("# Test Workflow\n", encoding="utf-8")

    bundle_dir = root / "bundles" / "test-bundle"
    bundle_dir.mkdir(parents=True)
    (bundle_dir / "manifest.yaml").write_text(
        "version: '1.0.0'\nproject_types: [backend, data]\nitems:\n  - kind: rule\n    id: test-rule\n  - kind: skill\n    id: test-skill\n",
        encoding="utf-8",
    )

    hook_dir = root / "hooks" / "test-hook"
    hook_dir.mkdir(parents=True)
    (hook_dir / "manifest.yaml").write_text(
        "version: '1.0.0'\nproject_types: [backend, data]\ndescription: Test hook\n",
        encoding="utf-8",
    )
    (hook_dir / "HOOK.md").write_text("# Test Hook\n", encoding="utf-8")
    scripts_dir = hook_dir / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "test-hook.sh").write_text("#!/bin/bash\necho hello\n", encoding="utf-8")
    (hook_dir / "hooks.json").write_text(
        '{"PostToolUse": [{"matcher": "Write", "hooks": [{"type": "command", "command": "\\"$CLAUDE_PROJECT_DIR\\"/.claude/hooks/test-hook.sh", "statusMessage": "Running test hook..."}]}]}',
        encoding="utf-8",
    )

    return root


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Create a project dir with .forge/config.yaml (tool: cursor)."""
    root = tmp_path / "project"
    root.mkdir()
    forge_dir = root / ".forge"
    forge_dir.mkdir()
    (forge_dir / "config.yaml").write_text(
        "project_type: backend\nregistry:\n  url: https://example.com/registry.git\n  ref: main\ninstalled: []\n",
        encoding="utf-8",
    )
    return root


@pytest.fixture
def claude_code_project_root(tmp_path: Path) -> Path:
    """Create a project dir with .forge/config.yaml configured for claude-code."""
    root = tmp_path / "claude_project"
    root.mkdir()
    forge_dir = root / ".forge"
    forge_dir.mkdir()
    (forge_dir / "config.yaml").write_text(
        "project_types: [backend]\nregistry:\n  url: https://example.com/registry.git\n  ref: main\ntool: claude-code\ninstalled: []\n",
        encoding="utf-8",
    )
    return root
