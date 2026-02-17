# Forge

CLI for managing AI agents, rules, and skills from a centralized, versioned registry.

## Install

Using [uv](https://docs.astral.sh/uv/) (recommended):

```bash
# Install forge globally (available as `forge`)
uv tool install forge-cli --from git+https://github.com/<org>/forge.git](https://github.com/DrivvenConsulting/forge.git
```

Or add it as a dependency in your project and run via `uv run`:

```bash
# From your project root (with a pyproject.toml)
uv add --git https://github.com/<org>/forge.git forge-cli
uv run forge init --project-type backend
```

No PyPI release for MVP.

## Quick start

If you added Forge as a project dependency with `uv add`, run every command as `uv run forge ...` instead of `forge`.

1. In your project directory, initialize Forge with one or more project types:

   ```bash
   forge init --project-type backend
   forge init --project-type data,infra
   ```

   This creates `.forge/config.yaml` with `project_types` and default registry URL.

2. List available items (filtered by your project types) or list installed items:

   ```bash
   forge list
   forge list --category rule
   forge list --installed
   ```

3. Install an agent, rule, skill, or bundle:

   ```bash
   forge install rule framework-fastapi
   forge install bundle backend-essentials
   ```

4. Update or remove:

   ```bash
   forge update
   forge update agent backend-engineer
   forge remove rule framework-fastapi
   ```

## Project config (`.forge/config.yaml`)

- **project_types**: List of one or more of `data`, `backend`, `frontend`, `infra`. Registry items whose `project_types` include any of these can be listed or installed. Use multiple types for mixed projects (e.g. `[data, infra]` for data + devops).
- **registry**: `url` (Git clone URL) and optional `ref` (branch or tag, default `main`).
- **installed**: List of installed items with `kind`, `id`, `version`, and `source_registry_ref` (filled by Forge).

Configs with the legacy key `project_type` (singular) are still supported and treated as a single-type project.

Example:

```yaml
project_types:
  - backend
registry:
  url: https://github.com/DrivvenConsulting/forge-registry.git
  ref: main
installed:
  - kind: rule
    id: framework-fastapi
    version: "1.0.0"
    source_registry_ref: main
```

## Install destinations

- **Agents** → `.cursor/agents/<id>.md`
- **Rules** → `.cursor/rules/<id>/RULE.md`
- **Skills** → `.cursor/skills/<id>/SKILL.md`

Bundles expand to multiple installs; each member is installed as above and recorded in `installed`.

## Registry format

The registry is a Git repository with this layout:

```
agents/
  <id>/
    manifest.yaml    # version, project_types, description
    agent.md         # (or other .md)
rules/
  <id>/
    manifest.yaml
    RULE.md
skills/
  <id>/
    manifest.yaml
    SKILL.md
bundles/
  <id>/
    manifest.yaml    # version, project_types, items: [{ kind, id }]
```

**Item manifest** (`manifest.yaml` for agents, rules, skills):

- `version`: string (e.g. `1.0.0`)
- `project_types`: list of strings (`data`, `backend`, `frontend`, `infra`)
- `description`: optional string

**Bundle manifest** adds:

- `items`: list of `{ kind: "agent"|"rule"|"skill", id: "<id>" }`

Registry is versioned via Git tags or branches; Forge uses the `ref` from project config to clone or update.

## Creating a registry

To scaffold a new registry repo (e.g. for your team or org), run in an empty directory:

```bash
forge init --registry
```

This creates `agents/`, `rules/`, `skills/`, and `bundles/` with a `.gitkeep` in each. Add items as subdirectories with a `manifest.yaml` and the correct content file (`agent.md`, `RULE.md`, or `SKILL.md`; bundles need only `manifest.yaml`).

To also add minimal example items that show the expected manifest schema and file names:

```bash
forge init --registry --with-examples
```

Do not run `forge init --registry` inside a directory that already has a Forge project (`.forge/config.yaml`) or an existing registry layout (any of the four category directories).

## Creator skills (base skills in the registry)

The **forge-registry** repo includes three **base skills** that guide creation of new agents, rules, and skills in the correct Forge format. They are available for all project types (`data`, `backend`, `frontend`, `infra`). Install them like any other skill:

```bash
forge install skill create-forge-agent
forge install skill create-forge-rule
forge install skill create-forge-skill
```

| Skill | Purpose |
|-------|---------|
| **create-forge-agent** | Create a new agent (`agents/<id>/manifest.yaml` + `agent.md`) |
| **create-forge-rule** | Create a new rule (`rules/<id>/manifest.yaml` + `RULE.md`) |
| **create-forge-skill** | Create a new skill (`skills/<id>/manifest.yaml` + `SKILL.md`) |

After install, they live in `.cursor/skills/<id>/SKILL.md`. In Cursor, ask in natural language (e.g. “Create a new Forge rule for FastAPI backend standards” or “Scaffold a Forge skill for code review”); the agent will use the matching skill and produce the correct registry layout.

## Commands

| Command | Description |
|--------|-------------|
| `forge init [--project-type TYPES] [--registry-url URL] [--registry-ref REF]` | Create `.forge/config.yaml` (TYPES can be comma-separated, e.g. `data,infra`) |
| `forge init --registry [--with-examples]` | Scaffold a registry repo (agents/, rules/, skills/, bundles/); optional example items |
| `forge list [--installed] [--category agent\|rule\|skill\|bundle] [--project-type TYPE]` | List available registry items or installed items (`--installed`) |
| `forge install <kind> <id>` | Install one item or a bundle (`kind` can be `bundle`) |
| `forge remove <kind> <id>` | Remove an installed agent, rule, or skill |
| `forge update` | Update all installed items |
| `forge update <kind> <id>` | Update one installed item |

## Core API (reusable)

Business logic lives in the `forge.core` package and can be used without the CLI:

```python
from pathlib import Path
from forge.core import (
    find_project_root,
    load_config,
    fetch_registry,
    get_registry_items,
    list_items,
    install_item,
    remove_item,
    update_all,
)

project_root = find_project_root()
config = load_config(project_root)
registry_root = fetch_registry(config.registry.url, config.registry.ref)
items = list_items(config.registry.url, config.registry.ref, config.project_types)
# ... install_item, remove_item, update_all, etc.
```

## Development and tests

With uv, from the forge repo root:

```bash
uv sync --all-extras
uv run pytest tests -v
```

## License

MIT
