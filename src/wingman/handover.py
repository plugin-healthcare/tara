"""Framework-agnostic agent memory / handover folder.

Agents (any framework) often write session notes, handover docs, and scratch
memory that shouldn't land in git. ``wingman init`` creates a dedicated folder
for these and git-ignores its contents by default. The folder lives under the
emerging ``.agent/`` namespace (paired with the ``AGENTS.md`` convention) so it
stays useful regardless of which agent runtime consumes it.

Opt out of git-ignoring (to *commit* handover docs, e.g. a shared agent memory)
by setting ``gitignore = false`` under ``[handover]`` in ``.wingman/config.toml``.
The folder can also be relocated with ``dir`` in that same section.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from wingman.core import repo_root

# General per-repo wingman settings (introduced for the handover opt-out).
CONFIG = Path(".wingman") / "config.toml"
GITIGNORE = Path(".gitignore")
DEFAULT_DIR = Path(".agent") / "memory"

# Substring that identifies our block in an existing .gitignore, so re-running
# init stays idempotent even if the user tweaks the surrounding comments.
_MARKER = "# Wingman: agent memory / handover"


def load_config() -> dict:
    """Parse ``.wingman/config.toml`` (empty dict if absent)."""
    path = repo_root() / CONFIG
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text())


def handover_settings() -> tuple[Path, bool]:
    """``(folder, gitignore)`` from the ``[handover]`` config, with defaults."""
    cfg = load_config().get("handover", {})
    folder = Path(cfg.get("dir") or DEFAULT_DIR)
    gitignore = bool(cfg.get("gitignore", True))
    return folder, gitignore


def _readme(folder: Path, gitignore: bool) -> str:
    rel = folder.as_posix()
    status = (
        "Its contents are **git-ignored** by default: session and handover docs "
        "written here stay local and never land in version control."
        if gitignore
        else "Its contents are **committed** (git-ignoring was opted out via "
        "`[handover] gitignore = false` in `.wingman/config.toml`), so docs here "
        "are shared through version control as a persistent agent memory."
    )
    keep_note = (
        "This `README.md` is kept tracked so the folder exists on a fresh clone; "
        "everything else here is ignored.\n"
        if gitignore
        else ""
    )
    return (
        f"# Agent memory / handover\n\n"
        f"`{rel}/` is a framework-agnostic place for AI agents to write session "
        f"notes, handover documents, and scratch memory.\n\n"
        f"{status}\n\n"
        f"{keep_note}\n"
        f"To commit handover docs instead (shared memory), set "
        f"`gitignore = false` under `[handover]` in `.wingman/config.toml` and "
        f"remove the matching block from `.gitignore`. To relocate the folder, "
        f"set `dir` in that same section.\n"
    )


def _gitignore_block(folder: Path) -> str:
    rel = folder.as_posix()
    return (
        f"{_MARKER} scratch, not for publication. The folder and its README stay\n"
        f"# tracked; session/handover docs written here are ignored. Opt out\n"
        f"# (commit handover docs) via [handover] gitignore=false in\n"
        f"# .wingman/config.toml, then remove this block.\n"
        f"{rel}/*\n"
        f"!{rel}/README.md\n"
    )


def ensure_gitignored(
    folder: Path,
    dry_run: bool,
    *,
    marker: str = _MARKER,
    block: str | None = None,
) -> str:
    """Add (or confirm) a git-ignore block for ``folder`` in the repo .gitignore.

    ``marker`` and ``block`` let other ``.agent/`` artifacts (e.g. the tracking
    log) reuse this same idempotent .gitignore wiring with their own text.
    """
    path = repo_root() / GITIGNORE
    existing = path.read_text() if path.exists() else ""
    rel = folder.as_posix()
    if marker in existing or f"{rel}/*" in existing or f"{rel}/" in existing:
        return f"  .gitignore already ignores {rel}/"
    if dry_run:
        return f"  [dry-run] {'update' if existing else 'create'} .gitignore for {rel}/"
    text = existing
    if text and not text.endswith("\n"):
        text += "\n"
    if text:
        text += "\n"
    text += block if block is not None else _gitignore_block(folder)
    path.write_text(text)
    return f"  {'updated' if existing else 'created'} .gitignore for {rel}/"


def write_handover(dry_run: bool) -> str:
    """Create the agent memory/handover folder and wire up git-ignoring."""
    folder, gitignore = handover_settings()
    rel = folder.as_posix()
    lines: list[str] = []
    if dry_run:
        lines.append(f"  [dry-run] {rel}/ (+ README.md)")
    else:
        target = repo_root() / folder
        target.mkdir(parents=True, exist_ok=True)
        readme = target / "README.md"
        if not readme.exists():
            readme.write_text(_readme(folder, gitignore))
        lines.append(f"  wrote {rel}/README.md")
    if gitignore:
        lines.append(ensure_gitignored(folder, dry_run))
    else:
        lines.append(f"  [handover] gitignore=false — {rel}/ will be committed")
    return "\n".join(lines)
