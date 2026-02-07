"""forge update: update installed items."""

from forge.core.project import find_project_root, load_config
from forge.core.update import update_all, update_item
import typer


def update_cmd(
    kind: str | None = typer.Argument(None, help="agent, rule, or skill (omit to update all)"),
    item_id: str | None = typer.Argument(None, help="Item id (required if kind is set)"),
) -> None:
    """Update all installed items, or a single item if kind and id are given."""
    if (kind is None) != (item_id is None):
        typer.echo("Provide both kind and id to update one item, or neither to update all.", err=True)
        raise typer.Exit(1)
    if kind is None and item_id is None:
        project_root = find_project_root()
        if project_root is None:
            typer.echo("Not in a Forge project. Run 'forge init' first.", err=True)
            raise typer.Exit(1)
        try:
            updated = update_all(project_root)
        except RuntimeError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)
        if not updated:
            typer.echo("Nothing to update (or no items installed).")
            return
        for k, i in updated:
            typer.echo(f"Updated {k} {i}.")
        return
    if kind not in ("agent", "rule", "skill"):
        typer.echo("Kind must be agent, rule, or skill.", err=True)
        raise typer.Exit(1)
    project_root = find_project_root()
    if project_root is None:
        typer.echo("Not in a Forge project.", err=True)
        raise typer.Exit(1)
    config = load_config(project_root)
    if config is None:
        typer.echo("No .forge/config.yaml found.", err=True)
        raise typer.Exit(1)
    try:
        ok = update_item(project_root, config, kind, item_id)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    if not ok:
        typer.echo(f"{kind} {item_id} is not installed or could not be updated.", err=True)
        raise typer.Exit(1)
    typer.echo(f"Updated {kind} {item_id}.")
