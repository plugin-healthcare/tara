# Skills in tara

Skills are reference files Copilot loads on demand, stored as `.github/skills/<name>/SKILL.md` (plus optional `references/` and `assets/`).
Tara fetches them from git, pins them in `.tara/skills.lock`, and records them in `.tara/skills.toml`.

## Installing

Skills are grouped into themes in the `tara init` / `tara add` picker: pick a theme and all of its skills install at once.
You can also install directly:

```bash
tara skill add query      # one skill from the index
tara skill add duckdb      # a theme (all DuckDB skills at once)
tara skill add streamlit   # the official Streamlit skill
tara skill add https://github.com/org/repo --path skills/foo --ref main
```

Manage installed skills:

```bash
tara skill list            # installed skills (--all also shows themes)
tara skill update [name]   # re-fetch one or all to the latest commit
tara skill remove <name>   # delete from disk and the manifest
```

## Themes in the index

- `duckdb` (from [duckdb/duckdb-skills](https://github.com/duckdb/duckdb-skills)): every official DuckDB skill (`query`, `read-file`, `attach-db`, `convert-file`, `s3-explore`, `spatial`, and so on).
- `streamlit` (from [streamlit/agent-skills](https://github.com/streamlit/agent-skills)): building, styling, and deploying Streamlit apps.
- `dagster` (from [dagster-io/skills](https://github.com/dagster-io/skills)): `dagster-expert` (Dagster and the `dg` CLI) and `dignified-python` (opinionated production Python standards).
- `agent-tooling` (from [anthropics/skills](https://github.com/anthropics/skills)): `skill-creator` and `mcp-builder`.
- `developing` (from [anthropics/skills](https://github.com/anthropics/skills)): `webapp-testing` (Playwright-driven web app testing) and `frontend-design` (frontend design guidance).
- `claude-api` (from [anthropics/skills](https://github.com/anthropics/skills)): building on the Claude API — model ids, params, streaming, tool use, caching, token counting. Indexed against the `anthropic` package, so `tara sync` picks it up automatically.
- `likec4` (from [likec4/likec4](https://github.com/likec4/likec4)): `likec4-dsl` reference for `.c4`/`.likec4` files.
- `gh-stack` (from [github/gh-stack](https://github.com/github/gh-stack)): `gh-stack` skill for creating, viewing, and managing stacked pull requests with the `gh stack` CLI.

## Sets

A theme is a set: it bundles every skill under a directory so you install them in one go.
`tara skill add duckdb` clones the repo once and installs all its skills (minus the Claude-Code-only `read-memories`), recording each one individually so `skill list`, `update`, and `remove` still work per-skill.
See the sets at the bottom of `tara skill list --all`.

## Libraries without a skill

Not every popular library has an official skill.
FastAPI, Pydantic, and Polars ship no official `SKILL.md`.
Polars is covered through its MCP server, and Pydantic through the `docs` MCP server (its `llms.txt`).
Add your own to `.tara/skills.toml` (or the index) any time.

## Discovering skills from installed packages

`tara sync` scans installed packages for `SKILL.md` files bundled under the library-skills convention and copies them into `.github/skills/`.
For packages with a known theme in the index it fetches those, and for the rest (with `--docs`, on by default) it probes PyPI for an `llms.txt` and wires it into the `docs` MCP server.
