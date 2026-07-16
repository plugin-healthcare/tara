"""The check gate: run a project's lint/format/test commands in order.

Tara is Python + uv focused, so the bundled default gate runs ``uv run ruff``
and ``uv run pytest``. Override per-repo with ``.tara/checks.toml``.
"""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from tara.core import data_path, repo_root

LOCAL_CHECKS = Path(".tara") / "checks.toml"
DEFAULT_STACK = "python"

# `uv audit` and `uv run ty` in the default gate need a recent uv.
MIN_UV = (0, 11)


@dataclass
class Check:
    name: str
    cmd: str


@dataclass
class CheckResult:
    name: str
    cmd: str
    returncode: int

    @property
    def passed(self) -> bool:
        return self.returncode == 0


def _parse(text: str) -> list[Check]:
    raw = tomllib.loads(text).get("check", [])
    return [Check(name=c["name"], cmd=c["cmd"]) for c in raw]


def load_checks(stack: str | None) -> list[Check]:
    """Repo-local ``.tara/checks.toml`` wins; else bundled stack defaults."""
    local = repo_root() / LOCAL_CHECKS
    if local.exists():
        return _parse(local.read_text())
    bundled = data_path() / "checks" / f"{stack or DEFAULT_STACK}.toml"
    if not bundled.exists():
        raise FileNotFoundError(
            f"no checks defined for stack '{stack or DEFAULT_STACK}' "
            f"(create {LOCAL_CHECKS} to define your own)"
        )
    return _parse(bundled.read_text())


def _uv_version() -> tuple[int, ...] | None:
    """Parsed ``uv --version`` (major, minor, patch), or None if uv is absent."""
    try:
        out = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, check=False
        )
    except (FileNotFoundError, OSError):
        return None
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", out.stdout)
    return tuple(int(g) for g in m.groups()) if m else None


def _uv_preflight(checks: list[Check]) -> CheckResult | None:
    """If any check shells out to uv, ensure a new-enough uv is installed."""
    if not any(re.search(r"\buv\b", c.cmd) for c in checks):
        return None
    version = _uv_version()
    if version is None:
        print("error: uv is not installed but the gate needs it", file=sys.stderr)
        return CheckResult("uv-version", "uv --version", 127)
    if version[:2] < MIN_UV:
        want = ".".join(str(p) for p in MIN_UV)
        have = ".".join(str(p) for p in version)
        print(
            f"error: uv {have} is too old; the gate needs uv >= {want} "
            "(for `uv audit` and `uv run ty`)",
            file=sys.stderr,
        )
        return CheckResult("uv-version", "uv --version", 1)
    return None


def run_checks(stack: str | None, fail_fast: bool = True) -> list[CheckResult]:
    """Run each check in CWD, streaming output. Stop on first failure if fail_fast."""
    checks = load_checks(stack)
    preflight = _uv_preflight(checks)
    if preflight is not None:
        return [preflight]
    results: list[CheckResult] = []
    for check in checks:
        proc = subprocess.run(shlex.split(check.cmd), cwd=repo_root())
        results.append(CheckResult(check.name, check.cmd, proc.returncode))
        if fail_fast and proc.returncode != 0:
            break
    return results
