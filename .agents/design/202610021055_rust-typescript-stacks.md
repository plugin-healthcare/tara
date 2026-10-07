# Contributed stacks such as Rust and TypeScript: draft for review

Date: 2026-10-02
Status: posted as #43 with sub-issues #44 to #48, all in 2.x.
Request: Daniel would like Rust and TypeScript added next to Python.
Revised: 2026-10-04, after the scope decision below.

## Scope decision

Python is the only stack that Tara's maintainers set up in full, with standards, `uv` dev tools, and dependency triggers.
Other stacks are contributed through the registry and maintained by their contributor.
Tara only provides a small entry point that installs a contributed stack's files, without code for each stack.
Skills for any language are already covered by draft E, because users pick them from external sources themselves.

## How a stack works today

A stack is mostly a set of data files, looked up by name.

| File | Used by | Purpose |
| ---- | ------- | ------- |
| `data/instructions/<stack>.md` | `core.assemble_instructions` | Appended to `.github/copilot-instructions.md`. |
| `data/mcp/<stack>.json` | `core.merged_servers` | Extra MCP servers in `.mcp.json`. |
| `data/checks/<stack>.toml` | `check.load_checks` | Commands for `tara check`. |
| `data/standards/<stack>/` | `standards.py` | `pre-commit-config.yaml` and `pyproject-tools.toml`. |

`core.available_stacks()` discovers stacks from the `instructions/` and `mcp/` folders, so a new stack is partly a data change.

## Where Python is hard-coded

1. `tara init` runs the standards and dev-tool steps only when the stack is `python` (`src/tara/cli.py:283-286`).
2. `standards.py` compares against `pyproject.toml` only. Rust uses `Cargo.toml`, `rustfmt.toml`, and `clippy.toml`, and TypeScript uses `package.json`, `tsconfig.json`, and a linter config.
3. `tara sync` reads direct dependencies from `pyproject.toml` only (`src/tara/sync.py:90-100`), so package-triggered skills and instructions never fire for `Cargo.toml` or `package.json`.
4. `packages` in `skills/index.toml` and `catalog/instructions/index.toml` holds PyPI names without an ecosystem, so `duckdb` cannot mean both the PyPI package and the crate.
5. The config holds one `stack` string (`src/tara/config.py:123`). Repositories that mix Python with a Rust extension (PyO3, maturin) or a TypeScript frontend cannot select both.

## Stack contract

A contributed stack is a folder in the registry, `stacks/<name>/`, with these files.

| File | Required | What Tara does with it |
| ---- | -------- | ---------------------- |
| `stack.toml` | Yes | Name, description, and owner. Tara shows the owner in `tara init`, so it is clear who maintains the stack. |
| `<name>.instructions.md` | Yes | Installed as a scoped instruction file with its own `applyTo`, such as `**/*.rs`. |
| `checks.toml` | No | Commands for `tara check`, in the format Python uses today. |
| `pre-commit.yaml` | No | Hooks that `tara init` offers to add to `.pre-commit-config.yaml`. |
| `mcp.json` | No | Extra MCP servers. |

Tara does not compare manifests such as `Cargo.toml` or `package.json`, does not install toolchains, and does not read their dependencies.
A contributor who wants more setup help documents it in the stack's instructions or a runbook.

## Code changes

1. Support a list of stacks in the config, so a Python repository with a Rust extension or a TypeScript frontend can select both.
   A legacy `stack = "python"` reads as `stacks = ["python"]` without a warning.
2. Install any stack that follows the contract, without stack-specific code.
   The Python-only steps in `tara init` (`src/tara/cli.py:283-286`) stay Python-only.
3. Move the language-neutral testing rules from `python.md` to `base.md`, so other stacks get them without the `uv` and `pytest` setup.

## Tooling baselines

The contributor of each stack chooses its tools.
The table below is only a starting point for Daniel.

| Category | Python (current) | Rust | TypeScript |
| -------- | ---------------- | ---- | ---------- |
| Format | `ruff format` | `cargo fmt --check` | Biome or Prettier |
| Lint | `ruff check` | `cargo clippy --all-targets -- -D warnings` | Biome or ESLint |
| Types | `ty check` | Covered by the compiler | `tsc --noEmit` with `strict` |
| Test | `pytest` | `cargo test` | `vitest run` |

## Relation to other work

- The remote catalog registry (`.agents/design/202610021040_remote-catalog-registry.md`) would hold the stack content, so new stacks would not need a Tara release.
- The token cost issue (#41) applies to stack instructions too.

## Suggested split

| Issue | Change | Owner |
| ----- | ------ | ----- |
| #43 | Rewrite as "Let contributors add stacks through the registry". | Yannick |
| #44 | Keep: a list of stacks in the config. | Tara maintainers |
| #45 | Close as not planned. Users pick skills for any language themselves (draft E). | |
| #46 | Rewrite as "Install a contributed stack from its folder". No manifest comparisons. | Tara maintainers |
| new | Move the language-neutral testing rules to `base.md`. | Tara maintainers |
| #47, #48 | Keep as data-only stack folders in the registry, maintained by the contributor. | Daniel, if he agrees |

## Open questions

1. Does Daniel take ownership of the Rust and TypeScript stacks?
2. Does the contract need anything else before the first contributed stack, or should it start with instructions and checks only?
3. Decided: all stack work is 2.x, because stack content lives in the registry and does not decide the package version.
