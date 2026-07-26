"""Tara configuration models (Pydantic), loaded from ``.tara/config.toml``."""

from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

from tara.core import repo_root

_CONFIG = Path(".tara") / "config.toml"


class StandardsConfig(BaseModel):
    """Opinionated tooling standard. The stack is flexible; these are the defaults.

    Override any field under ``[standards]`` in ``.tara/config.toml``.
    """

    default_stack: str = "python"
    pyproject_categories: list[str] = Field(
        default_factory=lambda: ["ruff", "pytest", "ty", "uv"]
    )
    dev_tools: list[str] = Field(
        default_factory=lambda: ["ruff", "ty", "pytest", "pre-commit"]
    )

    @classmethod
    def load(cls) -> StandardsConfig:
        """Read the ``[standards]`` table from config, or fall back to defaults."""
        path = repo_root() / _CONFIG
        if not path.exists():
            return cls()
        table = tomllib.loads(path.read_text()).get("standards", {})
        return cls.model_validate(table)
