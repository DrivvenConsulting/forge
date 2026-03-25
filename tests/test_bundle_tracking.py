"""Bundle-level install, update, remove, and refcount behavior."""

from pathlib import Path

import pytest

from forge.core.install import install_bundle, install_item
from forge.core.models import ProjectConfig, RegistryConfig
from forge.core.project import load_config, save_config
from forge.core.registry import get_registry_items
from forge.core.remove import remove_bundle
from forge.core.update import update_bundle


def _add_alt_bundle(registry_root: Path) -> None:
    """Second bundle that also includes test-rule (for refcount tests)."""
    bundle_dir = registry_root / "bundles" / "test-bundle-alt"
    bundle_dir.mkdir(parents=True)
    (bundle_dir / "manifest.yaml").write_text(
        "version: '1.0.0'\nproject_types: [backend, data]\nitems:\n  - kind: rule\n    id: test-rule\n",
        encoding="utf-8",
    )


@pytest.fixture
def registry_two_bundles(registry_root: Path) -> Path:
    _add_alt_bundle(registry_root)
    return registry_root


def test_install_bundle_idempotent_updates_members(registry_root: Path, project_root: Path) -> None:
    config = load_config(project_root)
    assert config is not None
    items = get_registry_items(registry_root)
    by_kind_id = {(i.kind, i.id): i for i in items}
    bundle = by_kind_id[("bundle", "test-bundle")]
    install_bundle(registry_root, bundle, by_kind_id, project_root, config, "main")

    skill_path = project_root / ".cursor" / "skills" / "test-skill" / "SKILL.md"
    assert skill_path.exists()

    bundle_dir = registry_root / "bundles" / "test-bundle"
    (bundle_dir / "manifest.yaml").write_text(
        "version: '2.0.0'\nproject_types: [backend, data]\nitems:\n  - kind: rule\n    id: test-rule\n",
        encoding="utf-8",
    )
    items2 = get_registry_items(registry_root)
    by2 = {(i.kind, i.id): i for i in items2}
    bundle2 = by2[("bundle", "test-bundle")]
    config2 = load_config(project_root)
    assert config2 is not None
    install_bundle(registry_root, bundle2, by2, project_root, config2, "main")

    assert not skill_path.exists()
    assert (project_root / ".cursor" / "rules" / "test-rule" / "RULE.md").exists()
    config3 = load_config(project_root)
    assert config3 is not None
    assert config3.installed_bundles[0].version == "2.0.0"
    assert len(config3.installed_bundles[0].members) == 1


def test_remove_bundle_refcount_two_bundles(registry_two_bundles: Path, project_root: Path) -> None:
    items = get_registry_items(registry_two_bundles)
    by_kind_id = {(i.kind, i.id): i for i in items}
    config = load_config(project_root)
    assert config is not None
    install_bundle(registry_two_bundles, by_kind_id[("bundle", "test-bundle")], by_kind_id, project_root, config, "main")
    config = load_config(project_root)
    assert config is not None
    install_bundle(registry_two_bundles, by_kind_id[("bundle", "test-bundle-alt")], by_kind_id, project_root, config, "main")

    rule_path = project_root / ".cursor" / "rules" / "test-rule" / "RULE.md"
    skill_path = project_root / ".cursor" / "skills" / "test-skill" / "SKILL.md"
    assert rule_path.exists()
    assert skill_path.exists()

    config = load_config(project_root)
    assert config is not None
    assert remove_bundle(project_root, config, "test-bundle")
    assert rule_path.exists()
    assert not skill_path.exists()

    config = load_config(project_root)
    assert config is not None
    assert remove_bundle(project_root, config, "test-bundle-alt")
    assert not rule_path.exists()


def test_remove_bundle_keeps_standalone_overlap(registry_root: Path, project_root: Path) -> None:
    items = get_registry_items(registry_root)
    by_kind_id = {(i.kind, i.id): i for i in items}
    config = load_config(project_root)
    assert config is not None
    install_item(registry_root, by_kind_id[("rule", "test-rule")], project_root, config, "main")
    config = load_config(project_root)
    assert config is not None
    install_bundle(registry_root, by_kind_id[("bundle", "test-bundle")], by_kind_id, project_root, config, "main")

    rule_path = project_root / ".cursor" / "rules" / "test-rule" / "RULE.md"
    config = load_config(project_root)
    assert config is not None
    assert remove_bundle(project_root, config, "test-bundle")
    assert rule_path.exists()


def test_update_bundle(registry_root: Path, project_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("forge.core.update.fetch_registry", lambda url, ref: registry_root)

    items = get_registry_items(registry_root)
    by_kind_id = {(i.kind, i.id): i for i in items}
    config = load_config(project_root)
    assert config is not None
    install_bundle(registry_root, by_kind_id[("bundle", "test-bundle")], by_kind_id, project_root, config, "main")

    bundle_dir = registry_root / "bundles" / "test-bundle"
    (bundle_dir / "manifest.yaml").write_text(
        "version: '3.0.0'\nproject_types: [backend, data]\nitems:\n  - kind: rule\n    id: test-rule\n",
        encoding="utf-8",
    )

    config2 = load_config(project_root)
    assert config2 is not None
    assert update_bundle(project_root, config2, "test-bundle")

    skill_path = project_root / ".cursor" / "skills" / "test-skill" / "SKILL.md"
    assert not skill_path.exists()
    config3 = load_config(project_root)
    assert config3 is not None
    assert config3.installed_bundles[0].version == "3.0.0"


def test_load_save_installed_bundles_roundtrip(tmp_path: Path) -> None:
    from forge.core.models import BundleItemRef, InstalledBundle

    forge_dir = tmp_path / ".forge"
    forge_dir.mkdir()
    config = ProjectConfig(
        project_types=["backend"],
        registry=RegistryConfig(url="https://x.git", ref="main"),
        installed=[],
        installed_bundles=[
            InstalledBundle(
                id="b1",
                version="1.0.0",
                source_registry_ref="main",
                members=[BundleItemRef(kind="rule", id="r1")],
            )
        ],
    )
    save_config(tmp_path, config)
    loaded = load_config(tmp_path)
    assert loaded is not None
    assert len(loaded.installed_bundles) == 1
    assert loaded.installed_bundles[0].id == "b1"
    assert loaded.installed_bundles[0].members[0].kind == "rule"
