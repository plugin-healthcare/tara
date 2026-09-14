# Claude port through `@`-imports, plus catalog follow-ups

Date: 2026-09-07
Branch: `feat/claude-code-support`
Status of the current branch: green gate, uncommitted.

## 1. Rework the Claude port to `@`-imports (implemented as a hybrid)

Claude Code 2.1.236 was tested directly. Nested command files expand relative `@` imports,
but subagent files treat both relative and repository-root forms as literal prompt text.
The implementation therefore imports prompt bodies for commands and retains generated
copies for agent bodies. `.github/` remains the only authored source in both cases.

Today `src/tara/claude.py` translates and duplicates content: `translate_agent` and
`translate_prompt` copy the body of every `.github/agents/*.agent.md` and
`.github/prompts/**/*.prompt.md` into `.claude/`. Two copies means the Claude side goes
stale whenever the Copilot side is edited without a regeneration.

The developer's finding: a Claude-side file whose body is just `@.github/agents/yoda.agent.md`
keeps a single source of truth without leaving the standard layout. Import semantics from
the Claude Code memory docs:

- Imported files are expanded and loaded into context at launch, alongside the file that
  references them.
- Relative and absolute paths both work; a relative path resolves against the file
  containing the import, not the working directory.
- Imports recurse to a maximum depth of four hops.
- Import parsing skips code spans and fenced code blocks, so a path in backticks stays
  literal.

`port_instructions` already uses this for `CLAUDE.md`. Extend it to agents and commands.

### Steps

1. Confirm empirically that Claude Code expands `@path` in `.claude/agents/*.md` and
   `.claude/commands/*.md`, not only in memory files. The docs describe the syntax for
   `CLAUDE.md`; the developer reports it works elsewhere. Write one agent and one command
   by hand, launch Claude Code, and check the body arrives. Do not spend a session on
   documentation for this; test it.
2. Keep the frontmatter translation. Claude registers a subagent by its frontmatter
   (`name`, `description`, `tools`), and the tool mapping in `_TOOL_MAP` still has to run.
   Only the body changes, from the copied text to a single `@` line.
3. Path direction: `.claude/agents/yoda.md` importing `.github/agents/yoda.agent.md` is
   two directories up and across. Decide between a repo-root-relative path and a
   correctly computed relative one, and cover it with a test.
4. Same treatment for `.claude/commands/`, including the nested `python/add-types.md`
   case, where the relative depth differs.
5. Leave `_STARTER_COMMANDS` (`check`, `review`) as inline bodies. They have no Copilot
   source to import.
6. Skills stay mirrored. A `SKILL.md` is discovered by directory scan and its frontmatter
   is read directly, so an import in the body would not be expanded before discovery.
   Verify this before changing anything about `port_skills`.
7. Update `tests/test_claude.py`: the existing assertions look for translated body text
   that will no longer be there.
8. Update the README Claude Code section and the CHANGELOG. Call it a behaviour change:
   the ported files no longer contain a copy of the body.

### Risks

- If an import is not expanded in agents or commands, the agent silently loses its
  instructions. That is worse than duplication, so step 1 gates the rest.
- The four-hop limit: `CLAUDE.md` imports `copilot-instructions.md`, which may import
  more. An agent importing an agent file that imports something else stays well inside
  the limit, but count the hops before adding another layer.

## 2. Dogfood the new catalog files in this repo

`.github/instructions/python.instructions.md` here is hand-written and now diverges from
the catalog version this session added. Install the catalog file (`tara add`) and check
whether anything in the local one is worth keeping first. Same question for
`markdown.instructions.md`, which this repo does not have at all.

## 3. Refresh the three scanned repos

- `pluginlake` and `nyctea` carry the pre-fine-tuning `markdown.instructions.md`. They
  need the new catalog version.
- Both would benefit from `python.instructions.md`, and `nyctea` can drop the Polars
  "common mistakes" block from its `copilot-instructions.md` once it has the scoped file.
- `srdp-hub/srdp` is not Tara-managed (hand-written `AGENTS.md` and `copilot-instructions.md`).
  Decide whether to bring it under `tara init` or leave it. Its hooks and instructions are
  now upstream in Tara either way.
- `pluginlake/.github/skills/plugin-brand.md` is org-specific and a loose file rather than
  a skill directory. It stays local; it does not belong in the catalog.

## 4. Skill size discipline (new, from the likec4 observation)

`likec4-dsl` installs 18 files and 216K with a 428-line `SKILL.md`; `dagster-expert`
installs 173 files and 764K. A few small specialised skills work better than one large
one, because the whole `SKILL.md` enters context on selection while the reference files
are only read on demand.

Options, roughly in order of effort:

- Add a `tara audit` finding for an oversized skill: warn above roughly 200 lines of
  `SKILL.md`, and note the installed file count and total size. `audit_instructions`
  already warns past 400 lines, so the rule shape exists.
- Give `index.toml` a way to install a subset of a large upstream skill's references,
  or at least report what a theme is about to pull in before installing it.
- Reconsider whether the `likec4` theme belongs in the index at its current size.

Measure before acting. The claim that fewer, more specialised skills win needs a source
or a test in this repo, not just an impression.

## 5. Parked

Moving the Python stack section out of the always-on `copilot-instructions.md` into the
scoped `python.instructions.md`. It would cut tokens on every request, but it changes
generated output for every existing repo, so it needs a migration and its own increment.

## Progress on 2026-09-08

- The Claude port was completed as a hybrid after testing Claude Code 2.1.236 directly.
  Commands expand relative `@` imports, including nested commands. Subagents leave the
  import text literal, so Tara still copies their bodies.
- The repo now dogfoods the markdown rules and the concise Python/Polars additions under
  `.github/instructions/`.
- `tara audit` now warns above 200 lines in `SKILL.md` and reports the complete skill's
  file count and size. The real `likec4-dsl` skill produces a warning at 429 lines,
  18 files, and 180.8 KiB.
- The proposed `reviewing-changes` skill was removed after specialist review because it
  duplicated `review.prompt.md`. Its evidence-based checks now live in that prompt.
- `managing-github-issues` remains separate from content-focused
  `writing-epics-stories`, with explicit confirmation before shared GitHub mutations and
  stable-key guidance for bulk runs.
- The sibling repositories were not edited. Their refresh stays a separate task because
  each has its own dirty worktree and review cycle.
- The Python always-on-to-scoped migration remains parked.
