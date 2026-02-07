"""forge init: create .forge/config.yaml."""

from forge.core.models import ProjectConfig, RegistryConfig
from forge.core.project import find_project_root, save_config
from pathlib import Path
import typer


DEFAULT_REGISTRY_URL = "https://github.com/DrivvenConsulting/forge-registry.git"


def init_cmd(
    project_type: str = typer.Option("backend", "--project-type", "-p", help="Comma-separated project types: data, backend, frontend, infra"),
    registry_url: str = typer.Option(DEFAULT_REGISTRY_URL, "--registry-url", "-r", help="Registry Git URL"),
    registry_ref: str = typer.Option("main", "--registry-ref", help="Registry branch or tag"),
) -> None:
    """Create .forge/config.yaml in the current directory."""
    cwd = Path.cwd()
    existing = find_project_root(cwd)
    if existing is not None:
        typer.echo(f"Forge is already initialized in {existing}.", err=True)
        raise typer.Exit(1)
    raw = [t.strip() for t in project_type.split(",") if t.strip()]
    valid = ("data", "backend", "frontend", "infra")
    project_types = []
    for t in raw:
        if t not in valid:
            typer.echo(f"Invalid project type: {t}. Use data, backend, frontend, or infra.", err=True)
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
