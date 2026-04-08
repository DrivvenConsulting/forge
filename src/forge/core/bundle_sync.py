"""Sync installed bundles with registry: install, reconcile members, refcount-aware removal."""

from pathlib import Path

from forge.core.install import copy_registry_item_to_project
from forge.core.models import BundleItemRef, InstalledBundle, ProjectConfig, RegistryItem
from forge.core.remove import remove_member_files
from forge.core.validation import is_compatible_with_project_types


def member_refcount(
    config: ProjectConfig,
    kind: str,
    item_id: str,
    *,
    exclude_bundle_id: str | None = None,
) -> int:
    """Count sources that reference an asset: standalone installs + bundles listing (kind, id)."""
    n = 0
    if any(i.kind == kind and i.id == item_id for i in config.installed):
        n += 1
    for b in config.installed_bundles:
        if exclude_bundle_id is not None and b.id == exclude_bundle_id:
            continue
        if any(r.kind == kind and r.id == item_id for r in b.members):
            n += 1
    return n


def _validate_bundle_members(
    bundle_item: RegistryItem,
    items_by_kind_id: dict[tuple[str, str], RegistryItem],
    project_types: list[str],
) -> None:
    if not bundle_item.items:
        raise ValueError("Bundle has no items")
    for ref in bundle_item.items:
        key = (ref.kind, ref.id)
        if key not in items_by_kind_id:
            raise ValueError(f"Bundle references unknown item: {ref.kind}/{ref.id}")
        member = items_by_kind_id[key]
        if not is_compatible_with_project_types(member, project_types):
            raise ValueError(
                f"Bundle member {ref.kind}/{ref.id} is not compatible with project types {project_types}."
            )


def sync_bundle_with_registry(
    registry_root: Path,
    project_root: Path,
    config: ProjectConfig,
    bundle_item: RegistryItem,
    items_by_kind_id: dict[tuple[str, str], RegistryItem],
    source_ref: str,
) -> None:
    """Install or reconcile one bundle: update files and exactly one InstalledBundle row. Does not save config."""
    if bundle_item.kind != "bundle" or not bundle_item.items:
        raise ValueError("Not a bundle or bundle has no items")
    _validate_bundle_members(bundle_item, items_by_kind_id, config.project_types)

    new_refs = list(bundle_item.items)
    new_keys = {(r.kind, r.id) for r in new_refs}
    bundle_id = bundle_item.id

    idx: int | None = None
    for i, b in enumerate(config.installed_bundles):
        if b.id == bundle_id:
            idx = i
            break

    if idx is not None:
        old_bundle = config.installed_bundles[idx]
        old_keys = {(r.kind, r.id) for r in old_bundle.members}
        for kind, mid in old_keys - new_keys:
            if member_refcount(config, kind, mid, exclude_bundle_id=bundle_id) == 0:
                remove_member_files(project_root, kind, mid, config.tool)
        for kind, mid in new_keys:
            member = items_by_kind_id[(kind, mid)]
            copy_registry_item_to_project(registry_root, member, project_root, config.tool)
        config.installed_bundles[idx] = InstalledBundle(
            id=bundle_id,
            version=bundle_item.version,
            source_registry_ref=source_ref,
            members=list(new_refs),
        )
    else:
        for ref in new_refs:
            member = items_by_kind_id[(ref.kind, ref.id)]
            copy_registry_item_to_project(registry_root, member, project_root, config.tool)
        config.installed_bundles.append(
            InstalledBundle(
                id=bundle_id,
                version=bundle_item.version,
                source_registry_ref=source_ref,
                members=list(new_refs),
            )
        )
