---
name: structuring-python-packages
description: "Use when creating, scaffolding, or restructuring a Python package or library: setting up the src-layout, a pyproject.toml with the uv_build backend, tests, and a runnable example. Applies Tara's Python conventions on top of uv init."
---

# Structuring Python packages

The canonical layout for a distributable Python package or library: a src-layout,
the `uv_build` backend, and tests kept out of the importable package. Works whether
you are starting from an empty repo or aligning an existing one.

## Create it with uv

In an empty (or fresh) repo, let uv do the scaffolding, then arrange the rest:

```
uv init --lib --build-backend uv <name>
```

This produces exactly the layout below: a src-layout package with `uv_build` wired
in `pyproject.toml` and a `py.typed` marker.

## Canonical layout

```
<name>/
  pyproject.toml          # project metadata + [build-system] uv_build
  README.md
  .python-version
  src/
    <package>/
      __init__.py
      py.typed            # ship type information
  tests/
    test_<something>.py
  examples/               # a small runnable example of the package in use
```

- **src-layout**: the package lives under `src/`, so tests run against the installed
  package, not the working directory. This catches missing-file and packaging bugs.
- **`uv_build` backend**: `[build-system]` uses `requires = ["uv_build..."]` and
  `build-backend = "uv_build"`. Do not swap it for setuptools/hatchling unless there
  is a concrete reason.
- **`py.typed`**: keep it so downstream consumers get your type hints.

## Conventions

- Follow the repo's Python conventions in `.github/copilot-instructions.md` (Python Stack).
- Add dependencies with `uv add` (never `pip install`); pin Python in `.python-version`.
- Tests go in top-level `tests/`, never inside `src/`. Run with `uv run pytest`.
- Lint and format before done: `uv run ruff check --fix && uv run ruff format`.
- Type-check with `ty`: `uv run ty check .`. Tara always uses `ty`.

## Opinionated tooling standard

`uv init` writes no tool config, so Tara ships one. Run `tara standards`
to see, per category, how a repo differs from the baseline (`ruff`, `pytest`,
`ty`, `uv`, plus pre-commit). It is non-destructive: it writes
`.pre-commit-config.yaml` only when absent and never overwrites or edits an
existing config that differs, it only warns.

To apply the tool config, append Tara's canonical block to the generated
`pyproject.toml` (this is what `tara check` reads):

```
tara standards --show >> pyproject.toml
```

`tara standards --show` is the canonical config (ruff, ty, pytest, uv), so this
skill does not restate it. The `tara check` gate also runs `uv audit` for CVEs and
PEP 792 project statuses (archived / deprecated / quarantined). `uv audit` and the
`exclude-newer` cooldown need uv >= 0.11; every dependency must carry a version constraint.

Enable the hooks once with `uv run pre-commit install`.

## Every increment ships something runnable

Add a small, working `examples/` script (or a documented public entrypoint) that
demonstrates the package, plus tests that cover the new behavior. An increment
without a way to run and verify it is not done.

Never commit; the developer reviews and commits. You scaffold and arrange the files.
