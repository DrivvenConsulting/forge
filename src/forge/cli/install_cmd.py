"""forge install: install an agent, rule, skill, or bundle."""

from forge.core.install import install_bundle, install_item
from forge.core.project import find_project_root, load_config
from forge.core.registry import fetch_registry, get_registry_items
from forge.core.validation import is_compatible_with_project_types
import typer


def install_cmd(
    kind: str = typer.Argument(..., help="agent, rule, skill, or bundle"),
    item_id: str = typer.Argument(..., help="Item id"),
) -> None:
    """Install an agent, rule, skill, or bundle from the registry."""
    if kind not in ("agent", "rule", "skill", "bundle"):
        typer.echo(f"Kind must be agent, rule, skill, or bundle; got {kind}.", err=True)
        raise typer.Exit(1)
    project_root = find_project_root()
    if project_root is None:
        typer.echo("Not in a Forge project. Run 'forge init' first.", err=True)
        raise typer.Exit(1)
    config = load_config(project_root)
    if config is None:
        typer.echo("No .forge/config.yaml found. Run 'forge init' first.", err=True)
        raise typer.Exit(1)
    try:
        registry_root = fetch_registry(config.registry.url, config.registry.ref)
    except RuntimeError as e:
        typer.echo(f"Registry error: {e}", err=True)
        raise typer.Exit(1)
    all_items = get_registry_items(registry_root)
    by_kind_id = {(i.kind, i.id): i for i in all_items}
    if kind == "bundle":
        key = ("bundle", item_id)
        if key not in by_kind_id:
            typer.echo(f"Bundle not found: {item_id}", err=True)
            raise typer.Exit(1)
        bundle_item = by_kind_id[key]
        if not is_compatible_with_project_types(bundle_item, config.project_types):
            typer.echo(f"Bundle {item_id} is not compatible with project types {config.project_types}.", err=True)
            raise typer.Exit(1)
        install_bundle(
            registry_root,
            bundle_item,
            by_kind_id,
            project_root,
            config,
            config.registry.ref,
        )
        typer.echo(f"Installed bundle {item_id}.")
    else:
        key = (kind, item_id)
        if key not in by_kind_id:
            typer.echo(f"Item not found: {kind}/{item_id}", err=True)
            raise typer.Exit(1)
        item = by_kind_id[key]
        if not is_compatible_with_project_types(item, config.project_types):
            typer.echo(f"{kind}/{item_id} is not compatible with project types {config.project_types}.", err=True)
            raise typer.Exit(1)
        install_item(registry_root, item, project_root, config, config.registry.ref)
        typer.echo(f"Installed {kind} {item_id}.")
