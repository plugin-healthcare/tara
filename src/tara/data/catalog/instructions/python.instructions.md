---
applyTo: "**/*.py"
description: "Python file conventions with correct and wrong examples: imports, typing, settings, errors, Polars, tests."
---

# Python file conventions

The prose version of these rules lives in `.github/copilot-instructions.md`; project
setup and the tooling baseline live in the `structuring-python-packages` skill. This
file is the file-scoped version with the correct and wrong shapes side by side.

## Imports

- Group order: stdlib, third-party, first-party (your own package), local.
- No relative imports anywhere. Always absolute.
- Use a `TYPE_CHECKING` guard for imports only needed at type-check time.
- On Python 3.12+, don't add `from __future__ import annotations` to new modules.
  Native type hints already work; the import is only for genuine forward references.

## Every public symbol has a docstring

```python
# correct
def table_ref(schema: str, table: str) -> str:
    """Derive a fully-qualified table reference.

    Args:
        schema: Schema name, for example ``raw``.
        table: Table name, for example ``orders``.

    Returns:
        Reference like ``warehouse.raw.orders``.
    """

# wrong: no docstring, so the contract lives only in the caller's head
def table_ref(schema: str, table: str) -> str:
    ...
```

## Signatures fully annotated, native syntax only

```python
# correct
def create_connection(
    settings: Settings,
    backend: StorageBackend | None = None,
) -> Connection:

# wrong: unannotated
def create_connection(settings, backend=None):

# wrong: legacy typing module
def create_connection(
    settings: Settings,
    backend: Optional[StorageBackend] = None,
) -> Connection:
```

## Small, focused functions

```python
# correct: one responsibility, named for it
def ensure_schema(conn: Connection, schema: str) -> None:
    """Create the schema if it does not already exist."""
    conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

# wrong: connects, installs, creates, and writes, so its name needs an "and"
def setup_and_write(settings, frame, schema, table):
    ...
```

## Settings through Pydantic

```python
# correct
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env")
    host: str = Field(default="localhost")
    password: str  # required, no default

# wrong: reading the environment ad hoc, no validation, no single source of truth
host = os.environ.get("APP_HOST", "localhost")
```

## Logging

```python
# correct
import logging

logger = logging.getLogger(__name__)
logger.info("Processing %d rows.", count)

# wrong
print(f"Processing {count} rows")
```

## Errors

```python
# correct: specific, and the cause survives
try:
    config = Settings()
except ValidationError as err:
    raise ConfigError("invalid settings") from err

# wrong: swallows every failure and returns a sentinel the caller must remember
try:
    config = Settings()
except Exception:
    return None
```

## SQL safety

```python
# acceptable: the identifier comes from validated internal input
conn.execute(f"SELECT * FROM {ref}")  # noqa: S608

# never: a user-controlled string interpolated into SQL
conn.execute(f"SELECT * FROM {user_input}")
```

## Classes and layout

- Use a class to group cohesive functions over shared data, not to hold mutable state.
- Return values instead of mutating arguments.
- No logic in `__init__.py`; imports and a module docstring only.
- Shared helpers live in a package-level `utils` module, not inside a submodule that
  happens to have needed them first.

## Polars

- Stay lazy. Use `pl.LazyFrame` and don't call `.collect()` until the final step or
  until an operation strictly requires it.
- Don't take or return `DataFrame` where `LazyFrame` works.
- Don't read large files into memory. Use `scan_parquet`, `scan_csv`, and `sink_parquet`
  for out-of-core work.
- Don't loop over rows or columns. Batch into a single `with_columns` or `select`.
- Don't pull rows or cells into Python lists. The round trip out of Arrow is expensive
  and unbounded when no limit is set.

## Testing

- `pytest`, test-first: the failing test comes before the code.
- Write tests as plain functions, not methods on a class. Use fixtures for shared setup.
- Test files mirror the source layout (`src/foo/bar.py` gives `tests/foo/test_bar.py`).
- Test your own code, not the behaviour of an external package.
