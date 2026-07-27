# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-07-27

Initial release of Tara, a GitHub Copilot guardrail toolkit that installs and
maintains the guardrails Copilot reads while you code.

### Added

- `tara init` to set up a repo: writes `.github/copilot-instructions.md` and
  `.mcp.json`, then adds selected instructions, skills, agents, and prompts.
- A git-ignored `.agent/` doc store (`memory/`, `planning/`, `reviews/`), each
  with an `index.md`, for the standardized working docs agents produce.
- `tara add` and `tara list` to manage bundled artifacts, and `tara sync` to pull
  in `SKILL.md` files shipped by installed packages (library-skills convention).
- `tara check`: a single gate running lint, format, type-check, tests, and a
  dependency audit, configurable per repo via `.tara/checks.toml`.
- `tara standards`: opinionated `pyproject.toml` tool tables and a
  `.pre-commit-config.yaml` baseline (ruff, ty, pytest, uv).
- `tara audit` to flag issues in MCP config and dependencies.
- `tara new` to scaffold ADRs, epics, stories, spikes, and other docs from templates.
- `tara skill`, `tara agent`, and `tara opencode` command groups.
- Bundled guardrails: base and Python instructions, a curated skill catalog, helper
  agents, and design, implement, refine, integrate, and review prompts.
