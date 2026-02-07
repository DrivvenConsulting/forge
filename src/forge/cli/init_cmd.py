"""forge init: create .forge/config.yaml."""

from forge.core.models import ProjectConfig, RegistryConfig
from forge.core.project import find_project_root, save_config
from pathlib import Path
import typer


DEFAULT_REGISTRY_URL = "https://github.com/DrivvenConsulting/forge-registry.git"


def init_cmd(
    project_type: str = typer.Option("backend", "--project-type", "-p", help="Project type: data, backend, frontend, infra"),
    registry_url: str = typer.Option(DEFAULT_REGISTRY_URL, "--registry-url", "-r", help="Registry Git URL"),
    registry_ref: str = typer.Option("main", "--registry-ref", help="Registry branch or tag"),
) -> None:
    """Create .forge/config.yaml in the current directory."""
    cwd = Path.cwd()
    existing = find_project_root(cwd)
    if existing is not None:
        typer.echo(f"Forge is already initialized in {existing}.", err=True)
        raise typer.Exit(1)
    if project_type not in ("data", "backend", "frontend", "infra"):
        typer.echo("Project type must be data, backend, frontend, or infra.", err=True)
        raise typer.Exit(1)
    config = ProjectConfig(
        project_type=project_type,
        registry=RegistryConfig(url=registry_url, ref=registry_ref),
        installed=[],
    )
    save_config(cwd, config)
    typer.echo(f"Initialized Forge in {cwd} with project type {project_type}.")
