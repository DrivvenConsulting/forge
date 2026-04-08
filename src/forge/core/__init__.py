"""Core business logic: registry resolution, install, update, remove, validation."""

from forge.core.install import install_bundle, install_item
from forge.core.list_items import list_items
from forge.core.project import find_project_root, load_config, save_config
from forge.core.registry import fetch_registry, get_registry_items
from forge.core.remove import remove_bundle, remove_item
from forge.core.setup import (
    configure_mcp,
    get_install_instructions,
    is_cli_installed,
    is_mcp_configured,
    load_claude_settings,
    run_setup_all,
    run_setup_for_tool,
    save_claude_settings,
)
from forge.core.update import update_all, update_bundle, update_item
from forge.core.validation import is_compatible_with_project_type, is_compatible_with_project_types

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
    "remove_bundle",
    "update_all",
    "update_item",
    "update_bundle",
    "is_compatible_with_project_type",
    "is_compatible_with_project_types",
    "configure_mcp",
    "get_install_instructions",
    "is_cli_installed",
    "is_mcp_configured",
    "load_claude_settings",
    "run_setup_all",
    "run_setup_for_tool",
    "save_claude_settings",
]
