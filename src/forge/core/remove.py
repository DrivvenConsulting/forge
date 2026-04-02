"""Remove an installed item: delete files and update project config."""

import shutil
from pathlib import Path

from forge.core.install import dest_path
from forge.core.models import InstalledItem, ProjectConfig
from forge.core.project import save_config


def remove_member_files(project_root: Path, kind: str, item_id: str, tool: str) -> None:
    """Delete installed files for an asset only (does not change config)."""
    root = Path(project_root)
    dst = dest_path(root, kind, item_id, tool)

    if dst.exists():
        if dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst, ignore_errors=True)
    if kind in ("rule", "skill"):
        parent = dst.parent
        if parent.exists() and parent.is_dir():
            shutil.rmtree(parent, ignore_errors=True)
    if kind == "prompt" and dst.parent.exists() and dst.parent.is_dir():
        try:
            if not any(dst.parent.iterdir()):
                dst.parent.rmdir()
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
        project_root: Project root (contains .forge/ and the target tool directory).
        config: Current project config (will be updated and saved).
        kind: One of agent, rule, skill, workflow, prompt.
        item_id: Id of the installed item.

    Returns:
        True if the item was found and removed; False if not in installed list.
    """
    root = Path(project_root)

    found = None
    for i, inst in enumerate(config.installed):
        if inst.kind == kind and inst.id == item_id:
            found = i
            break
    if found is None:
        return False

    remove_member_files(root, kind, item_id, config.tool)

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
            remove_member_files(root, ref.kind, ref.id, config.tool)

    config.installed_bundles.pop(idx)
    save_config(project_root, config)
    return True
