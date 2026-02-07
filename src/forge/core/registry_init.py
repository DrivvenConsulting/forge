"""Scaffold a new Forge registry repo (agents/, rules/, skills/, bundles/)."""

import yaml
from pathlib import Path

from forge.core.registry import REGISTRY_CATEGORIES


def is_registry_root(path: Path) -> bool:
    """Return True if path contains any of the registry category directories.

    Args:
        path: Directory to check (e.g. current working directory).

    Returns:
        True if any of agents/, rules/, skills/, or bundles/ exist under path.
    """
    root = Path(path).resolve()
    if not root.is_dir():
        return False
    return any((root / category).is_dir() for category in REGISTRY_CATEGORIES)


def scaffold_registry(root: Path, with_examples: bool = False) -> None:
    """Create registry directory layout and optionally example items.

    Creates agents/, rules/, skills/, bundles/ with a .gitkeep in each.
    If with_examples is True, adds one minimal example item per category
    with valid manifest.yaml and placeholder content files.

    Args:
        root: Directory to create the registry in (e.g. Path.cwd()).
        with_examples: If True, add _example agent, rule, skill, and bundle.
    """
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)

    for category in REGISTRY_CATEGORIES:
        category_dir = root / category
        category_dir.mkdir(parents=True, exist_ok=True)
        (category_dir / ".gitkeep").write_text("", encoding="utf-8")

    if not with_examples:
        return

    _write_example_agent(root)
    _write_example_rule(root)
    _write_example_skill(root)
    _write_example_bundle(root)


def _write_example_agent(root: Path) -> None:
    item_id = "_example"
    item_dir = root / "agents" / item_id
    item_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": "1.0.0",
        "project_types": ["backend"],
        "description": "Example agent. Replace with your own agent prompt.",
    }
    with open(item_dir / "manifest.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(manifest, f, default_flow_style=False, sort_keys=False)
    (item_dir / "agent.md").write_text(
        "# Example Agent\n\nReplace this file with your agent instructions.\n",
        encoding="utf-8",
    )


def _write_example_rule(root: Path) -> None:
    item_id = "_example"
    item_dir = root / "rules" / item_id
    item_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": "1.0.0",
        "project_types": ["backend"],
        "description": "Example rule. Replace with your own rule content.",
    }
    with open(item_dir / "manifest.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(manifest, f, default_flow_style=False, sort_keys=False)
    (item_dir / "RULE.md").write_text(
        "# Example Rule\n\nReplace this file with your rule content (RULE.md).\n",
        encoding="utf-8",
    )


def _write_example_skill(root: Path) -> None:
    item_id = "_example"
    item_dir = root / "skills" / item_id
    item_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": "1.0.0",
        "project_types": ["backend"],
        "description": "Example skill. Replace with your own skill content.",
    }
    with open(item_dir / "manifest.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(manifest, f, default_flow_style=False, sort_keys=False)
    (item_dir / "SKILL.md").write_text(
        "# Example Skill\n\nReplace this file with your skill content (SKILL.md).\n",
        encoding="utf-8",
    )


def _write_example_bundle(root: Path) -> None:
    item_id = "_example"
    item_dir = root / "bundles" / item_id
    item_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": "1.0.0",
        "project_types": ["backend"],
        "description": "Example bundle that includes the example rule.",
        "items": [{"kind": "rule", "id": "_example"}],
    }
    with open(item_dir / "manifest.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(manifest, f, default_flow_style=False, sort_keys=False)
