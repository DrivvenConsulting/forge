"""Remove an installed item: delete files and update project config."""

import shutil
from pathlib import Path

from forge.core.install import (
    _agent_dest_path,
    _prompt_dest_path,
    _rule_dest_path,
    _skill_dest_path,
    _workflow_dest_path,
)
from forge.core.models import InstalledItem, ProjectConfig
from forge.core.project import save_config


def remove_member_files(project_root: Path, kind: str, item_id: str) -> None:
    """Delete installed files for an asset under .cursor/ only (does not change config)."""
    root = Path(project_root)
    if kind == "agent":
        dest = _agent_dest_path(root, item_id)
    elif kind == "rule":
        dest = _rule_dest_path(root, item_id)
    elif kind == "skill":
        dest = _skill_dest_path(root, item_id)
    elif kind == "workflow":
        dest = _workflow_dest_path(root, item_id)
    elif kind == "prompt":
        dest = _prompt_dest_path(root, item_id)
    else:
        raise ValueError(f"Invalid kind: {kind}")

    if dest.exists():
        if dest.is_file():
            dest.unlink()
        else:
            shutil.rmtree(dest, ignore_errors=True)
    if kind in ("rule", "skill"):
        parent = dest.parent
        if parent.exists() and parent.is_dir():
            shutil.rmtree(parent, ignore_errors=True)
    if kind == "prompt" and dest.parent.exists() and dest.parent.is_dir():
        try:
            if not any(dest.parent.iterdir()):
                dest.parent.rmdir()
        except OSError:
            pass


def remove_item(
    project_root: Path,
    config: ProjectConfig,
    kind: str,
    item_id: str,
) -> bool:
    """Remove an installed item by kind and id. Delete its files and update config.

    Args:
        project_root: Project root (contains .forge/ and .cursor/).
        config: Current project config (will be updated and saved).
        kind: One of agent, rule, skill, workflow, prompt.
        item_id: Id of the installed item.

    Returns:
        True if the item was found and removed; False if not in installed list.
    """
    root = Path(project_root)
    if kind == "agent":
        dest = _agent_dest_path(root, item_id)
    elif kind == "rule":
        dest = _rule_dest_path(root, item_id)
    elif kind == "skill":
        dest = _skill_dest_path(root, item_id)
    elif kind == "workflow":
        dest = _workflow_dest_path(root, item_id)
    elif kind == "prompt":
        dest = _prompt_dest_path(root, item_id)
    else:
        raise ValueError(f"Invalid kind: {kind}")

    found = None
    for i, inst in enumerate(config.installed):
        if inst.kind == kind and inst.id == item_id:
            found = i
            break
    if found is None:
        return False

    remove_member_files(root, kind, item_id)

    config.installed.pop(found)
    save_config(project_root, config)
    return True


def remove_bundle(project_root: Path, config: ProjectConfig, bundle_id: str) -> bool:
    """Remove an installed bundle: delete member files when refcount drops to zero; remove bundle row."""
    from forge.core.bundle_sync import member_refcount

    root = Path(project_root)
    idx: int | None = None
    for i, b in enumerate(config.installed_bundles):
        if b.id == bundle_id:
            idx = i
            break
    if idx is None:
        return False

    bundle = config.installed_bundles[idx]
    for ref in bundle.members:
        if member_refcount(config, ref.kind, ref.id, exclude_bundle_id=bundle_id) == 0:
            remove_member_files(root, ref.kind, ref.id)

    config.installed_bundles.pop(idx)
    save_config(project_root, config)
    return True
