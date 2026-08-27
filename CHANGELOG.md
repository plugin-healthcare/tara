# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-08-26

### Added

- Claude Code as a target tool: `CLAUDE.md` (a thin `@import` pointer to the Copilot instructions), plus `.claude/agents/`, `.claude/commands/`, and `.claude/skills/` generated from the `.github/` setup. `.mcp.json` is read by Claude Code natively, so it needs no translation.
- `tara integrations` selects the coding-agent products Tara targets and generates their files. The selection is stored as explicit names under `integrations` in `.tara/config.toml`.
- `tara init --integrations` accepts a comma-separated list or `all`. Legacy `--tool`, `--tools`, and `tara tools` forms continue to work as deprecated aliases.
- `tara skill sync` runs the package-skill sync on its own, without regenerating tool files.
- Conventional CLI aliases: `-h` for `--help`, `-V` for `--version`, `-f` for `--force`, `-n` for `--dry-run`, `-a` for `--all`, and `-l` for `--list`.
- Claude-authored skills from `anthropics/skills`: `frontend-design` joins the `developing` theme, and a new `claude-api` theme is indexed against the `anthropic` package.

### Breaking changes

- Non-interactive generation no longer overwrites an existing file or skill that Tara cannot prove it owns. Scripts that intentionally replace such paths must pass `--force` to `tara init`, `tara integrations`, `tara sync`, or the deprecated `tara opencode sync`. Interactive runs show a unified diff and ask before replacing the path.
- Commands that consume `.tara/config.toml` now reject malformed TOML, unknown integrations, and invalid value types instead of silently falling back to defaults. Correct the configuration before running `tara init`, `tara integrations`, or `tara sync`; unrelated commands remain available for diagnosis and recovery.

### Changed

- `tara sync` now regenerates every configured integration after syncing skills from installed packages, so newly synced skills reach OpenCode and Claude Code too.
- `.tara/config.toml` records an explicit `integrations` list instead of the ambiguous `tool` or `tools` keys. Existing configs are migrated on read.
- `all` and `*` expand to the currently supported integration names when configuration is written. Legacy `tool = "all"` retains its 1.0 behavior and migrates to `["copilot", "opencode"]`.
- Removing an integration deletes only Tara-marked files and recorded skill directories. Hand-written files and unrelated OpenCode settings remain untouched.
- Frontmatter is parsed and written with PyYAML instead of a hand-rolled parser, so typed values (e.g. `tools: [read, search]`) survive round-tripping.
- The bundled base instructions gain branch naming (`<type>/<short-description>`), commit message format (imperative, 72-character subject), flaky-test guidance, and prose rules on full sentences and one-sentence-per-line wrapping.

### Deprecated

- `tara opencode sync` is superseded by `tara sync` and `tara integrations opencode`. It still works, but is hidden from help.

### Fixed

- `pyyaml` is now a declared runtime dependency. It was previously only present transitively via a dev dependency, so clean installs could fail.
- Relaxed the `pydantic` floor from `>=2.13.4` to `>=2.7` to avoid needless resolver conflicts.
- Ctrl-C in the interactive artifact picker now exits instead of silently confirming the current selection and continuing.
- A nested prompt no longer suppresses a same-named starter command. `.github/prompts/python/check.prompt.md` generated `python/check.md` but stopped the root `check.md` starter from being written, because collisions were tracked by filename rather than by path.
- `tara sync` now names the real owner of a skill it declines to overwrite (`git-managed` or `core catalog`) and says how to override it, instead of labelling every such skill "core-managed". The same skip is no longer reported twice.
- Generated integration files never silently overwrite hand-written ones. Every generated Markdown file carries a marker, and mirrored skills are recorded in `.tara/generated.json`. Interactive replacement shows a unified diff and asks for confirmation; non-interactive replacement requires `--force`. Tara no longer adopts unmarked pre-1.1 opencode output automatically.
- Porting skills no longer crashes on a plain file or symlink sitting in the destination skills directory.
- `opencode.json` is updated in place instead of rewritten. Settings Tara does not own (`model`, `theme`, `provider`, `agent`, `permission`, `keybinds`, ...) are preserved; only `$schema`, `instructions`, and `mcp` are managed. A malformed or non-object file is left byte-for-byte untouched and reported instead of being replaced.
- A Claude subagent whose Copilot `tools` list maps to nothing now falls back to a read-only allowlist. It previously omitted `tools` entirely, which silently granted the subagent the full toolset including `Bash` and `Write`.
- Agent permission lists remain under the external `tools` key required by Copilot and Claude Code. Empty lists now remain empty, while `all` and `*` expand to explicit current tool names instead of silently inheriting future capabilities.
- Copilot's own tool vocabulary (`codebase`, `usages`, `problems`, `editFiles`, `runCommands`, `findTestFiles`) is recognised when translating agent permissions for both Claude Code and opencode.
- A broken `.tara/config.toml` is reported by commands that consume it instead of raising a traceback or silently choosing defaults. Unrelated commands are no longer blocked by an invalid tool selection.
- Frontmatter parsing now requires an exact opening `---` and no longer stops at an indented `---` inside a block scalar.
- `tara integrations claude,opencode` accepts the comma-separated form documented by `tara init --integrations`.

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
