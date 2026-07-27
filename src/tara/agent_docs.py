"""Framework-agnostic agent doc store under ``.agent/``.

``tara init`` scaffolds a small, git-ignored doc store where any agent runtime
can keep the standardized working docs it produces during the fixed flow:

- ``.agent/memory/``   -- freeform session notes and handover scratch
- ``.agent/planning/`` -- plans and execution plans
- ``.agent/reviews/``  -- code and maturity reviews

Docs are named ``YYYY-MM-DD-<slug>.md`` and each folder keeps an ``index.md``
(one row per doc, newest first) so the next session can scan it quickly instead
of opening every file. The whole store is git-ignored: it is local working
knowledge, not published artifacts, and never a place for secrets.

Optimizing knowledge retention (a structured, queryable store) is deliberately
deferred; this flat, greppable layout is the interim.
"""

from __future__ import annotations

from pathlib import Path

from tara.core import repo_root

GITIGNORE = Path(".gitignore")
DOC_STORE = Path(".agent")

# Substring identifying our block in an existing .gitignore, so re-running init
# stays idempotent even if the user tweaks the surrounding comments.
_MARKER = "# Tara: agent doc store"

# Filename convention for docs in the store (date + short slug).
FILENAME = "YYYY-MM-DD-<slug>.md"

# Typed folders in the store, each with a one-line purpose used to seed its index.
FOLDERS: tuple[tuple[str, str], ...] = (
    ("memory", "Freeform session notes and handover scratch."),
    ("planning", "Plans and execution plans."),
    ("reviews", "Code and maturity reviews."),
)


def _index(name: str, purpose: str) -> str:
    """Seed content for a folder's ``index.md`` (a table the runtime appends to)."""
    return (
        f"# {name.capitalize()} index\n\n"
        f"{purpose} One row per doc, newest first. Name each file `{FILENAME}`.\n\n"
        f"| Date | File | Summary |\n"
        f"| ---- | ---- | ------- |\n"
    )


def ensure_gitignored(dry_run: bool) -> str:
    """Add (or confirm) a git-ignore block for the ``.agent/`` store."""
    rel = DOC_STORE.as_posix()
    path = repo_root() / GITIGNORE
    existing = path.read_text() if path.exists() else ""
    if _MARKER in existing or f"{rel}/" in existing:
        return f"  .gitignore already ignores {rel}/"
    if dry_run:
        return f"  [dry-run] {'update' if existing else 'create'} .gitignore for {rel}/"
    block = (
        f"{_MARKER}: local working knowledge (session notes, plans, reviews),\n"
        f"# not published artifacts. Never write secrets here.\n"
        f"{rel}/\n"
    )
    text = existing
    if text and not text.endswith("\n"):
        text += "\n"
    if text:
        text += "\n"
    text += block
    path.write_text(text)
    return f"  {'updated' if existing else 'created'} .gitignore for {rel}/"


def write_agent_docs(dry_run: bool) -> str:
    """Scaffold the ``.agent/`` doc store: typed folders each with an index."""
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
    lines.append(ensure_gitignored(dry_run))
    return "\n".join(lines)
