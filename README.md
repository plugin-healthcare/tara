![](./images/tara-duotone.png)

# Tara

Tara is an agentic engineering toolkit that guides both agents and developers to follow devops and coding best practices.
It is a small Python CLI you install in a repo to set up your coding agent the way you would: it writes the instruction and MCP files the agent reads, fetches and updates reusable skills, scaffolds prompts and agents, and runs a check gate that lints, type-checks, and tests the way you would by hand.
Tara is Python and uv focused and Copilot-first, with opencode supported and framework-agnostic tools for planning and reviewing.

## Why use it

Agents deliver quality when they have guardrails, not when they burn through tokens guessing.
That takes discipline and structure from both the developer and the agent.
An agent is far more useful when it knows how your project is built: its conventions, the tools it uses, and the quality bar a change has to clear.
Without that context it guesses, and the guesses drift from how you actually work.
Tara writes the context into the files your agent already reads, so its suggestions follow your project instead of a generic default.

If you are new to a stack, Tara also gives you a sensible starting point: an opinionated Python setup (ruff, `ty`, pytest, uv, and a pre-commit hook) and one command, `tara check`, that runs the same lint, type, test, and dependency checks a reviewer would.
You get a working baseline without wiring it together yourself, and everything Tara writes is a plain file you can read, edit, or remove.

## What Tara is (and is not)

There is a clean split between the two halves of the workflow:

- **Tara (this CLI) does setup and management.**
  It is a normal command-line tool.
  It writes files into your repo, fetches skills from git, audits those files for best practices, and runs your lint/format/test gate.
  It does not talk to a model at runtime (except `audit --deep`, which shells out to the Copilot CLI for an optional content review).
- **Your coding agent does the runtime work.**
  Copilot is the primary target: it reads the files Tara writes (`.github/copilot-instructions.md`, `.github/skills/`, `.github/agents/`, `.github/prompts/`, `.mcp.json`) while you code, and opencode is supported through a generated port.
  Tara never replaces the agent; it gets the guardrails in place and keeps them healthy.

In short: **Tara installs and maintains the guardrails; your agent uses them.**

About the name: [Tara](https://en.wikipedia.org/wiki/Tara_(Buddhism)) is an important female Buddha in Buddhism.
She is known as a saviouress who hears the cries of beings who are 'running around in circles' and saves them from danger.

## Install

Run it without installing:

```bash
uvx tara init
```

Or add it as a dev dependency of your project:

```bash
uv add --dev tara
uv run tara init
```

Every command operates on the current working directory (the repo you are in).

## Quick start

```bash
tara init            # write copilot-instructions.md + .mcp.json, then pick artifacts
tara list            # show the guardrails active in this repo
tara check           # run the lint/format/test gate
tara audit           # lint your skills/agents/instructions for best practices
```

Once the files are in place, see [`docs/using-in-copilot.md`](docs/using-in-copilot.md) for how your agent picks up each artifact (instructions, skills, agents, prompts, MCP) while you code.

## Commands

Full reference (every command, flag, and argument) is auto-generated in [`docs/cli.md`](docs/cli.md); refresh it with `uv run python scripts/gen_cli_docs.py`.
The essentials:

- **Setup:** `tara init` (write instructions + `.mcp.json`, pick artifacts), `tara add` (re-open the picker), `tara sync` (pull skills/docs from installed packages).
- **Inspect:** `tara list` (what your agent will pick up).
- **Skills & agents:** `tara skill add|list|update|remove`, `tara agent list|add`.
- **Quality gate:** `tara check` (ruff, `ty`, pytest, `uv audit`), `tara standards` (compare tooling to the opinionated baseline), `tara audit` (lint guardrail artifacts).
- **Scaffold:** `tara new [kind] [name]` (prompt, agent, or a document such as `adr`, `runbook`, `changelog`, `ci`).
  Run `tara new` to list kinds.

## What gets written into your repo

```
.github/
  copilot-instructions.md          # always-on instructions Copilot reads
  instructions/*.instructions.md   # scoped instructions (applyTo globs)
  skills/<name>/SKILL.md           # fetched skills (+ references/, assets/)
  agents/<name>.agent.md           # custom agents
  prompts/<name>.prompt.md         # slash-command prompts
.mcp.json                          # MCP servers (Copilot CLI "mcpServers" schema)
.agent/                            # git-ignored working docs (agent memory)
  memory/ planning/ reviews/       # each seeded with an index.md
.tara/
  config.toml                      # setup state: selected tool + stack (+ [standards] overrides)
  skills.toml                      # skill manifest (source of truth)
  skills.lock                      # pinned commits
  checks.toml                      # optional: override the check gate
  instructions.local.md            # optional: appended to copilot-instructions.md
  mcp.local.json                   # optional: merged into .mcp.json
```

## opencode

Copilot's `.github/` setup is the single source of truth.
opencode files are a generated **port** of it, so there's only ever one copy to maintain:

```bash
tara init --tool opencode   # set up Copilot, then port it to opencode
tara init --tool all        # same as --tool opencode
tara opencode sync          # re-port after changing .github/ (run anytime)
```

The port writes (all derived, never hand-edited):

```
opencode.json          # references .github/copilot-instructions.md + MCP servers
.opencode/agents/*.md   # translated from .github/agents/*.agent.md
.opencode/commands/*.md # translated from .github/prompts/**/*.prompt.md
.opencode/skills/<name>/ # mirrored from .github/skills/<name>/
```

Edit the Copilot side (or Tara's bundled standard) and re-run `tara opencode sync`.
The default `tara init` (`--tool copilot`) skips the port entirely.

## MCP setup

Tara writes the repo-root `.mcp.json` (the `mcpServers` schema the **GitHub Copilot CLI** reads).
Servers are **opt-in**: `tara init` / `tara add` show a picker.
Bundled servers are `github` and `git` (defaults), plus `polars` and `likec4`; `tara sync --docs` can wire in a `docs` server from a package's `llms.txt`.
Add repo-local servers in `.tara/mcp.local.json`.

Remote servers send tool-call arguments to a third party, so enabling one prints a warning.
VS Code reads `.vscode/mcp.json` (not the root file), and the Copilot coding agent reads its config from repo settings on GitHub.
See [`docs/mcp.md`](docs/mcp.md) for the full server list, transport details, and privacy breakdown.

## Skills

Skills are grouped into **themes** in the `tara init` / `tara add` picker: pick a theme and all of its skills install at once.
List them with `tara skill list --all`, or install one directly with `tara skill add <theme>`.
The index currently ships:

- **duckdb** (from [`duckdb/duckdb-skills`](https://github.com/duckdb/duckdb-skills)): every official DuckDB skill (`query`, `read-file`, `attach-db`, `convert-file`, `s3-explore`, `spatial`, and so on).
- **streamlit** (from [`streamlit/agent-skills`](https://github.com/streamlit/agent-skills)): building, styling, and deploying Streamlit apps.
- **dagster** (from [`dagster-io/skills`](https://github.com/dagster-io/skills)): `dagster-expert` (Dagster + `dg` CLI guidance) and `dignified-python` (opinionated production Python standards).
- **agent-tooling** (from [`anthropics/skills`](https://github.com/anthropics/skills)): `skill-creator` and `mcp-builder`.
- **developing** (from [`anthropics/skills`](https://github.com/anthropics/skills)): `webapp-testing` (Playwright-driven web app testing).
- **likec4** (from [`likec4/likec4`](https://github.com/likec4/likec4)): `likec4-dsl` reference for `.c4`/`.likec4` files.

```bash
tara skill add query           # one skill, from the index
tara skill add duckdb           # a whole set (all DuckDB skills at once)
tara skill add streamlit        # the official Streamlit skill
tara skill add https://github.com/org/repo --path skills/foo --ref main
```

**Sets** bundle every skill under a directory so you can grab them in one go.
`tara skill add duckdb` clones [`duckdb/duckdb-skills`](https://github.com/duckdb/duckdb-skills) once and installs all its skills (minus the Claude-Code-only `read-memories`), recording each individually so `skill list`, `update`, and `remove` still work per-skill.
See sets at the bottom of `tara skill list --all`.

Not every popular library has an official skill.
FastAPI, Pydantic, and Polars ship no official `SKILL.md`; Polars is covered through its MCP server above, and Pydantic through the `docs` MCP server (its `llms.txt`).
Add your own to `.tara/skills.toml` (or the index) any time.

## The check gate

`tara check` runs the commands in `.tara/checks.toml`, or the bundled defaults for your stack.
The Python default is:

```toml
[[check]]
name = "lint"
cmd = "uv run ruff check"

[[check]]
name = "format"
cmd = "uv run ruff format --check"

[[check]]
name = "types"
cmd = "uv run ty check ."

[[check]]
name = "test"
cmd = "uv run pytest --tb=short"

[[check]]
name = "security"
cmd = "uv audit --preview-features audit-command"
```

The `types` and `security` steps need uv >= 0.11.
`uv audit` reports known CVEs and PEP 792 adverse project statuses (archived / deprecated / quarantined).

It stops on the first failure (use `--no-fail-fast` to run them all) and exits non-zero if any check fails, so it works as a pre-commit or CI gate.

## Auditing guardrails

`tara audit` is a deterministic linter for the files your agent consumes.
It checks the mechanical things that make a skill or instruction effective: a kebab-case name that matches its folder, a description that says *when* to use it, complete frontmatter, and a body that is neither empty nor bloated.

For the subjective half (is this skill actually well written?), `--deep` hands the files to the Copilot CLI using the bundled `skill-reviewer` agent.
The mechanical audit always runs; the deep review is opt-in because it costs a model call.

## Development

```bash
uv sync
uv run pytest
uv run ruff check
uv run ruff format
```

## Credits

Projects we borrowed ideas from or built on top of:

- **[library-skills](https://github.com/tiangolo/library-skills)** by tiangolo: the convention of shipping `SKILL.md` files inside Python packages under `.agents/skills/`.
  `tara sync` scans installed packages using that standard and brings discovered skills into `.github/skills/` for your agent.
- **[ponytail](https://github.com/DietrichGebert/ponytail)** by DietrichGebert: a "write only what the task needs" ruleset for AI agents.
  Informed the thinking behind Tara's default instructions and check gate philosophy.
