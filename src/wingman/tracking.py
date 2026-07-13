"""Agent hand-off ledger: a queryable Parquet log under ``.agent/tracking/``.

The freeform ``.agent/memory/`` folder (see :mod:`wingman.handover`) holds prose
notes; this module adds a *structured* companion. Each phase of the fixed flow
(refine, design, implement, review, integrate) ends by appending one small
Parquet file per hand-off, which DuckDB can query across the whole dataset
without any of it becoming a wingman dependency (see ADR-0001).

Wingman only scaffolds the folder, documents the schema, and wires git-ignoring;
the GitHub Copilot runtime writes the rows. Its contents are git-ignored by
default (like ``.agent/memory/``); opt in to *commit and push* the Parquet by
setting ``gitignore = false`` under ``[tracking]`` in ``.wingman/config.toml``.
"""

from __future__ import annotations

from pathlib import Path

from wingman.core import repo_root
from wingman.handover import ensure_gitignored, load_config

DEFAULT_DIR = Path(".agent") / "tracking"
# Sub-directory the runtime writes one Parquet file per hand-off into.
HANDOFFS = "handoffs"

# Marker identifying our tracking block in .gitignore (kept idempotent on re-run).
_MARKER = "# Wingman: agent hand-off ledger"

# The columns each hand-off Parquet row carries. Documented here, in the README,
# and in base.md so the runtime writes a consistent schema.
SCHEMA: tuple[tuple[str, str], ...] = (
    ("ts", "TIMESTAMP — when the hand-off happened"),
    ("session_id", "VARCHAR — id of the agent session"),
    ("branch", "VARCHAR — git branch the work is on"),
    ("phase", "VARCHAR — refine | design | implement | review | integrate"),
    ("summary", "VARCHAR — what was done in this phase"),
    ("next_step", "VARCHAR — what the next session/developer should pick up"),
    ("files", "VARCHAR[] — paths touched in this phase"),
)


def tracking_settings() -> tuple[Path, bool]:
    """``(folder, gitignore)`` from the ``[tracking]`` config, with defaults."""
    cfg = load_config().get("tracking", {})
    folder = Path(cfg.get("dir") or DEFAULT_DIR)
    gitignore = bool(cfg.get("gitignore", True))
    return folder, gitignore


def _duckdb_python(sql: str, *, show: bool) -> str:
    """Wrap a SQL statement in the runtime's ephemeral-DuckDB python invocation.

    DuckDB is run via ``uv run --with duckdb`` so it never becomes a project
    dependency; the ``duckdb`` PyPI package is a library, not a CLI.
    """
    call = f'print(duckdb.sql("{sql}"))' if show else f'duckdb.sql("{sql}")'
    call = call.replace('"', '\\"')
    return f'uv run --with duckdb python -c "import duckdb; {call}"'


def append_command(folder: Path) -> str:
    """The command the runtime runs to append a single hand-off row.

    Each call writes one uniquely-named Parquet file (substitute a real
    ``<ts>-<session>-<phase>`` slug), so the ledger is append-only with no
    read-modify-rewrite and no write races.
    """
    rel = folder.as_posix()
    sql = (
        "COPY (SELECT now() AS ts, '<session>' AS session_id, "
        "'<branch>' AS branch, '<phase>' AS phase, '<summary>' AS summary, "
        "'<next_step>' AS next_step, ['path/one.py'] AS files) "
        f"TO '{rel}/{HANDOFFS}/<ts>-<session>-<phase>.parquet' (FORMAT parquet)"
    )
    return _duckdb_python(sql, show=False)


def query_command(folder: Path) -> str:
    """The command to read the whole ledger, newest first."""
    rel = folder.as_posix()
    sql = (
        "SELECT ts, phase, summary, next_step "
        f"FROM read_parquet('{rel}/{HANDOFFS}/**/*.parquet') ORDER BY ts DESC"
    )
    return _duckdb_python(sql, show=True)


def _schema_table() -> str:
    return "\n".join(f"- `{name}` — {desc}" for name, desc in SCHEMA)


def _readme(folder: Path, gitignore: bool) -> str:
    rel = folder.as_posix()
    status = (
        "Its Parquet contents are **git-ignored** by default, so the ledger stays "
        "local. Opt in to *commit and push* it by setting `[tracking] gitignore = "
        "false` in `.wingman/config.toml` and removing the matching block from "
        "`.gitignore`."
        if gitignore
        else "Its Parquet contents are **committed** (`[tracking] gitignore = false`), "
        "so the ledger is shared through version control."
    )
    return (
        f"# Agent hand-off ledger\n\n"
        f"`{rel}/{HANDOFFS}/` is a structured, queryable log of the fixed flow's "
        f"phase hand-offs. Each hand-off is written as one small Parquet file; "
        f"DuckDB queries the whole dataset. See `docs/decisions/0001-*.md`.\n\n"
        f"{status}\n\n"
        f"## Schema\n\n"
        f"Each row carries:\n\n"
        f"{_schema_table()}\n\n"
        f"## Append a hand-off (runtime)\n\n"
        f"```sh\n{append_command(folder)}\n```\n\n"
        f"## Query the ledger\n\n"
        f"```sh\n{query_command(folder)}\n```\n\n"
        f"Nothing here is a wingman dependency: DuckDB runs ephemerally via "
        f"`uv run --with duckdb`, and the Parquet files are the portable source "
        f"of truth.\n"
    )


def _gitignore_block(folder: Path) -> str:
    rel = folder.as_posix()
    return (
        f"{_MARKER}: local by default. The folder and its README stay tracked;\n"
        f"# hand-off Parquet files are ignored. Opt out (commit and push the\n"
        f"# ledger) via [tracking] gitignore=false in .wingman/config.toml, then\n"
        f"# remove this block.\n"
        f"{rel}/{HANDOFFS}/\n"
        f"!{rel}/README.md\n"
    )


def write_tracking(dry_run: bool) -> str:
    """Create the hand-off ledger folder and wire up git-ignoring."""
    folder, gitignore = tracking_settings()
    rel = folder.as_posix()
    lines: list[str] = []
    if dry_run:
        lines.append(f"  [dry-run] {rel}/{HANDOFFS}/ (+ README.md)")
    else:
        target = repo_root() / folder / HANDOFFS
        target.mkdir(parents=True, exist_ok=True)
        readme = repo_root() / folder / "README.md"
        if not readme.exists():
            readme.write_text(_readme(folder, gitignore))
        lines.append(f"  wrote {rel}/README.md")
    if gitignore:
        lines.append(
            ensure_gitignored(
                folder, dry_run, marker=_MARKER, block=_gitignore_block(folder)
            )
        )
    else:
        lines.append(f"  [tracking] gitignore=false — {rel}/ will be committed")
    return "\n".join(lines)
