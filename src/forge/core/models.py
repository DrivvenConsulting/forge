"""Pydantic models for registry items, manifests, and project config."""

from typing import Literal

from pydantic import BaseModel, Field

ItemKind = Literal["agent", "rule", "skill", "bundle", "workflow", "prompt"]
ProjectType = Literal["data", "backend", "frontend", "infra", "product"]

PROJECT_TYPES: tuple[ProjectType, ...] = ("data", "backend", "frontend", "infra", "product")
ITEM_KINDS: tuple[ItemKind, ...] = ("agent", "rule", "skill", "bundle", "workflow", "prompt")


class ItemManifest(BaseModel):
    """Manifest for a single registry item (agent, rule, skill)."""

    version: str = Field(..., min_length=1)
    project_types: list[str] = Field(..., min_length=1)
    description: str | None = None


class BundleItemRef(BaseModel):
    """Reference to an item inside a bundle."""

    kind: Literal["agent", "rule", "skill", "workflow", "prompt"]
    id: str = Field(..., min_length=1)


class BundleManifest(BaseModel):
    """Manifest for a bundle (collection of items)."""

    version: str = Field(..., min_length=1)
    project_types: list[str] = Field(..., min_length=1)
    description: str | None = None
    items: list[BundleItemRef] = Field(..., min_length=1)


class RegistryItem(BaseModel):
    """In-memory representation of a registry entry (agent, rule, skill, or bundle)."""

    kind: ItemKind
    id: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    project_types: list[str] = Field(..., min_length=1)
    description: str | None = None
    path: str = Field(..., description="Relative path inside registry root, e.g. agents/backend-engineer")
    items: list[BundleItemRef] | None = Field(
        default=None,
        description="For bundles only: list of item references",
    )


class InstalledItem(BaseModel):
    """Record of an installed item in project config."""

    kind: Literal["agent", "rule", "skill", "workflow", "prompt"]
    id: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    source_registry_ref: str = Field(..., description="Git ref used at install time, e.g. main or v1.0.0")


class RegistryConfig(BaseModel):
    """Registry URL and ref from project config."""

    url: str = Field(..., min_length=1)
    ref: str = Field(default="main", min_length=1)


class ProjectConfig(BaseModel):
    """Project-level Forge configuration (.forge/config.yaml)."""

    project_types: list[ProjectType] = Field(..., min_length=1)
    registry: RegistryConfig
    installed: list[InstalledItem] = Field(default_factory=list)
