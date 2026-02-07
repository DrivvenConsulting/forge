"""List registry items filtered by project type and optional category."""

from pathlib import Path

from forge.core.models import ItemKind, ProjectType, RegistryItem
from forge.core.registry import fetch_registry, get_registry_items
from forge.core.validation import is_compatible_with_project_type


def list_items(
    registry_url: str,
    registry_ref: str,
    project_type: ProjectType,
    category: ItemKind | None = None,
    registry_root: Path | None = None,
) -> list[RegistryItem]:
    """List available registry items compatible with project_type, optionally filtered by kind.

    If registry_root is provided, uses it instead of fetching (for tests or pre-cloned registry).
    Otherwise fetches the registry from registry_url at registry_ref.

    Args:
        registry_url: Git URL of the registry.
        registry_ref: Branch or tag to use.
        project_type: Only return items whose project_types include this.
        category: If set, only return items of this kind (agent, rule, skill, bundle).
        registry_root: Optional path to existing registry clone; if set, url/ref are ignored.

    Returns:
        List of matching registry items.

    Raises:
        RuntimeError: If fetch fails (when registry_root is not provided).
    """
    if registry_root is not None:
        root = Path(registry_root)
    else:
        root = fetch_registry(registry_url, registry_ref)
    all_items = get_registry_items(root)
    filtered = [i for i in all_items if is_compatible_with_project_type(i, project_type)]
    if category is not None:
        filtered = [i for i in filtered if i.kind == category]
    return filtered
