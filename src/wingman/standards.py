"""Opinionated per-stack tooling standards: pyproject tool tables + pre-commit.

Wingman ships one baseline per stack under ``data/standards/<stack>/``. The
compare helpers report which categories in the target repo differ from that
baseline; the writer is non-destructive: it creates a missing
``.pre-commit-config.yaml`` but never overwrites one that already differs, and
it never edits an existing ``pyproject.toml`` (it only reports).
"""

from __future__ import annotations

import re
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path

from wingman.core import data_path, repo_root

DEFAULT_STACK = "python"
PYPROJECT = Path("pyproject.toml")
PRECOMMIT = Path(".pre-commit-config.yaml")

# pyproject [tool.<category>] tables wingman is opinionated about.
PYPROJECT_CATEGORIES = ["ruff", "pytest", "ty", "uv"]

# Dev tools the standard expects to be runnable via `uv run` and pre-commit.
# `uv audit` is native to uv, so it needs no dependency of its own.
DEV_TOOLS = ["ruff", "ty", "pytest", "pre-commit"]

_VERSION_OP = re.compile(r"[<>=!~]")


@dataclass
class CategoryStatus:
    name: str
    status: str  # "ok" | "missing" | "differs" | "no-pyproject"


def standard_dir(stack: str | None) -> Path:
    return data_path() / "standards" / (stack or DEFAULT_STACK)


def pyproject_tools_text(stack: str | None) -> str:
    return (standard_dir(stack) / "pyproject-tools.toml").read_text()


def precommit_text(stack: str | None) -> str:
    return (standard_dir(stack) / "pre-commit-config.yaml").read_text()


def _pyproject_standard(stack: str | None) -> dict:
    return tomllib.loads(pyproject_tools_text(stack)).get("tool", {})


def compare_pyproject(stack: str | None) -> list[CategoryStatus]:
    """Per-category status of the repo's pyproject tool tables vs the standard."""
    std = _pyproject_standard(stack)
    path = repo_root() / PYPROJECT
    if not path.exists():
        return [CategoryStatus(c, "no-pyproject") for c in PYPROJECT_CATEGORIES]
    repo_tool = tomllib.loads(path.read_text()).get("tool", {})
    out: list[CategoryStatus] = []
    for cat in PYPROJECT_CATEGORIES:
        have = repo_tool.get(cat)
        if have is None:
            out.append(CategoryStatus(cat, "missing"))
        elif have == std.get(cat):
            out.append(CategoryStatus(cat, "ok"))
        else:
            out.append(CategoryStatus(cat, "differs"))
    return out


def compare_precommit(stack: str | None) -> str:
    """Status of the repo's .pre-commit-config.yaml vs the standard."""
    path = repo_root() / PRECOMMIT
    if not path.exists():
        return "missing"
    return "ok" if path.read_text() == precommit_text(stack) else "differs"


def write_precommit(stack: str | None, dry_run: bool = False) -> bool:
    """Write .pre-commit-config.yaml only if absent. Returns True if written."""
    if compare_precommit(stack) != "missing":
        return False
    if not dry_run:
        (repo_root() / PRECOMMIT).write_text(precommit_text(stack))
    return True


def _requirement_name(req: str) -> str:
    return re.split(r"[<>=!~;@\[\s]", req.strip(), maxsplit=1)[0]


def _is_pinned(req: str) -> bool:
    """True if a PEP 508 requirement string declares a version or direct reference."""
    base = req.split(";", 1)[0].strip()  # drop environment markers
    if not base:
        return True
    if "@" in base:  # direct URL / path reference
        return True
    base = re.sub(r"\[[^\]]*\]", "", base)  # drop extras
    return bool(_VERSION_OP.search(base))


def unpinned_dependencies() -> list[str]:
    """Names of pyproject dependencies (incl. groups/extras) that lack a version."""
    unpinned = {_requirement_name(r) for r in _all_requirements() if not _is_pinned(r)}
    unpinned.discard("")
    return sorted(unpinned)


def _all_requirements() -> list[str]:
    """Every requirement string in pyproject: deps, extras, and dependency groups."""
    path = repo_root() / PYPROJECT
    if not path.exists():
        return []
    data = tomllib.loads(path.read_text())
    project = data.get("project", {})
    reqs: list[str] = list(project.get("dependencies", []))
    for extra in (project.get("optional-dependencies") or {}).values():
        reqs += extra
    for group in (data.get("dependency-groups") or {}).values():
        reqs += [g for g in group if isinstance(g, str)]
    return reqs


def declared_dependency_names() -> set[str]:
    """Lower-cased names of every dependency declared in pyproject."""
    return {_requirement_name(r).lower() for r in _all_requirements()} - {""}


def missing_dev_tools() -> list[str]:
    """Standard dev tools (ruff/ty/pytest/pre-commit) not yet declared as deps."""
    if not (repo_root() / PYPROJECT).exists():
        return []
    have = declared_dependency_names()
    return [t for t in DEV_TOOLS if t not in have]


def add_dev_tools(tools: list[str], dry_run: bool = False) -> tuple[bool, str]:
    """Add ``tools`` to the dev dependency group via ``uv add --dev``."""
    if not tools:
        return True, "no dev tools to add"
    cmd = ["uv", "add", "--dev", *tools]
    if dry_run:
        return True, "[dry-run] " + " ".join(cmd)
    return _run_uv(cmd)


def install_precommit_hook(dry_run: bool = False) -> tuple[bool, str]:
    """Install the git pre-commit hook via ``uv run pre-commit install``."""
    cmd = ["uv", "run", "pre-commit", "install"]
    if dry_run:
        return True, "[dry-run] " + " ".join(cmd)
    return _run_uv(cmd)


def _run_uv(cmd: list[str]) -> tuple[bool, str]:
    """Run a ``uv`` command, returning (ok, message) without raising if uv is absent."""
    joined = " ".join(cmd)
    try:
        proc = subprocess.run(cmd, cwd=repo_root())
    except OSError:
        return False, f"{joined} (uv not found — install uv or activate a virtualenv)"
    return proc.returncode == 0, joined
