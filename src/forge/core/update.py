"""Update installed items: re-fetch registry and re-install."""

from pathlib import Path

from forge.core.install import install_item
from forge.core.models import ProjectConfig, RegistryItem
from forge.core.project import load_config, save_config
from forge.core.registry import fetch_registry, get_registry_items
from forge.core.remove import remove_item
from forge.core.validation import is_compatible_with_project_type


def _items_by_kind_id(items: list[RegistryItem]) -> dict[tuple[str, str], RegistryItem]:
    """Build (kind, id) -> RegistryItem map for non-bundle items."""
    return {(i.kind, i.id): i for i in items if i.kind != "bundle"}


def update_item(
    project_root: Path,
    config: ProjectConfig,
    kind: str,
    item_id: str,
) -> bool:
    """Update one installed item: re-fetch registry, re-install, update config.

    Args:
        project_root: Project root.
        config: Current project config.
        kind: agent, rule, or skill.
        item_id: Id of the installed item.

    Returns:
        True if the item was installed and updated; False if not in installed list.
    """
    root = Path(project_root)
    if kind not in ("agent", "rule", "skill"):
        raise ValueError(f"Invalid kind: {kind}")
    inst = next((i for i in config.installed if i.kind == kind and i.id == item_id), None)
    if inst is None:
        return False

    registry_root = fetch_registry(config.registry.url, config.registry.ref)
    all_items = get_registry_items(registry_root)
    items_by_kind_id = _items_by_kind_id(all_items)
    key = (kind, item_id)
    if key not in items_by_kind_id:
        return False
    new_item = items_by_kind_id[key]
    if not is_compatible_with_project_type(new_item, config.project_type):
        return False

    remove_item(project_root, config, kind, item_id)
    config = load_config(project_root)
    if config is None:
        return False
    install_item(registry_root, new_item, root, config, config.registry.ref)
    return True


def update_all(project_root: Path) -> list[tuple[str, str]]:
    """Update all installed items. Re-fetch registry and re-install each.

    Args:
        project_root: Project root.

    Returns:
        List of (kind, id) that were successfully updated.

    Raises:
        RuntimeError: If config missing or registry fetch fails.
    """
    root = Path(project_root)
    config = load_config(root)
    if config is None:
        raise RuntimeError("No project config found; run forge init first")

    registry_root = fetch_registry(config.registry.url, config.registry.ref)
    all_items = get_registry_items(registry_root)
    items_by_kind_id = _items_by_kind_id(all_items)
    updated: list[tuple[str, str]] = []
    to_update = list(config.installed)

    for inst in to_update:
        key = (inst.kind, inst.id)
        if key not in items_by_kind_id:
            continue
        new_item = items_by_kind_id[key]
        if not is_compatible_with_project_type(new_item, config.project_type):
            continue
        remove_item(root, config, inst.kind, inst.id)
        config = load_config(root)
        if config is None:
            continue
        install_item(registry_root, new_item, root, config, config.registry.ref)
        updated.append((inst.kind, inst.id))
        config = load_config(root)
        if config is None:
            break

    return updated
