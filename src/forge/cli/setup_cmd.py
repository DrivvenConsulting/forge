"""forge setup: developer environment setup wizard."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from forge.core.setup import (
    CLAUDE_SETTINGS_PATH,
    is_cli_installed,
    is_mcp_configured,
    run_setup_all,
    run_setup_for_tool,
)
from forge.core.setup_catalog import SETUP_TOOLS, SETUP_TOOLS_BY_ID

setup_app = typer.Typer(help="Set up developer tools and MCP servers.")
console = Console()


@setup_app.callback(invoke_without_command=True)
def setup_cmd(ctx: typer.Context) -> None:
    """Run the full setup wizard for all tools."""
    if ctx.invoked_subcommand is not None:
        return
    results = run_setup_all()
    _print_setup_results(results)


@setup_app.command("tool")
def setup_tool_cmd(
    tool_id: str = typer.Argument(..., help="Tool ID, e.g. github-mcp, aws-cli"),
) -> None:
    """Set up a single tool by ID."""
    if tool_id not in SETUP_TOOLS_BY_ID:
        known = ", ".join(SETUP_TOOLS_BY_ID.keys())
        typer.echo(f"Unknown tool: {tool_id}. Known tools: {known}", err=True)
        raise typer.Exit(1)
    result = run_setup_for_tool(SETUP_TOOLS_BY_ID[tool_id])
    _print_setup_results([result])


@setup_app.command("list")
def setup_list_cmd() -> None:
    """List all known tools and their current installation/configuration status."""
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID")
    table.add_column("Kind", style="dim")
    table.add_column("Display Name")
    table.add_column("Status")

    for t in SETUP_TOOLS:
        if t.kind == "cli":
            status = "[green]installed[/green]" if is_cli_installed(t) else "[yellow]not installed[/yellow]"
        else:
            status = (
                "[green]configured[/green]"
                if is_mcp_configured(t)
                else "[yellow]not configured[/yellow]"
            )
        table.add_row(t.id, t.kind, t.display_name, status)

    console.print(table)


def _print_setup_results(results: list[dict]) -> None:
    """Format and print setup results to the terminal."""
    for r in results:
        typer.echo(f"\n{'=' * 60}")
        typer.echo(f"  {r['display_name']}  [{r['id']}]")
        typer.echo(f"{'=' * 60}")

        if r["already_done"]:
            kind_label = "installed" if r["kind"] == "cli" else "configured"
            typer.echo(f"  Status: already {kind_label}. Nothing to do.")
            continue

        if r["status"] == "configured":
            typer.echo("  Status: MCP server entry written to ~/.claude/settings.json.")
            typer.echo("  Fill in your API credentials using the steps below.")
        elif r["status"] == "needs_action":
            typer.echo("  Status: not installed.")
            instructions = r["install_instructions"]
            if instructions:
                typer.echo("\n  Install with:")
                for cmd in instructions:
                    typer.echo(f"    $ {cmd}")
            else:
                typer.echo(
                    "\n  No automated install instructions available for this platform."
                    " See the official documentation."
                )

        if r["auth_steps"]:
            typer.echo("\n  How to configure / authenticate:")
            for step in r["auth_steps"]:
                _print_step(step)

        if r["post_install_steps"]:
            typer.echo("\n  Post-install steps:")
            for step in r["post_install_steps"]:
                _print_step(step)

        if r["env_vars_required"]:
            typer.echo(f"\n  Required environment variables: {', '.join(r['env_vars_required'])}")


def _print_step(step: object) -> None:
    typer.echo(f"    {step.step}. {step.description}")  # type: ignore[union-attr]
    if step.command:  # type: ignore[union-attr]
        typer.echo(f"       $ {step.command}")  # type: ignore[union-attr]
