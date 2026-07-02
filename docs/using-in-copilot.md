# Using wingman's guardrails in GitHub Copilot

Wingman only does setup. Once it has written the files into your repo, GitHub
Copilot is what actually reads and uses them while you code. This guide shows
how each artifact is picked up, using the **GitHub Copilot CLI** as the primary
surface (that is what wingman's `.mcp.json` targets), with notes for VS Code.

Run `wingman init` first, then start Copilot in the repo:

```bash
copilot
```

Inside a session, `/env` shows everything Copilot has loaded: instructions, MCP
servers, skills, agents, hooks, and LSPs. Use it to confirm your guardrails are
active.

## Instructions (always-on and scoped)

Wingman writes `.github/copilot-instructions.md` (always-on) and optional
`.github/instructions/*.instructions.md` (scoped, each with an `applyTo` glob in
its frontmatter). Copilot reads both automatically, with no command needed:

- The always-on file is included in every request.
- A scoped file is added only when you are working on files that match its
  `applyTo` glob (for example `**/*.py`).

Use `/instructions` to view which instruction files are active and toggle them.
`/env` lists the same set. In VS Code these files are read automatically too.

## Skills

Wingman fetches skills into `.github/skills/<name>/SKILL.md`. Copilot loads a
skill on its own when your request matches the `description` in the skill's
frontmatter, so you usually do not invoke them by hand. Just describe the task
(for example "write an ADR for this decision") and the relevant skill is pulled
in.

Manage them with `/skills` (enable, disable, inspect). Confirm what is available
with `wingman skill list` or `wingman list`.

## Agents

Wingman installs custom agents into `.github/agents/<name>.agent.md`. Select one
in a session with:

```
/agent            # browse installed agents
/agent yoda       # switch to a specific agent
```

An agent swaps in its own persona, tool set, and constraints (for example the
read-only mentor agents wingman bundles). Use `wingman agent list` to see which
agents are installed in the repo.

## Prompts (slash-command prompts)

Wingman scaffolds reusable prompts into `.github/prompts/<name>.prompt.md`. These
are primarily a **VS Code Copilot** feature: in the Chat view type `/` followed
by the prompt's filename to run it, or open the file and use the play button.

In the Copilot CLI, treat a prompt file as a saved instruction you can paste or
reference by path when you want that exact workflow.

## MCP servers

Wingman writes the repo-root `.mcp.json` (the `mcpServers` schema the Copilot CLI
reads). Servers give Copilot extra tools: git operations, GitHub issues and PRs,
docs lookups, and so on. They are opt-in, chosen during `wingman init` /
`wingman add`.

In a session, use `/mcp` to view and manage servers, and `/env` to confirm they
are connected. Then just ask for something a server provides ("open a PR for this
branch", "what changed in this file's history") and Copilot calls the tool.

VS Code does not read the root `.mcp.json`; it reads `.vscode/mcp.json` under a
`servers` key. See [`mcp.md`](mcp.md) for the full breakdown and the privacy
notes on remote servers.

## The check gate

Wingman's gate is not a Copilot feature, it is a plain command:

```bash
wingman check      # ruff lint + format, ty types, pytest, uv audit
```

Ask Copilot to run it after making changes ("run wingman check and fix anything
that fails"). This keeps Copilot's edits inside the same lint, type, test, and
supply-chain guardrails you would enforce by hand. Override the steps per repo in
`.wingman/checks.toml`.

## Quick reference

| You want to | Do this |
| --- | --- |
| Confirm what Copilot loaded | `/env` in a session |
| See or toggle instructions | `/instructions` |
| Pick a custom agent | `/agent [name]` |
| Manage skills | `/skills` |
| Manage MCP servers | `/mcp` |
| Run a saved prompt (VS Code) | `/<prompt-name>` in Chat |
| Run the quality gate | `wingman check` |
