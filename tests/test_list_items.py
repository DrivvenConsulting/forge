"""Tests for list_items (with registry_root to avoid git fetch)."""

from pathlib import Path

import pytest

from forge.core.list_items import list_items


def test_list_items_filtered_by_project_type(registry_root: Path) -> None:
    items = list_items(
        "https://example.com/registry.git",
        "main",
        "backend",
        category=None,
        registry_root=registry_root,
    )
    ids = [(i.kind, i.id) for i in items]
    assert ("agent", "test-agent") in ids
    assert ("rule", "test-rule") in ids
    assert ("skill", "test-skill") in ids
    assert ("bundle", "test-bundle") in ids


def test_list_items_filtered_by_category(registry_root: Path) -> None:
    items = list_items(
        "https://example.com/registry.git",
        "main",
        "backend",
        category="rule",
        registry_root=registry_root,
    )
    assert all(i.kind == "rule" for i in items)
    assert len(items) == 1
    assert items[0].id == "test-rule"


def test_list_items_incompatible_project_type(registry_root: Path) -> None:
    items = list_items(
        "https://example.com/registry.git",
        "main",
        "infra",
        category=None,
        registry_root=registry_root,
    )
    assert len(items) == 0
