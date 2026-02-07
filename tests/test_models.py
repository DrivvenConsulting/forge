"""Tests for core models."""

import pytest

from forge.core.models import (
    BundleItemRef,
    BundleManifest,
    InstalledItem,
    ItemManifest,
    ProjectConfig,
    RegistryConfig,
    RegistryItem,
)


def test_item_manifest() -> None:
    m = ItemManifest(version="1.0.0", project_types=["backend"], description="x")
    assert m.version == "1.0.0"
    assert m.project_types == ["backend"]
    assert m.description == "x"


def test_bundle_manifest() -> None:
    m = BundleManifest(
        version="1.0.0",
        project_types=["backend"],
        items=[BundleItemRef(kind="rule", id="r1"), BundleItemRef(kind="skill", id="s1")],
    )
    assert len(m.items) == 2
    assert m.items[0].kind == "rule" and m.items[0].id == "r1"


def test_registry_item() -> None:
    r = RegistryItem(
        kind="agent",
        id="a1",
        version="1.0.0",
        project_types=["backend"],
        path="agents/a1",
    )
    assert r.kind == "agent"
    assert r.path == "agents/a1"


def test_project_config() -> None:
    c = ProjectConfig(
        project_type="backend",
        registry=RegistryConfig(url="https://x.git", ref="main"),
        installed=[InstalledItem(kind="rule", id="r1", version="1.0.0", source_registry_ref="main")],
    )
    assert c.project_type == "backend"
    assert len(c.installed) == 1
    assert c.installed[0].id == "r1"
