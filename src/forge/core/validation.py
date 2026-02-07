"""Project type compatibility and manifest validation."""

from forge.core.models import PROJECT_TYPES, ProjectType, RegistryItem


def is_compatible_with_project_type(item: RegistryItem, project_type: ProjectType) -> bool:
    """Return True if the registry item is installable for the given project type.

    Args:
        item: Registry item (agent, rule, skill, or bundle).
        project_type: Current project type.

    Returns:
        True if project_type is in the item's project_types list.
    """
    return project_type in item.project_types


def is_valid_project_type(value: str) -> bool:
    """Return True if value is a valid project type."""
    return value in PROJECT_TYPES
