# ADR-0001: track agent hand-offs as a Parquet ledger queried with DuckDB

- **Status:** Accepted
- **Date:** 2026-07-13
- **Authors:** @yannick-vinkesteijn

## Context and Problem Statement

Each phase of the fixed flow ends in a hand-off, but that state only lives in prose
under `.agent/memory/`, which can't be queried. How do we track phase hand-offs so
they're queryable and optionally shareable, without turning wingman into a runtime or
adding a dependency?

## Considered Options

- Parquet ledger written by the runtime, queried with DuckDB.
- A `wingman handoff` CLI that owns writes and queries.
- A SQLite database.

## Decision Outcome

Chosen option: **Parquet ledger, queried with DuckDB**. The Parquet files are a
portable, pushable source of truth any tool can read, DuckDB gives efficient SQL over
the whole set, and it needs no wingman dependency — the runtime runs it ephemerally
(`uv run --with duckdb`). Wingman only scaffolds `.agent/tracking/`, wires the
`.gitignore` opt-out, and documents the schema; the runtime writes one Parquet file
per hand-off. Git-ignored by default; opt in to commit via `[tracking] gitignore =
false`.

### Consequences

- Good, because the ledger is queryable with plain SQL and portable across
  polars/pandas/DuckDB, with no wingman dependency or new subcommand.
- Bad, because one file per hand-off produces many small Parquet files over time, and
  correctness depends on the runtime following instructions rather than an enforced
  command.
