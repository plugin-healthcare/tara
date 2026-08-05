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

# Header marking our block in .gitignore. We look for the marker before writing
# so the header line is emitted at most once, even when several subpaths are
# ignored in one run or init is re-run over an existing block.
_MARKER = "# Tara: agent doc store"
_MARKER_LINE = (
    f"{_MARKER}: local scratch, not published artifacts. Never write secrets here."
)

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


def _relpath(sub: str) -> str:
    """Normalize a store subpath to a posix path under ``.agents/``.

    ``sub`` comes from ``[agents] gitignore`` and must point *inside* the store:
    absolute paths, ``..`` traversal, and empty values are rejected so a stray
    config value can never add ``.gitignore`` rules for files outside ``.agents/``.
    """
    p = Path(sub)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError(f"invalid [agents] gitignore subpath: {sub!r}")
    return (DOC_STORE / p).as_posix()


def ensure_gitignored(rels: list[str], dry_run: bool) -> list[str]:
    """Git-ignore ``rels`` (posix paths under the store) under a single block.

    ``rels`` are normalized store paths (see :func:`_relpath`). Idempotent: paths
    already ignored are left untouched and the marker header is written at most
    once. Returns one status line per path, plus a summary line when new entries
    are added.
    """
    path = repo_root() / GITIGNORE
    existing = path.read_text() if path.exists() else ""
    present = set(existing.splitlines())
    msgs = [
        f"  .gitignore already ignores {rel}/" for rel in rels if f"{rel}/" in present
    ]
    missing = [rel for rel in rels if f"{rel}/" not in present]
    if not missing:
        return msgs
    listed = ", ".join(f"{rel}/" for rel in missing)
    if dry_run:
        verb = "update" if existing else "create"
        return [*msgs, f"  [dry-run] {verb} .gitignore for {listed}"]
    new_lines = [f"{rel}/" for rel in missing]
    if _MARKER not in existing:
        new_lines.insert(0, _MARKER_LINE)
    text = existing.rstrip("\n")
    if text:
        text += "\n" if _MARKER in existing else "\n\n"
    text += "\n".join(new_lines) + "\n"
    path.write_text(text)
    return [*msgs, f"  {'updated' if existing else 'created'} .gitignore for {listed}"]


def write_agent_docs(dry_run: bool, gitignore: list[str] | None = None) -> str:
    """Scaffold the ``.agents/`` doc store: typed folders each with an index.

    The store is tracked by default. ``gitignore`` is a list of subpaths under
    ``.agents/`` (from ``[agents] gitignore`` in ``.tara/config.toml``) to keep
    local instead; each listed subpath is added to ``.gitignore``. Subpaths are
    validated up front, so an invalid value fails before anything is written.
    """
    rels = [_relpath(sub) for sub in gitignore or []]
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
    lines.extend(ensure_gitignored(rels, dry_run))
    return "\n".join(lines)
