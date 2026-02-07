"""forge list: list available agents, rules, skills, and bundles."""

from typing import cast

import typer
from rich.console import Console
from rich.table import Table

from forge.core.list_items import list_items
from forge.core.models import ItemKind, ProjectType
from forge.core.project import find_project_root, load_config


def list_cmd(
    category: ItemKind | None = typer.Option(None, "--category", "-c", help="Filter by kind: agent, rule, skill, bundle"),
    project_type: str | None = typer.Option(None, "--project-type", "-p", help="Override project type (data, backend, frontend, infra)"),
    all_items: bool = typer.Option(False, "--all", "-a", help="Show all items, not only those for current project type"),
    installed: bool = typer.Option(False, "--installed", "-i", help="List installed items in this project"),
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

    if installed:
        items_to_show = list(config.installed)
        if category is not None:
            items_to_show = [i for i in items_to_show if i.kind == category]
        if not items_to_show:
            typer.echo("No installed items found.")
            return
        table = Table(show_header=True, header_style="bold")
        table.add_column("Kind", style="dim")
        table.add_column("ID")
        table.add_column("Version", style="dim")
        table.add_column("Source ref", style="dim")
        for i in items_to_show:
            table.add_row(i.kind, i.id, i.version, i.source_registry_ref)
        console = Console()
        console.print(table)
        return

    if project_type is not None:
        if project_type not in ("data", "backend", "frontend", "infra"):
            typer.echo(f"Invalid project type: {project_type}. Use data, backend, frontend, or infra.", err=True)
            raise typer.Exit(1)
        project_types = [cast(ProjectType, project_type)]
    else:
        project_types = list(config.project_types)
    try:
        items = list_items(
            config.registry.url,
            config.registry.ref,
            project_types,
            category=category,
            all_items=all_items,
        )
    except RuntimeError as e:
        typer.echo(f"Registry error: {e}", err=True)
        raise typer.Exit(1)
    if not items:
        typer.echo("No items found.")
        return
    table = Table(show_header=True, header_style="bold")
    table.add_column("Kind", style="dim")
    table.add_column("ID")
    table.add_column("Version", style="dim")
    table.add_column("Description", no_wrap=False)
    for i in items:
        table.add_row(i.kind, i.id, i.version, i.description or "")
    console = Console()
    console.print(table)
