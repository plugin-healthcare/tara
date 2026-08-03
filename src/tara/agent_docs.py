"""Framework-agnostic agent doc store under ``.agents/``.

``tara init`` scaffolds a small doc store where any agent runtime can keep the
standardized working docs it produces during the fixed flow:

- ``.agents/plan/``    -- plans and execution plans
- ``.agents/design/``  -- design docs and technical drafts
- ``.agents/review/``  -- code and maturity reviews
- ``.agents/memory/``  -- freeform session notes and handover scratch

Docs are named ``YYYYMMDDHHMM_<short-descriptive-title>.md`` (no spaces) and each
folder keeps an ``index.md``
(one row per doc, newest first) so the next session can scan it quickly instead
of opening every file. The store is committed by default as shared team
knowledge; set ``[agents] gitignore`` in ``.tara/config.toml`` to keep chosen
subfolders (for example ``memory``) local. Never write secrets anywhere here.

ADRs live in ``docs/decisions/`` and stories/epics in your tracker or board,
not here; this store holds working plans, designs, reviews, and handover notes.

Optimizing knowledge retention (a structured, queryable store) is deliberately
deferred; this flat, greppable layout is the interim.
"""

from __future__ import annotations

from pathlib import Path

from tara.core import repo_root

DOC_STORE = Path(".agents")
GITIGNORE = Path(".gitignore")

# Substring identifying our block in an existing .gitignore, so re-running init
# stays idempotent even if the user tweaks the surrounding comments.
_MARKER = "# Tara: agent doc store"

# Filename convention for docs in the store: timestamp to the minute (so files
# sort by time and rarely collide across parallel sessions) + a hyphenated title.
FILENAME = "YYYYMMDDHHMM_<short-descriptive-title>.md"

# Typed folders in the store, each with a one-line purpose used to seed its index.
FOLDERS: tuple[tuple[str, str], ...] = (
    ("plan", "Plans and execution plans."),
    ("design", "Design docs; finalized ADRs live in docs/decisions/."),
    ("review", "Code and maturity reviews."),
    ("memory", "Freeform session notes and handover scratch."),
)


def _index(name: str, purpose: str) -> str:
    """Seed content for a folder's ``index.md`` (a table the runtime appends to)."""
    return (
        f"# {name.capitalize()} index\n\n"
        f"{purpose} One row per doc, newest first. Name each file `{FILENAME}`.\n\n"
        f"| Date | File | Summary |\n"
        f"| ---- | ---- | ------- |\n"
    )


def ensure_gitignored(rel: str, dry_run: bool) -> str:
    """Add (or confirm) a git-ignore entry for ``rel`` (a path under the store)."""
    path = repo_root() / GITIGNORE
    existing = path.read_text() if path.exists() else ""
    if f"{rel}/" in existing.splitlines():
        return f"  .gitignore already ignores {rel}/"
    if dry_run:
        return f"  [dry-run] {'update' if existing else 'create'} .gitignore for {rel}/"
    block = (
        f"{_MARKER}: local scratch, not published artifacts. "
        f"Never write secrets here.\n"
        f"{rel}/\n"
    )
    text = existing.rstrip("\n")
    if text:
        text += "\n\n"
    text += block
    path.write_text(text)
    return f"  {'updated' if existing else 'created'} .gitignore for {rel}/"


def write_agent_docs(dry_run: bool, gitignore: list[str] | None = None) -> str:
    """Scaffold the ``.agents/`` doc store: typed folders each with an index.

    The store is tracked by default. ``gitignore`` is a list of subpaths under
    ``.agents/`` (from ``[agents] gitignore`` in ``.tara/config.toml``) to keep
    local instead; each listed subpath is added to ``.gitignore``.
    """
    lines: list[str] = []
    for name, purpose in FOLDERS:
        folder = DOC_STORE / name
        frel = folder.as_posix()
        if dry_run:
            lines.append(f"  [dry-run] {frel}/index.md")
            continue
        target = repo_root() / folder
        target.mkdir(parents=True, exist_ok=True)
        index = target / "index.md"
        if not index.exists():
            index.write_text(_index(name, purpose))
        lines.append(f"  wrote {frel}/index.md")
    for sub in gitignore or []:
        rel = (DOC_STORE / sub).as_posix()
        lines.append(ensure_gitignored(rel, dry_run))
    return "\n".join(lines)
