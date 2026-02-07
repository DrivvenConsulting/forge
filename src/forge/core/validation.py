"""Project type compatibility and manifest validation."""

from forge.core.models import PROJECT_TYPES, ProjectType, RegistryItem


def is_compatible_with_project_types(item: RegistryItem, project_types: list[ProjectType]) -> bool:
    """Return True if the registry item is installable for any of the given project types.

    Args:
        item: Registry item (agent, rule, skill, or bundle).
        project_types: Project types (e.g. from config).

    Returns:
        True if any project_type is in the item's project_types list.
    """
    return any(pt in item.project_types for pt in project_types)


def is_compatible_with_project_type(item: RegistryItem, project_type: ProjectType) -> bool:
    """Return True if the registry item is installable for the given project type.

    Args:
        item: Registry item (agent, rule, skill, or bundle).
        project_type: Current project type.

    Returns:
        True if project_type is in the item's project_types list.
    """
    return is_compatible_with_project_types(item, [project_type])


def is_valid_project_type(value: str) -> bool:
    """Return True if value is a valid project type."""
    return value in PROJECT_TYPES
