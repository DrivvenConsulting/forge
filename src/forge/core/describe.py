"""Core helpers for describing registry items."""

from pathlib import Path
from typing import Any

from forge.core.models import ItemKind, ProjectType, RegistryItem
from forge.core.registry import get_registry_items


def _items_by_kind_id(items: list[RegistryItem]) -> dict[tuple[ItemKind, str], RegistryItem]:
    """Build (kind, id) -> RegistryItem map for all items."""
    return {(i.kind, i.id): i for i in items}


def describe_item(
    registry_root: Path,
    kind: ItemKind,
    item_id: str,
    project_types: list[ProjectType] | None = None,
) -> dict[str, Any]:
    """Return a structured description of a registry item.

    The description is backend-agnostic and suitable for CLI or other frontends.
    For bundles, includes a ``members`` list with resolved items where possible.
    """
    all_items = get_registry_items(registry_root)
    items_map = _items_by_kind_id(all_items)
    key = (kind, item_id)
    if key not in items_map:
        raise KeyError(f"Item not found: {kind}/{item_id}")
    item = items_map[key]

    base: dict[str, Any] = {
        "kind": item.kind,
        "id": item.id,
        "version": item.version,
        "project_types": list(item.project_types),
        "description": item.description,
        "path": item.path,
    }

    if item.kind != "bundle" or not item.items:
        return base

    members: list[dict[str, Any]] = []
    for ref in item.items:
        ref_key = (ref.kind, ref.id)
        member = items_map.get(ref_key)
        if member is None:
            members.append(
                {
                    "kind": ref.kind,
                    "id": ref.id,
                    "status": "missing",
                }
            )
            continue

        status = "ok"
        if project_types is not None:
            if not any(pt in member.project_types for pt in project_types):
                status = "incompatible"

        members.append(
            {
                "kind": member.kind,
                "id": member.id,
                "version": member.version,
                "project_types": list(member.project_types),
                "description": member.description,
                "path": member.path,
                "status": status,
            }
        )

    base["members"] = members
    return base

