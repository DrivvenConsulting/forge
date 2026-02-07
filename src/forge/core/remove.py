"""Remove an installed item: delete files and update project config."""

import shutil
from pathlib import Path

from forge.core.install import _agent_dest_path, _rule_dest_path, _skill_dest_path
from forge.core.models import InstalledItem, ProjectConfig
from forge.core.project import save_config


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
        kind: One of agent, rule, skill.
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
    else:
        raise ValueError(f"Invalid kind: {kind}")

    found = None
    for i, inst in enumerate(config.installed):
        if inst.kind == kind and inst.id == item_id:
            found = i
            break
    if found is None:
        return False

    if dest.exists():
        if dest.is_file():
            dest.unlink()
        else:
            shutil.rmtree(dest, ignore_errors=True)
    if kind in ("rule", "skill"):
        parent = dest.parent
        if parent.exists() and parent.is_dir():
            shutil.rmtree(parent, ignore_errors=True)

    config.installed.pop(found)
    save_config(project_root, config)
    return True
