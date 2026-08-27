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

from pydantic import BaseModel, Field, ValidationError, field_validator

from tara.core import COPILOT, normalize_integrations, repo_root

CONFIG = Path(".tara") / "config.toml"


class ConfigError(Exception):
    """``.tara/config.toml`` says something Tara cannot act on.

    Raised instead of falling back to defaults: a typo in ``integrations`` must be
    reported, not silently turned into a setup the developer did not ask for.
    The CLI reports it as a one-line error and exits non-zero.
    """


def _explain(exc: ValidationError) -> str:
    """Render a ValidationError as one readable ``key: reason`` line per problem."""
    lines = []
    for err in exc.errors():
        key = ".".join(str(part) for part in err["loc"]) or "config"
        reason = err["msg"].removeprefix("Value error, ")
        lines.append(f"  {key}: {reason}")
    return "\n".join(lines)


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

    ``integrations`` lists the coding-agent products Tara targets; Copilot is present
    because every other tool's files are generated from its ``.github/`` setup.
    ``stack`` is the default stack; ``standards`` holds optional tooling
    overrides; ``agents`` tunes the ``.agents/`` doc store.
    """

    integrations: list[str] = Field(default_factory=lambda: [COPILOT])
    stack: str = "python"
    standards: StandardsConfig = Field(default_factory=StandardsConfig)
    agents: AgentsConfig = Field(default_factory=AgentsConfig)

    @field_validator("integrations", mode="before")
    @classmethod
    def _normalize(cls, value: object) -> list[str]:
        """Accept a list, a single name, or the legacy ``all`` shorthand."""
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            raise ValueError("integrations must be a string or list of strings")
        if not all(isinstance(item, str) for item in value):
            raise ValueError("integrations must contain only strings")
        return normalize_integrations([item for item in value if isinstance(item, str)])

    @classmethod
    def load(cls) -> TaraConfig:
        """Read ``.tara/config.toml``, or return defaults if it is absent.

        Raises :class:`ConfigError` when the file exists but cannot be used, so
        the command reports what is wrong with it rather than guessing.
        """
        path = repo_root() / CONFIG
        if not path.exists():
            return cls()
        try:
            raw = tomllib.loads(path.read_text())
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(f"{CONFIG} is not valid TOML: {exc}") from exc
        except OSError as exc:
            raise ConfigError(f"cannot read {CONFIG}: {exc}") from exc
        if "integrations" not in raw:
            if "tools" in raw:
                raw["integrations"] = raw.pop("tools")
            elif "tool" in raw:
                legacy = raw.pop("tool")
                raw["integrations"] = (
                    [COPILOT, "opencode"] if legacy == "all" else legacy
                )
        try:
            return cls.model_validate(raw)
        except ValidationError as exc:
            raise ConfigError(f"{CONFIG} is invalid:\n{_explain(exc)}") from exc

    @property
    def port_targets(self) -> list[str]:
        """Configured integrations whose files are generated from Copilot."""
        return [
            integration for integration in self.integrations if integration != COPILOT
        ]


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


def write_config(integrations: list[str] | str, stack: str, dry_run: bool) -> str:
    """Record setup state in ``.tara/config.toml``, preserving existing overrides.

    Optional tables the config does not set are appended as commented examples so
    the available knobs stay discoverable.
    """
    path = repo_root() / CONFIG
    existing = tomllib.loads(path.read_text()) if path.exists() else {}
    selected = normalize_integrations(integrations)
    data: dict[str, object] = {"integrations": selected, "stack": stack}
    for key, value in existing.items():
        if key not in ("tool", "tools", "integrations", "stack"):
            data[key] = value
    rel = CONFIG.as_posix()
    listed = ", ".join(selected)
    if dry_run:
        verb = "update" if path.exists() else "write"
        return f"  [dry-run] {verb} {rel} (integrations={listed}, stack={stack})"
    path.parent.mkdir(parents=True, exist_ok=True)
    docs = "\n".join(doc for name, doc in _OPTION_DOCS.items() if name not in data)
    text = _HEADER + _dump(data)
    if docs:
        text += "\n# --- optional settings (uncomment to enable) ---\n" + docs
    path.write_text(text)
    verb = "updated" if existing else "wrote"
    return f"  {verb} {rel} (integrations={listed}, stack={stack})"
