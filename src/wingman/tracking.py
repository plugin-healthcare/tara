"""Agent hand-off log: a queryable SQLite table under ``.agent/tracking/``.

The freeform ``.agent/memory/`` folder (see :mod:`wingman.handover`) holds prose
notes; this module adds a *structured* companion. Each phase of the fixed flow
(refine, design, implement, review, integrate) ends by appending one row to a
single SQLite database, ``.agent/tracking/handoffs.db`` (see ADR-0001).

SQLite is used deliberately: its file format is a stable, documented open
standard, ``sqlite3`` ships with the Python standard library (zero dependency),
and WAL mode lets concurrent sessions append safely. DuckDB is *not* required to
write the log; when you want its query ergonomics it reads the same SQLite file
directly (``sqlite_scan`` / ``ATTACH``).

Wingman only scaffolds the database (folder, empty schema, git-ignoring) and
documents how to use it; the GitHub Copilot runtime writes the rows. The log is
git-ignored by default (like ``.agent/memory/``); opt in to *commit and push* it
by setting ``gitignore = false`` under ``[tracking]`` in ``.wingman/config.toml``.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from wingman.core import repo_root
from wingman.handover import ensure_gitignored, load_config

DEFAULT_DIR = Path(".agent") / "tracking"
# The single SQLite database the runtime appends hand-off rows to.
HANDOFFS_DB = "handoffs.db"

# Marker identifying our tracking block in .gitignore (kept idempotent on re-run).
_MARKER = "# Wingman: agent hand-off log"

# The columns each hand-off row carries. Documented here, in the README, and in
# base.md so the runtime writes a consistent schema.
SCHEMA: tuple[tuple[str, str], ...] = (
    ("ts", "TEXT — when the hand-off happened (UTC, `datetime('now')`)"),
    ("session_id", "TEXT — id of the agent session"),
    ("branch", "TEXT — git branch the work is on"),
    ("phase", "TEXT — refine | design | implement | review | integrate"),
    ("summary", "TEXT — what was done in this phase"),
    ("next_step", "TEXT — what the next session/developer should pick up"),
    ("files", "TEXT — JSON array of paths touched in this phase"),
)

# Idempotent DDL wingman applies when scaffolding; the runtime only INSERTs.
_SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS handoffs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL DEFAULT (datetime('now')),
  session_id TEXT NOT NULL,
  branch TEXT,
  phase TEXT NOT NULL,
  summary TEXT NOT NULL,
  next_step TEXT,
  files TEXT
);
"""


def tracking_settings() -> tuple[Path, bool]:
    """``(folder, gitignore)`` from the ``[tracking]`` config, with defaults."""
    cfg = load_config().get("tracking", {})
    folder = Path(cfg.get("dir") or DEFAULT_DIR)
    gitignore = bool(cfg.get("gitignore", True))
    return folder, gitignore


def _init_db(path: Path) -> None:
    """Create the log DB with WAL mode and the idempotent hand-off schema."""
    con = sqlite3.connect(path)
    try:
        con.execute("PRAGMA journal_mode=WAL")
        con.executescript(_SCHEMA_SQL)
        con.commit()
    finally:
        con.close()


def append_command(db: Path) -> str:
    """The command the runtime runs to append a single hand-off row.

    Uses only the standard-library ``sqlite3`` module — no wingman dependency —
    and a parameterised INSERT so values never need escaping.
    """
    rel = db.as_posix()
    return (
        "uv run python - <<'PY'\n"
        "import json, sqlite3\n"
        f'con = sqlite3.connect("{rel}")\n'
        "con.execute(\n"
        '    "INSERT INTO handoffs '
        '(session_id, branch, phase, summary, next_step, files) "\n'
        '    "VALUES (?, ?, ?, ?, ?, ?)",\n'
        '    ("<session>", "<branch>", "<phase>", "<summary>", "<next_step>", '
        'json.dumps(["path/one.py"])),\n'
        ")\n"
        "con.commit()\n"
        "PY"
    )


def query_command(db: Path) -> str:
    """The command to read the whole log, newest first (standard library)."""
    rel = db.as_posix()
    return (
        "uv run python - <<'PY'\n"
        "import sqlite3\n"
        f'con = sqlite3.connect("{rel}")\n'
        "for row in con.execute(\n"
        '    "SELECT ts, phase, summary, next_step FROM handoffs ORDER BY ts DESC"\n'
        "):\n"
        "    print(row)\n"
        "PY"
    )


def duckdb_query_command(db: Path) -> str:
    """Optional: the same query via DuckDB, which reads the SQLite file directly."""
    rel = db.as_posix()
    sql = (
        "SELECT ts, phase, summary, next_step "
        f"FROM sqlite_scan('{rel}', 'handoffs') ORDER BY ts DESC"
    )
    sql = sql.replace('"', '\\"')
    inner = f'import duckdb; print(duckdb.sql(\\"{sql}\\"))'
    return f'uv run --with duckdb python -c "{inner}"'


def _schema_table() -> str:
    return "\n".join(f"- `{name}` — {desc}" for name, desc in SCHEMA)


def _readme(folder: Path, gitignore: bool) -> str:
    rel = folder.as_posix()
    db = folder / HANDOFFS_DB
    status = (
        f"The `{HANDOFFS_DB}` database is **git-ignored** by default, so the log "
        "stays local. Opt in to *commit and push* it by setting `[tracking] "
        "gitignore = false` in `.wingman/config.toml` and removing the matching "
        "block from `.gitignore`."
        if gitignore
        else f"The `{HANDOFFS_DB}` database is **committed** (`[tracking] gitignore "
        "= false`), so the log is shared through version control."
    )
    return (
        f"# Agent hand-off log\n\n"
        f"`{rel}/{HANDOFFS_DB}` is a structured, queryable record of the fixed "
        f"flow's phase hand-offs: one SQLite table, one row per hand-off. Wingman "
        f"creates the empty database; the runtime appends rows. See "
        f"`docs/decisions/0001-*.md`.\n\n"
        f"{status}\n\n"
        f"## Schema (`handoffs` table)\n\n"
        f"Each row carries:\n\n"
        f"{_schema_table()}\n\n"
        f"## Append a hand-off (runtime)\n\n"
        f"```sh\n{append_command(db)}\n```\n\n"
        f"## Query the log\n\n"
        f"```sh\n{query_command(db)}\n```\n\n"
        f"Prefer DuckDB's SQL ergonomics? It reads the SQLite file directly — no "
        f"export, and still no project dependency:\n\n"
        f"```sh\n{duckdb_query_command(db)}\n```\n\n"
        f"Nothing here is a wingman dependency: `sqlite3` is in the Python standard "
        f"library, and the SQLite file is the portable source of truth.\n"
    )


def _gitignore_block(folder: Path) -> str:
    rel = folder.as_posix()
    return (
        f"{_MARKER}: local by default. The folder and its README stay tracked;\n"
        f"# the SQLite database (and its WAL side-files) are ignored. Opt out\n"
        f"# (commit and push the log) via [tracking] gitignore=false in\n"
        f"# .wingman/config.toml, then remove this block.\n"
        f"{rel}/{HANDOFFS_DB}\n"
        f"{rel}/{HANDOFFS_DB}-wal\n"
        f"{rel}/{HANDOFFS_DB}-shm\n"
        f"!{rel}/README.md\n"
    )


def write_tracking(dry_run: bool) -> str:
    """Create the hand-off log database and wire up git-ignoring."""
    folder, gitignore = tracking_settings()
    rel = folder.as_posix()
    lines: list[str] = []
    if dry_run:
        lines.append(f"  [dry-run] {rel}/{HANDOFFS_DB} (+ README.md)")
    else:
        target = repo_root() / folder
        target.mkdir(parents=True, exist_ok=True)
        _init_db(target / HANDOFFS_DB)
        readme = target / "README.md"
        if not readme.exists():
            readme.write_text(_readme(folder, gitignore))
        lines.append(f"  wrote {rel}/{HANDOFFS_DB} and {rel}/README.md")
    if gitignore:
        lines.append(
            ensure_gitignored(
                folder, dry_run, marker=_MARKER, block=_gitignore_block(folder)
            )
        )
    else:
        lines.append(f"  [tracking] gitignore=false — {rel}/ will be committed")
    return "\n".join(lines)
