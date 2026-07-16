# Python Stack

Additional instructions for Python projects. Applied on top of the base instructions.

## Package Management

- Use `uv` for all dependency and environment management (`uv add`, `uv run`, `uv sync`).
- Never use `pip install` directly in a project with a `pyproject.toml`.
- Never use hatchling or setuptools: the build backend is `uv_build`
  (`build-backend = "uv_build"`).
- Pin Python version in `.python-version`.
- Hold back freshly published releases with `[tool.uv] exclude-newer = "14 days"`
  so a just-compromised version cannot slip in. Requires uv >= 0.11.
- Audit dependencies with `uv audit --preview-features audit-command`: it reports
  known CVEs and adverse project statuses (PEP 792: archived / deprecated /
  quarantined). Requires uv >= 0.11.
- Every dependency must declare a version constraint (e.g. `httpx>=0.27`), never a
  bare package name. `tara standards` flags unpinned dependencies.

## Code Style

- Formatter and linter: `ruff`. Run `uv run ruff check --fix && uv run ruff format`.
- The ruff baseline is `select = ["ALL"]` with a curated ignore list, line-length
  120, and google docstrings. Run `tara standards --show` for the canonical config.
- Type hints on all public functions and methods. Type-check with `ty`
  (`uv run ty check .`); tara always uses `ty`, not mypy.
- Prefer `pathlib.Path` over `os.path`.
- No bare `except:`; always catch specific exceptions.
- Run the pre-commit hooks (`uv run pre-commit install` once); they run ruff and ty.

## Data

- Prefer `polars` over `pandas` for all tabular data work.
- Use lazy evaluation (`pl.LazyFrame`) by default; collect only when needed.
- When in doubt about Polars API or syntax, use the `polars` MCP server.

## Testing

- Framework: `pytest`. Run with `uv run pytest`.
- Test-first: write the failing test before the implementation.
- Structure each test as GIVEN (arrange the conditions), WHEN (run the behaviour),
  THEN (assert the result).
- Test files mirror source layout: `src/foo/bar.py` → `tests/foo/test_bar.py`.
- Use `pytest.mark.parametrize` for data-driven cases.
- Mock external I/O; tests must be runnable offline.

## Project Layout

```
src/<package>/    ← application code
tests/            ← mirrors src/ layout
pyproject.toml    ← single source of truth for metadata + deps
.python-version   ← pinned Python version for uv
```
