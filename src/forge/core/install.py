"""Install a single item or bundle: copy files and update project config."""

import json
import shutil
from pathlib import Path

from forge.core.models import InstalledItem, ProjectConfig, RegistryItem
from forge.core.project import load_config, save_config


def dest_path(project_root: Path, kind: str, item_id: str, tool: str) -> Path:
    """Return the installation path for an item given the target tool.

    Args:
        project_root: Project root directory.
        kind: One of agent, rule, skill, workflow, prompt.
        item_id: Item identifier (may contain / for prompts).
        tool: Target tool — 'cursor' or 'claude-code'.
    """
    base = project_root / (".cursor" if tool == "cursor" else ".claude")
    if kind == "agent":
        return base / "agents" / f"{item_id}.md"
    elif kind == "rule":
        return base / "rules" / item_id / "RULE.md"
    elif kind == "skill":
        return base / "skills" / item_id / "SKILL.md"
    elif kind == "workflow":
        if tool == "claude-code":
            return base / "commands" / item_id
        return base / "workflows" / item_id
    elif kind == "prompt":
        if tool == "claude-code":
            return base / "commands" / f"{item_id}.md"
        return base / "prompts" / f"{item_id}.md"
    elif kind == "hook":
        if tool != "claude-code":
            raise ValueError("Hooks are only supported for claude-code projects")
        return base / "hooks" / f"{item_id}.sh"
    raise ValueError(f"Invalid kind: {kind}")


def _copy_agent(registry_root: Path, item: RegistryItem, project_root: Path, tool: str) -> None:
    """Copy agent content (first .md file) to the target agents directory."""
    src_dir = registry_root / item.path
    dest_file = dest_path(project_root, "agent", item.id, tool)
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    md_files = list(src_dir.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No .md file found in {src_dir}")
    shutil.copy2(md_files[0], dest_file)


def _copy_rule(registry_root: Path, item: RegistryItem, project_root: Path, tool: str) -> None:
    """Copy RULE.md to the target rules directory."""
    src_file = registry_root / item.path / "RULE.md"
    if not src_file.exists():
        raise FileNotFoundError(f"RULE.md not found in {registry_root / item.path}")
    dest_file = dest_path(project_root, "rule", item.id, tool)
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dest_file)


def _copy_skill(registry_root: Path, item: RegistryItem, project_root: Path, tool: str) -> None:
    """Copy SKILL.md to the target skills directory."""
    src_file = registry_root / item.path / "SKILL.md"
    if not src_file.exists():
        raise FileNotFoundError(f"SKILL.md not found in {registry_root / item.path}")
    dest_file = dest_path(project_root, "skill", item.id, tool)
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dest_file)


def _copy_workflow(registry_root: Path, item: RegistryItem, project_root: Path, tool: str) -> None:
    """Copy WORKFLOW.md and manifest.yaml to workflows/ (Cursor) or commands/<id>/ (Claude Code)."""
    src_dir = registry_root / item.path
    dest_dir = dest_path(project_root, "workflow", item.id, tool)
    dest_dir.mkdir(parents=True, exist_ok=True)
    workflow_md = src_dir / "WORKFLOW.md"
    manifest_yaml = src_dir / "manifest.yaml"
    if not workflow_md.exists():
        raise FileNotFoundError(f"WORKFLOW.md not found in {src_dir}")
    shutil.copy2(workflow_md, dest_dir / "WORKFLOW.md")
    if manifest_yaml.exists():
        shutil.copy2(manifest_yaml, dest_dir / "manifest.yaml")


def _install_hook(registry_root: Path, item: RegistryItem, project_root: Path, tool: str) -> None:
    """Copy hook script and merge hooks.json into project .claude/settings.json."""
    if tool != "claude-code":
        raise ValueError("Hooks are only supported for claude-code projects")
    script_src = registry_root / item.path / "scripts" / f"{item.id}.sh"
    if not script_src.exists():
        raise FileNotFoundError(f"Hook script not found: {script_src}")
    script_dest = dest_path(project_root, "hook", item.id, tool)
    script_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(script_src, script_dest)
    script_dest.chmod(script_dest.stat().st_mode | 0o111)

    hooks_json_path = registry_root / item.path / "hooks.json"
    if hooks_json_path.exists():
        from forge.core.setup import load_claude_settings, save_claude_settings

        hook_defs = json.loads(hooks_json_path.read_text(encoding="utf-8"))
        settings_path = project_root / ".claude" / "settings.json"
        settings = load_claude_settings(settings_path)
        project_hooks = settings.setdefault("hooks", {})
        for event, matchers in hook_defs.items():
            event_list = project_hooks.setdefault(event, [])
            for new_entry in matchers:
                new_cmds = {h["command"] for h in new_entry.get("hooks", [])}
                already = any(
                    new_cmds == {h["command"] for h in ex.get("hooks", [])}
                    and ex.get("matcher") == new_entry.get("matcher")
                    for ex in event_list
                )
                if not already:
                    event_list.append(new_entry)
        save_claude_settings(settings, settings_path)


def _copy_prompt(registry_root: Path, item: RegistryItem, project_root: Path, tool: str) -> None:
    """Copy prompt .md file to the target prompts/commands directory."""
    src_file = registry_root / item.path
    if not src_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {src_file}")
    dest_file = dest_path(project_root, "prompt", item.id, tool)
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dest_file)


def copy_registry_item_to_project(
    registry_root: Path, item: RegistryItem, project_root: Path, tool: str
) -> None:
    """Copy one agent/rule/skill/workflow/prompt from registry into the target tool directory. Does not update config."""
    if item.kind == "agent":
        _copy_agent(registry_root, item, project_root, tool)
    elif item.kind == "rule":
        _copy_rule(registry_root, item, project_root, tool)
    elif item.kind == "skill":
        _copy_skill(registry_root, item, project_root, tool)
    elif item.kind == "workflow":
        _copy_workflow(registry_root, item, project_root, tool)
    elif item.kind == "prompt":
        _copy_prompt(registry_root, item, project_root, tool)
    elif item.kind == "hook":
        _install_hook(registry_root, item, project_root, tool)
    else:
        raise ValueError(f"Expected agent, rule, skill, workflow, prompt, or hook; got {item.kind}")


def _install_single_item(
    registry_root: Path,
    item: RegistryItem,
    project_root: Path,
    config: ProjectConfig,
    source_ref: str,
) -> None:
    """Copy one item into the project and append to config.installed. Caller must save config."""
    copy_registry_item_to_project(registry_root, item, project_root, config.tool)
    config.installed.append(
        InstalledItem(
            kind=item.kind,
            id=item.id,
            version=item.version,
            source_registry_ref=source_ref,
        )
    )


def install_item(
    registry_root: Path,
    item: RegistryItem,
    project_root: Path,
    config: ProjectConfig,
    source_ref: str,
) -> None:
    """Install a single agent, rule, skill, workflow, or prompt. Updates config and saves.

    Args:
        registry_root: Path to cloned registry repo.
        item: Registry item (must be agent, rule, skill, workflow, or prompt).
        project_root: Project root (contains .forge/).
        config: Current project config (will be updated and saved).
        source_ref: Git ref used for this install (e.g. main).

    Raises:
        ValueError: If item is a bundle or project type incompatible.
        FileNotFoundError: If item files are missing in registry.
    """
    if item.kind == "bundle":
        raise ValueError("Use install_bundle for bundles")
    _install_single_item(registry_root, item, project_root, config, source_ref)
    save_config(project_root, config)


def install_bundle(
    registry_root: Path,
    bundle_item: RegistryItem,
    items_by_kind_id: dict[tuple[str, str], RegistryItem],
    project_root: Path,
    config: ProjectConfig,
    source_ref: str,
) -> None:
    """Install or sync a bundle: one InstalledBundle row and member files. Idempotent if bundle id exists.

    Args:
        registry_root: Path to cloned registry repo.
        bundle_item: Bundle registry item (must have .items).
        items_by_kind_id: Map (kind, id) -> RegistryItem for resolving bundle members.
        project_root: Project root.
        config: Current project config (will be updated and saved).
        source_ref: Git ref used for this install.

    Raises:
        ValueError: If a bundle member is not found or not compatible.
        FileNotFoundError: If any item files are missing.
    """
    from forge.core.bundle_sync import sync_bundle_with_registry

    sync_bundle_with_registry(
        registry_root,
        project_root,
        config,
        bundle_item,
        items_by_kind_id,
        source_ref,
    )
    save_config(project_root, config)
