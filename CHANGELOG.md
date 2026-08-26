# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-08-26

### Added

- Claude Code as a target tool: `CLAUDE.md` (a thin `@import` pointer to the Copilot instructions), plus `.claude/agents/`, `.claude/commands/`, and `.claude/skills/` generated from the `.github/` setup. `.mcp.json` is read by Claude Code natively, so it needs no translation.
- `tara tools` picks which agent tools this repo targets (menu, explicit list, or `--list`) and generates their files. The selection is stored as `tools` in `.tara/config.toml`.
- `tara init --tools` targets several tools at once, as a comma-separated list (e.g. `--tools claude,opencode`) or `all`. `--tool` continues to work.
- `tara skill sync` runs the package-skill sync on its own, without regenerating tool files.
- Claude-authored skills from `anthropics/skills`: `frontend-design` joins the `developing` theme, and a new `claude-api` theme is indexed against the `anthropic` package.

### Changed

- `tara sync` now regenerates the files for every tool in `.tara/config.toml` after syncing skills from installed packages, so newly synced skills reach opencode and Claude Code too.
- `.tara/config.toml` records a `tools` list instead of a single `tool`. Existing configs are migrated on read.
- `all` means every supported tool, so it now includes Claude Code. Repos configured with `tool = "all"` under 1.0.0 will have `CLAUDE.md` and `.claude/` generated on their next `tara sync`. Set `tools = ["copilot", "opencode"]` to keep the previous set.
- Frontmatter is parsed and written with PyYAML instead of a hand-rolled parser, so typed values (e.g. `tools: [read, search]`) survive round-tripping.
- The bundled base instructions gain branch naming (`<type>/<short-description>`), commit message format (imperative, 72-character subject), flaky-test guidance, and prose rules on full sentences and one-sentence-per-line wrapping.

### Deprecated

- `tara opencode sync` is superseded by `tara sync` (all configured tools) and `tara tools opencode` (one tool). It still works, but is hidden from help.

### Fixed

- `pyyaml` is now a declared runtime dependency. It was previously only present transitively via a dev dependency, so clean installs could fail.
- Relaxed the `pydantic` floor from `>=2.13.4` to `>=2.7` to avoid needless resolver conflicts.
- Ctrl-C in the interactive artifact picker now exits instead of silently confirming the current selection and continuing.

## [1.0.0] - 2026-07-27

Initial release of Tara, an agentic engineering toolkit that installs and maintains the guardrails your agent reads while you code (Copilot-first, with opencode supported).

### Added

- `tara init` to set up a repo: writes `.github/copilot-instructions.md` and `.mcp.json`, then adds selected instructions, skills, agents, and prompts.
- `.tara/config.toml` records the repo's setup state (the selected tool and stack) and holds optional `[standards]` tooling overrides and `[agents]` doc-store options; fresh configs self-document these.
- A git-tracked `.agents/` doc store (`plan/`, `design/`, `review/`, `memory/`), each with an `index.md`, for standardized working docs agents produce; set `[agents] gitignore` in `.tara/config.toml` to keep chosen subfolders local.
- `tara add` and `tara list` to manage bundled artifacts, and `tara sync` to pull in `SKILL.md` files shipped by installed packages (library-skills convention).
- `tara check`: a single gate running lint, format, type-check, tests, and a dependency audit, configurable per repo via `.tara/checks.toml`.
- `tara standards`: opinionated `pyproject.toml` tool tables and a `.pre-commit-config.yaml` baseline (ruff, ty, pytest, uv).
- `tara audit` to flag issues in MCP config and dependencies.
- `tara new` to scaffold ADRs, epics, stories, spikes, and other docs from templates.
- `tara skill`, `tara agent`, and `tara opencode` command groups.
- Bundled guardrails: base and Python instructions, a curated skill catalog, helper agents, and design, implement, refine, integrate, and review prompts.
