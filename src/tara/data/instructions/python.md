# Python Stack

Extends the base instructions with everyday Python coding conventions. Project
setup, dependency hygiene, and the tooling baseline live in the
`structuring-python-packages` skill and `tara standards`, not here.

## Code Style

- Format and lint with `ruff` (`uv run ruff check --fix && uv run ruff format`).
- Type-hint public APIs; check with `ty` (`uv run ty check .`), never mypy.
- Prefer `pathlib` over `os.path`. Log via `logging` (`getLogger(__name__)`), never `print()`.
- No bare `except`; catch specific exceptions.
- Put the exit condition in the `for`/`while`; don't steer a `while True` with scattered
  `break`/`continue`.

## Structure

- A class is an intentionally named abstraction over cohesive functions on shared data.
  Reach for one when functions cluster around shared state or shape, else plain
  functions. No inheritance or polymorphism required.
- Prefer stateless/immutable classes: build data once (constructor, frozen `dataclass`,
  or Pydantic `BaseModel`), methods return new values. Functional core, I/O at the edges.
- Standardise a variant family (plugins/adapters/backends) behind an `abc.ABC` or
  `typing.Protocol`. Keep inheritance shallow and contract-only; favour composition.
- No nested `def` unless a closure or decorator needs it; lift to module level or a
  `_`-prefixed method.
- One goal per function; if its name needs an "and", split it.
- Modular, reusable code: small generic utils and cohesive modules with clear
  interfaces, not copy-paste.
- Inject collaborators (clients, config) via constructor or arguments, not module
  singletons or globals.
- Standardise the approach to cross-cutting concerns but let each module own its own
  (its logger, its config), so you don't get modules that only look independent.

## Configuration

- Model settings and config with Pydantic (`BaseSettings` for env/app, `BaseModel` for
  structured), not dicts/argparse/dataclasses. Validate and coerce at the boundary.
- Parse, don't validate: build the typed model once at the boundary, then trust those
  types downstream.

## Errors

- Fail fast: check at the boundary and raise immediately, don't limp on with half-valid state.
- Raise specific exceptions from a small per-package hierarchy (own base `Error`); don't
  catch a blanket `Exception`.
- Never swallow errors or signal failure with `None`/sentinels; `raise ... from err` to
  keep the cause.

## Data

- Prefer `polars` over `pandas`; default to lazy `pl.LazyFrame`, collect only when needed.
- Unsure on the Polars API? Use the `polars` MCP server.

## Testing

- `pytest` (`uv run pytest`), test-first: failing test before the code.
- Structure tests GIVEN/WHEN/THEN; mirror layout (`src/foo/bar.py` -> `tests/foo/test_bar.py`);
  `parametrize` data cases; mock I/O so tests run offline.
