"""Install a single item or bundle: copy files and update project config."""

import shutil
from pathlib import Path

from forge.core.models import InstalledItem, ProjectConfig, RegistryItem
from forge.core.project import load_config, save_config
from forge.core.validation import is_compatible_with_project_type


def _agent_dest_path(project_root: Path, item_id: str) -> Path:
    """Path for installed agent: .cursor/agents/<id>.md"""
    return project_root / ".cursor" / "agents" / f"{item_id}.md"


def _rule_dest_path(project_root: Path, item_id: str) -> Path:
    """Path for installed rule: .cursor/rules/<id>/RULE.md"""
    return project_root / ".cursor" / "rules" / item_id / "RULE.md"


def _skill_dest_path(project_root: Path, item_id: str) -> Path:
    """Path for installed skill: .cursor/skills/<id>/SKILL.md"""
    return project_root / ".cursor" / "skills" / item_id / "SKILL.md"


def _copy_agent(registry_root: Path, item: RegistryItem, project_root: Path) -> None:
    """Copy agent content (first .md file) to .cursor/agents/<id>.md."""
    src_dir = registry_root / item.path
    dest_file = _agent_dest_path(project_root, item.id)
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    md_files = list(src_dir.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No .md file found in {src_dir}")
    shutil.copy2(md_files[0], dest_file)


def _copy_rule(registry_root: Path, item: RegistryItem, project_root: Path) -> None:
    """Copy RULE.md to .cursor/rules/<id>/RULE.md."""
    src_file = registry_root / item.path / "RULE.md"
    if not src_file.exists():
        raise FileNotFoundError(f"RULE.md not found in {registry_root / item.path}")
    dest_file = _rule_dest_path(project_root, item.id)
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dest_file)


def _copy_skill(registry_root: Path, item: RegistryItem, project_root: Path) -> None:
    """Copy SKILL.md to .cursor/skills/<id>/SKILL.md."""
    src_file = registry_root / item.path / "SKILL.md"
    if not src_file.exists():
        raise FileNotFoundError(f"SKILL.md not found in {registry_root / item.path}")
    dest_file = _skill_dest_path(project_root, item.id)
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dest_file)


def _install_single_item(
    registry_root: Path,
    item: RegistryItem,
    project_root: Path,
    config: ProjectConfig,
    source_ref: str,
) -> None:
    """Copy one agent/rule/skill and append to config.installed. Caller must save config."""
    if item.kind == "agent":
        _copy_agent(registry_root, item, project_root)
    elif item.kind == "rule":
        _copy_rule(registry_root, item, project_root)
    elif item.kind == "skill":
        _copy_skill(registry_root, item, project_root)
    else:
        raise ValueError(f"Expected agent, rule, or skill; got {item.kind}")
    config.installed.append(
        InstalledItem(
            kind=item.kind,
            id=item.id,
            version=item.version,
            source_registry_ref=source_ref,
        )
    )


def install_item(
    registry_root: Path,
    item: RegistryItem,
    project_root: Path,
    config: ProjectConfig,
    source_ref: str,
) -> None:
    """Install a single agent, rule, or skill. Updates config and saves.

    Args:
        registry_root: Path to cloned registry repo.
        item: Registry item (must be agent, rule, or skill).
        project_root: Project root (contains .forge/).
        config: Current project config (will be updated and saved).
        source_ref: Git ref used for this install (e.g. main).

    Raises:
        ValueError: If item is a bundle or project type incompatible.
        FileNotFoundError: If item files are missing in registry.
    """
    if item.kind == "bundle":
        raise ValueError("Use install_bundle for bundles")
    _install_single_item(registry_root, item, project_root, config, source_ref)
    save_config(project_root, config)


def install_bundle(
    registry_root: Path,
    bundle_item: RegistryItem,
    items_by_kind_id: dict[tuple[str, str], RegistryItem],
    project_root: Path,
    config: ProjectConfig,
    source_ref: str,
) -> None:
    """Install a bundle: resolve each member and install them. Updates config and saves.

    Args:
        registry_root: Path to cloned registry repo.
        bundle_item: Bundle registry item (must have .items).
        items_by_kind_id: Map (kind, id) -> RegistryItem for resolving bundle members.
        project_root: Project root.
        config: Current project config (will be updated and saved).
        source_ref: Git ref used for this install.

    Raises:
        ValueError: If a bundle member is not found or not compatible.
        FileNotFoundError: If any item files are missing.
    """
    if bundle_item.kind != "bundle" or not bundle_item.items:
        raise ValueError("Not a bundle or bundle has no items")
    for ref in bundle_item.items:
        key = (ref.kind, ref.id)
        if key not in items_by_kind_id:
            raise ValueError(f"Bundle references unknown item: {ref.kind}/{ref.id}")
        member = items_by_kind_id[key]
        _install_single_item(registry_root, member, project_root, config, source_ref)
    save_config(project_root, config)
