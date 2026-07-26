# ADR-0001: track agent hand-offs as a SQLite log

- **Status:** Accepted
- **Date:** 2026-07-14
- **Authors:** @yannick-vinkesteijn

## Context and Problem Statement

Each phase of the fixed flow ends in a hand-off, but that state only lives in prose
under `.agent/memory/`, which can't be queried. How do we track phase hand-offs so
they're queryable and optionally shareable, without turning tara into a runtime or
adding a dependency?

## Considered Options

- A SQLite database written by the runtime.
- Parquet files (one per hand-off) queried with DuckDB.
- A `tara handoff` CLI that owns writes and queries.

## Decision Outcome

Chosen option: **a single SQLite database, `.agent/tracking/handoffs.db`**. `sqlite3`
ships with the Python standard library, so writing and reading the log needs no
project dependency; the SQLite file format is a stable, documented open standard; and
WAL mode lets concurrent sessions append safely. Tara creates the empty database
(idempotent schema), wires the `.gitignore` opt-out, and documents the schema; the
runtime appends one row per hand-off with a parameterised `INSERT`. Git-ignored by
default; opt in to commit via `[tracking] gitignore = false`.

This reverses an earlier draft that used Parquet files queried with DuckDB. Parquet
required DuckDB to touch the data (a dependency, even run ephemerally), produced one
small file per hand-off, and is an OLAP/columnar format ill-suited to appending single
rows. DuckDB is not lost: it reads the SQLite file directly (`sqlite_scan` / `ATTACH`)
whenever richer analytical queries are wanted.

### Consequences

- Good, because appending and querying use the standard library only — zero
  dependency, one file, indexed queries, and safe concurrent writes under WAL.
- Good, because the SQLite file is portable and any tool (including DuckDB, polars,
  pandas) can read it without an export step.
- Bad, because correctness still depends on the runtime following instructions rather
  than an enforced command, and a committed SQLite file is binary (opt-in only).
