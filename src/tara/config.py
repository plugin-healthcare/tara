"""Tara configuration (Pydantic), persisted in ``.tara/config.toml``.

``tara init`` writes this file to record the repo's setup state: the agent tool
it was set up for and the default stack. The optional ``[standards]`` table
overrides the opinionated tooling baseline. The models here read it back.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

from tara.core import repo_root

CONFIG = Path(".tara") / "config.toml"

_HEADER = "# Tara setup state, written by `tara init`. Safe to edit by hand.\n"


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
        """Read the ``[standards]`` overrides, or fall back to defaults."""
        return TaraConfig.load().standards


class TaraConfig(BaseModel):
    """Repo setup state recorded by ``tara init``.

    ``tool`` is the agent tool the repo is set up for (``copilot``, ``opencode``,
    or ``all``); ``stack`` is the default stack; ``standards`` holds optional
    tooling overrides.
    """

    tool: str = "copilot"
    stack: str = "python"
    standards: StandardsConfig = Field(default_factory=StandardsConfig)

    @classmethod
    def load(cls) -> TaraConfig:
        """Read ``.tara/config.toml``, or return defaults if it is absent."""
        path = repo_root() / CONFIG
        if not path.exists():
            return cls()
        return cls.model_validate(tomllib.loads(path.read_text()))


def _esc(value: str) -> str:
    """Escape a string for a double-quoted TOML value."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _fmt(value: object) -> str:
    """Render a scalar or string list as a TOML value."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_fmt(v) for v in value) + "]"
    return f'"{_esc(str(value))}"'


def _dump(data: dict[str, object]) -> str:
    """Serialize a shallow config (scalars/lists + one level of tables) to TOML."""
    lines: list[str] = []
    tables: list[tuple[str, dict]] = []
    for key, value in data.items():
        if isinstance(value, dict):
            tables.append((key, value))
        else:
            lines.append(f"{key} = {_fmt(value)}")
    for name, table in tables:
        lines.append("")
        lines.append(f"[{name}]")
        lines.extend(f"{k} = {_fmt(v)}" for k, v in table.items())
    return "\n".join(lines) + "\n"


def write_config(tool: str, stack: str, dry_run: bool) -> str:
    """Record setup state in ``.tara/config.toml``, preserving existing overrides."""
    path = repo_root() / CONFIG
    existing = tomllib.loads(path.read_text()) if path.exists() else {}
    data: dict[str, object] = {"tool": tool, "stack": stack}
    for key, value in existing.items():
        if key not in ("tool", "stack"):
            data[key] = value
    rel = CONFIG.as_posix()
    if dry_run:
        verb = "update" if path.exists() else "write"
        return f"  [dry-run] {verb} {rel} (tool={tool}, stack={stack})"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_HEADER + _dump(data))
    verb = "updated" if existing else "wrote"
    return f"  {verb} {rel} (tool={tool}, stack={stack})"
