"""Opinionated per-stack tooling standards: pyproject tool tables + pre-commit.

Tara ships one baseline per stack under ``data/standards/<stack>/``. The
compare helpers report which categories in the target repo differ from that
baseline; the writer is non-destructive: it creates a missing
``.pre-commit-config.yaml`` but never overwrites one that already differs, and
it never edits an existing ``pyproject.toml`` (it only reports).
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from tara.core import data_path, repo_root

DEFAULT_STACK = "python"
PYPROJECT = Path("pyproject.toml")
PRECOMMIT = Path(".pre-commit-config.yaml")

# pyproject [tool.<category>] tables Tara is opinionated about.
PYPROJECT_CATEGORIES = ["ruff", "pytest", "ty", "uv"]

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
    unpinned = {_requirement_name(r) for r in reqs if not _is_pinned(r)}
    unpinned.discard("")
    return sorted(unpinned)
