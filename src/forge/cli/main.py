"""Typer app entrypoint for Forge CLI."""

import typer

from forge.cli.init_cmd import init_cmd
from forge.cli.install_cmd import install_cmd
from forge.cli.list_cmd import list_cmd
from forge.cli.remove_cmd import remove_cmd
from forge.cli.update_cmd import update_cmd
from forge.cli.describe_cmd import describe_cmd

app = typer.Typer(
    name="forge",
    help="Manage AI agents, rules, and skills from a centralized registry.",
)

app.command("init")(init_cmd)
app.command("list")(list_cmd)
app.command("install")(install_cmd)
app.command("remove")(remove_cmd)
app.command("update")(update_cmd)
app.command("describe")(describe_cmd)

def main() -> None:
    """Entry point for the forge console script."""
    app()


if __name__ == "__main__":
    main()
