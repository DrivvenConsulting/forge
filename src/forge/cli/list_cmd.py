"""forge list: list available agents, rules, skills, and bundles."""

from typing import cast

import typer

from forge.core.list_items import list_items
from forge.core.models import ItemKind, ProjectType
from forge.core.project import find_project_root, load_config


def list_cmd(
    category: ItemKind | None = typer.Option(None, "--category", "-c", help="Filter by kind: agent, rule, skill, bundle"),
    project_type: str | None = typer.Option(None, "--project-type", "-p", help="Override project type (data, backend, frontend, infra)"),
) -> None:
    """List available agents, rules, skills, and bundles from the registry."""
    project_root = find_project_root()
    if project_root is None:
        typer.echo("Not in a Forge project. Run 'forge init' first.", err=True)
        raise typer.Exit(1)
    config = load_config(project_root)
    if config is None:
        typer.echo("No .forge/config.yaml found. Run 'forge init' first.", err=True)
        raise typer.Exit(1)
    pt = project_type if project_type is not None else config.project_type
    if pt not in ("data", "backend", "frontend", "infra"):
        typer.echo(f"Invalid project type: {pt}. Use data, backend, frontend, or infra.", err=True)
        raise typer.Exit(1)
    try:
        items = list_items(
            config.registry.url,
            config.registry.ref,
            cast(ProjectType, pt),
            category=category,
        )
    except RuntimeError as e:
        typer.echo(f"Registry error: {e}", err=True)
        raise typer.Exit(1)
    if not items:
        typer.echo("No items found.")
        return
    for i in items:
        desc = f"  {i.description}" if i.description else ""
        typer.echo(f"{i.kind}\t{i.id}\t{i.version}{desc}")
