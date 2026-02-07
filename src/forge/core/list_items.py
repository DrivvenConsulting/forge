"""List registry items filtered by project type and optional category."""

from pathlib import Path

from forge.core.models import ItemKind, ProjectType, RegistryItem
from forge.core.registry import fetch_registry, get_registry_items
from forge.core.validation import is_compatible_with_project_types


def list_items(
    registry_url: str,
    registry_ref: str,
    project_types: list[ProjectType],
    category: ItemKind | None = None,
    registry_root: Path | None = None,
    all_items: bool = False,
) -> list[RegistryItem]:
    """List available registry items compatible with any project_type, optionally filtered by kind.

    If registry_root is provided, uses it instead of fetching (for tests or pre-cloned registry).
    Otherwise fetches the registry from registry_url at registry_ref.

    Args:
        registry_url: Git URL of the registry.
        registry_ref: Branch or tag to use.
        project_types: Only return items whose project_types include any of these (ignored if all_items is True).
        category: If set, only return items of this kind (agent, rule, skill, bundle).
        registry_root: Optional path to existing registry clone; if set, url/ref are ignored.
        all_items: If True, return all items without project-type filtering.

    Returns:
        List of matching registry items.

    Raises:
        RuntimeError: If fetch fails (when registry_root is not provided).
    """
    if registry_root is not None:
        root = Path(registry_root)
    else:
        root = fetch_registry(registry_url, registry_ref)
    items = get_registry_items(root)
    if not all_items:
        items = [i for i in items if is_compatible_with_project_types(i, project_types)]
    if category is not None:
        items = [i for i in items if i.kind == category]
    return items
