"""Tests for validation (project type compatibility)."""

from forge.core.models import RegistryItem
from forge.core.validation import is_compatible_with_project_type, is_valid_project_type


def test_is_compatible_with_project_type() -> None:
    item = RegistryItem(
        kind="rule",
        id="r1",
        version="1.0.0",
        project_types=["backend", "data"],
        path="rules/r1",
    )
    assert is_compatible_with_project_type(item, "backend") is True
    assert is_compatible_with_project_type(item, "data") is True
    assert is_compatible_with_project_type(item, "frontend") is False


def test_is_valid_project_type() -> None:
    assert is_valid_project_type("backend") is True
    assert is_valid_project_type("data") is True
    assert is_valid_project_type("invalid") is False
