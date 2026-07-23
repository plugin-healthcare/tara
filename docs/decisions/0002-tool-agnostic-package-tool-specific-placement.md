# ADR-0002: tool-agnostic package, tool-specific placement

- **Status:** Accepted
- **Date:** 2026-07-20
- **Authors:** @yannick-vinkesteijn

## Context and Problem Statement

Wingman authors one set of guardrails under `wingman/data/` and writes them into a
repo for an agent tool to read. Today the write path targets GitHub Copilot only.
We want to support more tools (opencode, Claude Code, goose) without duplicating
content or naming the source after one tool.

## Considered Options

- Keep Copilot canonical and derive other tools from its `.github/` files.
- Make `AGENTS.md` the shared source and copy it to the Copilot file.
- Separate a tool-agnostic package from a tool-specific placement step.

## Decision Outcome

Split the two concerns:

- **The package is tool-agnostic.** Content and structure under `wingman/data/` use
  neutral names and assume no tool.
- **Placement is tool-specific.** Writing the content into a repo is where a tool's
  conventions apply. Keep it generic where beneficial (reference a shared core file
  instead of duplicating it) and tool-specific only where a tool requires it.

Only the GitHub Copilot writer is implemented now (`.github/copilot-instructions.md`
plus catalog files under `.github/`). Do not emit `AGENTS.md` on the Copilot path:
it is redundant, and the Copilot CLI ignores it when `copilot-instructions.md`
exists (github/copilot-cli#489). Other tools and a config-driven default set are
separate issues.

### Consequences

- Good, because content stays portable and adding a tool is a new writer, not a
  rewrite.
- Good, because the Copilot path stays one always-on file with no duplication.
- Bad, because the generic writer and config model are decided ahead of their
  implementation; only Copilot exists today.
