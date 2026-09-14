"""Optional Claude Code hooks, shipped as package data and merged into settings.

A hook turns a written-down convention into one the tool enforces: Claude Code
runs it around a tool call and can block the write. Tara ships bundles under
``data/catalog/hooks/<name>.hooks.json``; installing one merges its events into
the repo's ``.claude/settings.json``.

The merge only ever appends. An entry the developer wrote is never rewritten or
removed, and re-installing the same bundle is a no-op, so the file stays theirs.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from tara.core import data_path, repo_root

SETTINGS = Path(".claude") / "settings.json"
HOOKS_SUFFIX = ".hooks.json"


class HookError(Exception):
    """A hook bundle is unknown, malformed, or cannot be merged."""


def hooks_dir() -> Path:
    """Directory holding the bundled hook definitions (package data)."""
    return data_path() / "catalog" / "hooks"


def bundle_names() -> list[str]:
    """Names of every bundled hook definition, sorted."""
    base = hooks_dir()
    if not base.is_dir():
        return []
    return sorted(
        p.name.removesuffix(HOOKS_SUFFIX) for p in base.glob(f"*{HOOKS_SUFFIX}")
    )


def read_bundle(name: str) -> dict[str, Any]:
    """Read one hook bundle by name.

    Raises:
        HookError: when no bundle of that name is bundled, or its JSON is broken.
    """
    path = hooks_dir() / f"{name}{HOOKS_SUFFIX}"
    if not path.is_file():
        raise HookError(f"unknown hook bundle '{name}'")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as err:
        raise HookError(f"hook bundle '{name}' is not valid JSON: {err}") from err
    if not isinstance(data, dict) or not isinstance(data.get("hooks"), dict):
        raise HookError(f"hook bundle '{name}' has no 'hooks' mapping")
    return data


def _read_settings(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as err:
        raise HookError(f"{SETTINGS.as_posix()} is not valid JSON: {err}") from err
    if not isinstance(data, dict):
        raise HookError(f"{SETTINGS.as_posix()} is not a JSON object")
    return data


def _actions(entry: object) -> set[str]:
    """The command and prompt strings one matcher entry runs.

    Identity is the action text, because that is what actually executes. Two
    entries carrying the same command are the same hook however they are
    matched or spelled.
    """
    if not isinstance(entry, dict):
        return set()
    out: set[str] = set()
    entries = entry.get("hooks", [])
    if not isinstance(entries, list):
        return out
    for hook in entries:
        if isinstance(hook, dict):
            for key in ("command", "prompt"):
                value = hook.get(key)
                if isinstance(value, str):
                    out.add(value)
    return out


def _installed_actions(settings: dict[str, Any], event: str) -> set[str]:
    entries = settings.get("hooks", {}).get(event, [])
    if not isinstance(entries, list):
        return set()
    return {action for entry in entries for action in _actions(entry)}


def merge(
    settings: dict[str, Any], bundle: dict[str, Any]
) -> tuple[dict[str, Any], int]:
    """Merge a bundle's events into ``settings``. Returns the result and how many entries were added.

    Appends whole matcher entries; an existing entry is never edited, so a
    developer's own hook keeps running exactly as written. An entry whose
    actions are all present already is skipped, which makes re-install a no-op.
    """
    merged = json.loads(json.dumps(settings))  # deep copy, JSON in and JSON out
    events = merged.setdefault("hooks", {})
    if not isinstance(events, dict):
        raise HookError(f"{SETTINGS.as_posix()} has a non-object 'hooks' key")
    added = 0
    for event, entries in bundle["hooks"].items():
        existing = events.setdefault(event, [])
        if not isinstance(existing, list):
            raise HookError(f"{SETTINGS.as_posix()} has a non-list '{event}' hook list")
        present = _installed_actions(merged, event)
        for entry in entries:
            actions = _actions(entry)
            if actions and actions <= present:
                continue
            existing.append(entry)
            present |= actions
            added += 1
    return merged, added


def missing_requirements(bundle: dict[str, Any]) -> list[str]:
    """Executables the bundle needs that are not on PATH."""
    return [tool for tool in bundle.get("requires", []) if shutil.which(tool) is None]


def is_installed(name: str) -> bool:
    """Whether every action in a bundled hook already exists in settings."""
    bundle = read_bundle(name)
    settings = _read_settings(repo_root() / SETTINGS)
    _, added = merge(settings, bundle)
    return added == 0


def install(name: str, dry_run: bool = False) -> str:
    """Merge a bundled hook definition into the repo's Claude Code settings.

    Returns a status line. Nothing is written when the bundle is already
    installed, so the developer's file is left byte-for-byte alone.
    """
    bundle = read_bundle(name)
    path = repo_root() / SETTINGS
    settings = _read_settings(path)
    merged, added = merge(settings, bundle)
    rel = SETTINGS.as_posix()

    if added == 0:
        return f"  hooks   {name} already in {rel}"
    if dry_run:
        return f"  hooks   would add {added} to {rel} ({name})"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(merged, indent=2) + "\n")
    line = f"  hooks   {name} → {rel} ({added} added)"
    missing = missing_requirements(bundle)
    if missing:
        line += (
            f"\n  ⚠ needs {', '.join(missing)} on PATH; the hook is a no-op without it"
        )
    return line
