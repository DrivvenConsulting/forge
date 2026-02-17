"""forge describe: show details for an agent, rule, skill, bundle, workflow, or prompt."""

from typing import cast

import typer
from rich.console import Console
from rich.table import Table

from forge.core.describe import describe_item
from forge.core.models import ItemKind, ProjectType
from forge.core.project import find_project_root, load_config
from forge.core.registry import fetch_registry


def describe_cmd(
    kind: str = typer.Argument(..., help="agent, rule, skill, bundle, workflow, or prompt"),
    item_id: str = typer.Argument(..., help="Item id"),
) -> None:
    """Describe an agent, rule, skill, bundle, workflow, or prompt from the registry."""
    if kind not in ("agent", "rule", "skill", "bundle", "workflow", "prompt"):
        typer.echo(
            f"Kind must be agent, rule, skill, bundle, workflow, or prompt; got {kind}.",
            err=True,
        )
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

    project_types: list[ProjectType] = list(config.project_types)

    try:
        desc = describe_item(
            registry_root,
            cast(ItemKind, kind),
            item_id,
            project_types=project_types,
        )
    except KeyError:
        typer.echo(f"Item not found: {kind}/{item_id}", err=True)
        raise typer.Exit(1)

    console = Console()

    # Header table for the main item
    header = Table(show_header=True, header_style="bold")
    header.add_column("Kind", style="dim")
    header.add_column("ID")
    header.add_column("Version", style="dim")
    header.add_column("Project types", style="dim")
    header.add_column("Description")
    header.add_column("Registry path", style="dim")

    header.add_row(
        str(desc.get("kind", "")),
        str(desc.get("id", "")),
        str(desc.get("version", "")),
        ", ".join(desc.get("project_types", []) or []),
        str(desc.get("description", "") or ""),
        str(desc.get("path", "") or ""),
    )

    console.print(header)

    # For bundles, also print a members table
    if desc.get("kind") == "bundle" and desc.get("members"):
        members_table = Table(show_header=True, header_style="bold", title="Bundle members")
        members_table.add_column("Kind", style="dim")
        members_table.add_column("ID")
        members_table.add_column("Version", style="dim")
        members_table.add_column("Project types", style="dim")
        members_table.add_column("Description")
        members_table.add_column("Registry path", style="dim")
        members_table.add_column("Status", style="dim")

        for m in desc.get("members", []):
            members_table.add_row(
                str(m.get("kind", "")),
                str(m.get("id", "")),
                str(m.get("version", "")),
                ", ".join(m.get("project_types", []) or []),
                str(m.get("description", "") or ""),
                str(m.get("path", "") or ""),
                str(m.get("status", "")),
            )

        console.print()
        console.print(members_table)

