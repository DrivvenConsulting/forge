"""Core business logic: registry resolution, install, update, remove, validation."""

from forge.core.install import install_bundle, install_item
from forge.core.list_items import list_items
from forge.core.project import find_project_root, load_config, save_config
from forge.core.registry import fetch_registry, get_registry_items
from forge.core.remove import remove_item
from forge.core.update import update_all, update_item
from forge.core.validation import is_compatible_with_project_type

__all__ = [
    "install_item",
    "install_bundle",
    "list_items",
    "load_config",
    "save_config",
    "find_project_root",
    "fetch_registry",
    "get_registry_items",
    "remove_item",
    "update_all",
    "update_item",
    "is_compatible_with_project_type",
]
