"""Tests for registry parsing (get_registry_items)."""

from pathlib import Path

from forge.core.registry import get_registry_items


def test_get_registry_items(registry_root: Path) -> None:
    items = get_registry_items(registry_root)
    by_kind_id = {(i.kind, i.id): i for i in items}
    assert ("agent", "test-agent") in by_kind_id
    assert ("rule", "test-rule") in by_kind_id
    assert ("skill", "test-skill") in by_kind_id
    assert ("bundle", "test-bundle") in by_kind_id
    bundle = by_kind_id[("bundle", "test-bundle")]
    assert bundle.items is not None
    assert len(bundle.items) == 2
    assert bundle.items[0].kind == "rule" and bundle.items[0].id == "test-rule"
    assert items[0].version == "1.0.0"
    assert "backend" in items[0].project_types
