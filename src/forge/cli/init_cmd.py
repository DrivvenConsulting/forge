"""forge init: create .forge/config.yaml or scaffold a registry repo."""

from pathlib import Path

import typer

from forge.core.models import ProjectConfig, RegistryConfig
from forge.core.project import find_project_root, save_config
from forge.core.registry_init import is_registry_root, scaffold_registry


DEFAULT_REGISTRY_URL = "https://github.com/DrivvenConsulting/forge-registry.git"


def init_cmd(
    project_type: str = typer.Option(
        "backend",
        "--project-type",
        "-p",
        help="Comma-separated project types: data, backend, frontend, infra, product",
    ),
    registry_url: str = typer.Option(
        DEFAULT_REGISTRY_URL,
        "--registry-url",
        "-r",
        help="Registry Git URL",
    ),
    registry_ref: str = typer.Option("main", "--registry-ref", help="Registry branch or tag"),
    registry: bool = typer.Option(
        False,
        "--registry",
        help="Scaffold a registry repo (agents/, rules/, skills/, bundles/) instead of project config.",
    ),
    with_examples: bool = typer.Option(
        False,
        "--with-examples",
        help="Add minimal example items (only with --registry).",
    ),
) -> None:
    """Create .forge/config.yaml in the current directory, or scaffold a registry repo with --registry."""
    cwd = Path.cwd()

    if registry:
        existing_project = find_project_root(cwd)
        if existing_project is not None:
            typer.echo(
                f"Cannot initialize registry inside a Forge project ({existing_project}).",
                err=True,
            )
            raise typer.Exit(1)
        if is_registry_root(cwd):
            typer.echo("Registry layout already present in this directory.", err=True)
            raise typer.Exit(1)
        scaffold_registry(cwd, with_examples=with_examples)
        msg = "Initialized Forge registry in {}.".format(cwd)
        if with_examples:
            msg += " Example items were added in agents/, rules/, skills/, and bundles/."
        else:
            msg += " Add agents, rules, skills, and bundles in the respective directories."
        typer.echo(msg)
        return

    existing = find_project_root(cwd)
    if existing is not None:
        typer.echo(f"Forge is already initialized in {existing}.", err=True)
        raise typer.Exit(1)
    raw = [t.strip() for t in project_type.split(",") if t.strip()]
    valid = ("data", "backend", "frontend", "infra", "product")
    project_types = []
    for t in raw:
        if t not in valid:
            typer.echo(f"Invalid project type: {t}. Use data, backend, frontend, infra, or product.", err=True)
            raise typer.Exit(1)
        if t not in project_types:
            project_types.append(t)
    if not project_types:
        project_types = ["backend"]
    config = ProjectConfig(
        project_types=project_types,
        registry=RegistryConfig(url=registry_url, ref=registry_ref),
        installed=[],
    )
    save_config(cwd, config)
    typer.echo(f"Initialized Forge in {cwd} with project types {project_types}.")
