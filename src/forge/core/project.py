"""Load and save .forge/config.yaml; find project root."""

import os
from pathlib import Path

import yaml

from forge.core.models import BundleItemRef, InstalledBundle, InstalledItem, ProjectConfig, RegistryConfig


def find_project_root(start: Path | None = None) -> Path | None:
    """Walk up from start (or cwd) until .forge/config.yaml is found; return that directory.

    Args:
        start: Directory to start from. Defaults to current working directory.

    Returns:
        Path to project root, or None if not found.
    """
    current = Path(start or os.getcwd()).resolve()
    if not current.is_dir():
        current = current.parent
    while True:
        config_path = current / ".forge" / "config.yaml"
        if config_path.exists():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def _coerce_project_config(data: dict) -> ProjectConfig:
    """Build ProjectConfig from raw dict (e.g. from YAML)."""
    registry_data = data.get("registry") or {}
    registry = RegistryConfig(
        url=registry_data.get("url", ""),
        ref=registry_data.get("ref", "main"),
    )
    _standalone_kinds = ("agent", "rule", "skill", "workflow", "prompt")
    installed = [
        InstalledItem(
            kind=item["kind"],
            id=item["id"],
            version=item["version"],
            source_registry_ref=item["source_registry_ref"],
        )
        for item in data.get("installed", [])
        if isinstance(item, dict)
        and item.get("kind") in _standalone_kinds
        and item.get("id")
        and item.get("version")
        and item.get("source_registry_ref")
    ]
    installed_bundles: list[InstalledBundle] = []
    for b in data.get("installed_bundles", []):
        if not isinstance(b, dict) or not b.get("id") or not b.get("version") or not b.get("source_registry_ref"):
            continue
        raw_members = b.get("members") or []
        members: list[BundleItemRef] = []
        for m in raw_members:
            if (
                isinstance(m, dict)
                and m.get("kind") in _standalone_kinds
                and m.get("id")
            ):
                members.append(BundleItemRef(kind=m["kind"], id=m["id"]))
        if members:
            installed_bundles.append(
                InstalledBundle(
                    id=b["id"],
                    version=b["version"],
                    source_registry_ref=b["source_registry_ref"],
                    members=members,
                )
            )
    raw_types = data.get("project_types")
    if isinstance(raw_types, list) and len(raw_types) > 0:
        project_types = [str(t).strip() for t in raw_types if t]
    else:
        project_types = [str(data.get("project_type", "backend"))]
    project_types = [t for t in project_types if t in ("data", "backend", "frontend", "infra", "product")]
    if not project_types:
        project_types = ["backend"]
    raw_tool = data.get("tool", "cursor")
    tool = raw_tool if raw_tool in ("cursor", "claude-code") else "cursor"
    return ProjectConfig(
        project_types=project_types,
        registry=registry,
        tool=tool,
        installed=installed,
        installed_bundles=installed_bundles,
    )


def load_config(project_root: Path) -> ProjectConfig | None:
    """Load project config from project_root/.forge/config.yaml.

    Args:
        project_root: Path to project root (directory containing .forge/).

    Returns:
        ProjectConfig if file exists and is valid; None otherwise.
    """
    config_path = Path(project_root) / ".forge" / "config.yaml"
    if not config_path.exists():
        return None
    try:
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return None
        return _coerce_project_config(data)
    except Exception:
        return None


def save_config(project_root: Path, config: ProjectConfig) -> None:
    """Write project config to project_root/.forge/config.yaml.

    Args:
        project_root: Path to project root.
        config: Config to write.
    """
    root = Path(project_root)
    config_dir = root / ".forge"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.yaml"
    data = {
        "project_types": config.project_types,
        "registry": {
            "url": config.registry.url,
            "ref": config.registry.ref,
        },
        "tool": config.tool,
        "installed": [
            {
                "kind": item.kind,
                "id": item.id,
                "version": item.version,
                "source_registry_ref": item.source_registry_ref,
            }
            for item in config.installed
        ],
        "installed_bundles": [
            {
                "id": b.id,
                "version": b.version,
                "source_registry_ref": b.source_registry_ref,
                "members": [{"kind": m.kind, "id": m.id} for m in b.members],
            }
            for b in config.installed_bundles
        ],
    }
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
