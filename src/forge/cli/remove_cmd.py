"""forge remove: remove an installed agent, rule, or skill."""

from forge.core.project import find_project_root, load_config
from forge.core.remove import remove_item
import typer


def remove_cmd(
    kind: str = typer.Argument(..., help="agent, rule, skill, workflow, or prompt"),
    item_id: str = typer.Argument(..., help="Item id"),
) -> None:
    """Remove an installed agent, rule, skill, workflow, or prompt."""
    if kind not in ("agent", "rule", "skill", "workflow", "prompt"):
        typer.echo("Kind must be agent, rule, skill, workflow, or prompt.", err=True)
        raise typer.Exit(1)
    project_root = find_project_root()
    if project_root is None:
        typer.echo("Not in a Forge project.", err=True)
        raise typer.Exit(1)
    config = load_config(project_root)
    if config is None:
        typer.echo("No .forge/config.yaml found.", err=True)
        raise typer.Exit(1)
    ok = remove_item(project_root, config, kind, item_id)
    if not ok:
        typer.echo(f"{kind} {item_id} is not installed.", err=True)
        raise typer.Exit(1)
    typer.echo(f"Removed {kind} {item_id}.")
