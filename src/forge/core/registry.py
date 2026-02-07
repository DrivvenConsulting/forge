"""Fetch registry repo and parse manifests into in-memory registry items."""

import hashlib
import os
import subprocess
from pathlib import Path

import yaml

from forge.core.models import (
    BundleItemRef,
    BundleManifest,
    ItemKind,
    ItemManifest,
    RegistryItem,
)

REGISTRY_CATEGORIES: tuple[str, ...] = ("agents", "rules", "skills", "bundles")
KIND_FROM_DIR: dict[str, ItemKind] = {
    "agents": "agent",
    "rules": "rule",
    "skills": "skill",
    "bundles": "bundle",
}


def _cache_dir() -> Path:
    """Return the Forge cache directory (e.g. ~/.forge/cache)."""
    base = Path.home() / ".forge" / "cache"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _registry_cache_key(url: str, ref: str) -> str:
    """Return a stable directory name for this registry URL + ref."""
    content = f"{url}\n{ref}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def fetch_registry(url: str, ref: str, cache_dir: Path | None = None) -> Path:
    """Clone or update the registry repo at url/ref; return path to repo root.

    Uses a cache keyed by url+ref. If the directory already exists, runs git fetch
    and checkout so the ref is up to date.

    Args:
        url: Git clone URL (e.g. https://github.com/org/forge-registry.git).
        ref: Branch or tag (e.g. main, v1.0.0).
        cache_dir: Override cache root (for tests). Defaults to ~/.forge/cache.

    Returns:
        Path to the registry repo root.

    Raises:
        RuntimeError: If git clone or fetch fails.
    """
    root = cache_dir or _cache_dir()
    key = _registry_cache_key(url, ref)
    repo_path = root / key

    if repo_path.exists():
        try:
            subprocess.run(
                ["git", "fetch", "origin", ref, "--depth", "1"],
                cwd=repo_path,
                check=True,
                capture_output=True,
                timeout=60,
            )
            subprocess.run(
                ["git", "checkout", "FETCH_HEAD"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to update registry: {e.stderr.decode() if e.stderr else e}")
        except FileNotFoundError:
            raise RuntimeError("Git is not installed or not on PATH")
    else:
        try:
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    ref,
                    url,
                    str(repo_path),
                ],
                check=True,
                capture_output=True,
                timeout=120,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clone registry: {e.stderr.decode() if e.stderr else e}")
        except FileNotFoundError:
            raise RuntimeError("Git is not installed or not on PATH")

    return repo_path


def _load_manifest_yaml(path: Path) -> dict:
    """Load a YAML file; return empty dict if missing or invalid."""
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _parse_item_manifest(manifest_path: Path) -> ItemManifest | None:
    """Parse manifest.yaml for an agent/rule/skill. Returns None if invalid."""
    data = _load_manifest_yaml(manifest_path)
    if not data or "version" not in data or "project_types" not in data:
        return None
    try:
        return ItemManifest(
            version=str(data["version"]),
            project_types=[str(x) for x in data["project_types"]],
            description=str(data["description"]) if data.get("description") else None,
        )
    except Exception:
        return None


def _parse_bundle_manifest(manifest_path: Path) -> BundleManifest | None:
    """Parse manifest.yaml for a bundle. Returns None if invalid."""
    data = _load_manifest_yaml(manifest_path)
    if not data or "version" not in data or "project_types" not in data or "items" not in data:
        return None
    try:
        items = [
            BundleItemRef(kind=ref["kind"], id=ref["id"])
            for ref in data["items"]
            if isinstance(ref, dict) and ref.get("kind") in ("agent", "rule", "skill") and ref.get("id")
        ]
        if not items:
            return None
        return BundleManifest(
            version=str(data["version"]),
            project_types=[str(x) for x in data["project_types"]],
            description=str(data["description"]) if data.get("description") else None,
            items=items,
        )
    except Exception:
        return None


def get_registry_items(registry_root: Path) -> list[RegistryItem]:
    """Walk registry_root and build list of RegistryItem from manifest.yaml files.

    Args:
        registry_root: Path to the cloned registry repo root.

    Returns:
        List of all registry items (agents, rules, skills, bundles).
    """
    registry_root = Path(registry_root)
    result: list[RegistryItem] = []

    for category in REGISTRY_CATEGORIES:
        kind = KIND_FROM_DIR[category]
        dir_path = registry_root / category
        if not dir_path.is_dir():
            continue
        for item_dir in dir_path.iterdir():
            if not item_dir.is_dir():
                continue
            item_id = item_dir.name
            manifest_path = item_dir / "manifest.yaml"
            if kind == "bundle":
                bundle_manifest = _parse_bundle_manifest(manifest_path)
                if bundle_manifest is None:
                    continue
                result.append(
                    RegistryItem(
                        kind="bundle",
                        id=item_id,
                        version=bundle_manifest.version,
                        project_types=bundle_manifest.project_types,
                        description=bundle_manifest.description,
                        path=f"{category}/{item_id}",
                        items=bundle_manifest.items,
                    )
                )
            else:
                item_manifest = _parse_item_manifest(manifest_path)
                if item_manifest is None:
                    continue
                result.append(
                    RegistryItem(
                        kind=kind,
                        id=item_id,
                        version=item_manifest.version,
                        project_types=item_manifest.project_types,
                        description=item_manifest.description,
                        path=f"{category}/{item_id}",
                        items=None,
                    )
                )
    return result
