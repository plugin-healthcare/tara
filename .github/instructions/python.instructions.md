---
applyTo: "**/*.py"
---

# Python file conventions

- Use native type hints (`str | None`, `list[int]`); annotate public functions.
- Docstrings: follow the `pyproject.toml` convention (google by default) -- keep them
  short and to the point: purpose, key decisions, and how it works, plus
  args/returns/raises. Defer internal detail to a comment on its own line above the
  code (never inline/trailing).
- Prefer `pathlib.Path` over `os.path`. No bare `except:` — catch specific exceptions.
- Use `logging`, never `print()`, in library/application code.
- Tabular data: prefer `polars` (lazy `pl.LazyFrame`) over `pandas`.
- Run `uv run ruff check --fix && uv run ruff format` before considering a change done.
