"""Tara configuration (Pydantic), persisted in ``.tara/config.toml``.

``tara init`` writes this file to record the repo's setup state: the agent tool
it was set up for and the default stack. Optional tables tune behavior: the
``[standards]`` table overrides the tooling baseline, and ``[agents]`` controls
the ``.agents/`` doc store. Freshly written configs include commented examples
of these options so they are discoverable. The models here read the file back.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

from tara.core import repo_root

CONFIG = Path(".tara") / "config.toml"

_HEADER = "# Tara setup state, written by `tara init`. Safe to edit by hand.\n"

# Commented examples appended to a freshly written config so the optional knobs
# are discoverable. Only emitted for tables the config does not already set.
_OPTION_DOCS: dict[str, str] = {
    "standards": (
        "# [standards]  # override the opinionated tooling baseline\n"
        '# default_stack = "python"\n'
        '# pyproject_categories = ["ruff", "pytest", "ty", "uv"]\n'
        '# dev_tools = ["ruff", "ty", "pytest", "pre-commit"]\n'
    ),
    "agents": (
        "# [agents]  # keep parts of the .agents/ doc store local (untracked)\n"
        '# gitignore = ["memory"]  # e.g. do not commit session scratch/handover\n'
    ),
}


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


class AgentsConfig(BaseModel):
    """Controls the ``.agents/`` doc store. The store is tracked by default.

    ``gitignore`` lists subpaths under ``.agents/`` to keep local (untracked),
    for example ``["memory"]`` to avoid committing session scratch.
    """

    gitignore: list[str] = Field(default_factory=list)


class TaraConfig(BaseModel):
    """Repo setup state recorded by ``tara init``.

    ``tool`` is the agent tool the repo is set up for (``copilot``, ``opencode``,
    or ``all``); ``stack`` is the default stack; ``standards`` holds optional
    tooling overrides; ``agents`` tunes the ``.agents/`` doc store.
    """

    tool: str = "copilot"
    stack: str = "python"
    standards: StandardsConfig = Field(default_factory=StandardsConfig)
    agents: AgentsConfig = Field(default_factory=AgentsConfig)

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
    """Record setup state in ``.tara/config.toml``, preserving existing overrides.

    Optional tables the config does not set are appended as commented examples so
    the available knobs stay discoverable.
    """
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
    docs = "\n".join(doc for name, doc in _OPTION_DOCS.items() if name not in data)
    text = _HEADER + _dump(data)
    if docs:
        text += "\n# --- optional settings (uncomment to enable) ---\n" + docs
    path.write_text(text)
    verb = "updated" if existing else "wrote"
    return f"  {verb} {rel} (tool={tool}, stack={stack})"
