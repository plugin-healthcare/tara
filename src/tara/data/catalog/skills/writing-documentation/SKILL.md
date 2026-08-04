---
name: writing-documentation
description: "Use when writing or improving documentation: a README, a guide or how-to, module and API docstrings, usage examples, or an explanation of how something works. Covers audience, structure, docstrings, diagrams, and keeping docs in sync with the code. For specific artifacts, defer to the ADR, changelog, and runbook skills and templates."
---

# Writing documentation

Good documentation answers a reader's question faster than reading the code would.
Write for that reader: the why, the decisions, and how to use the thing, not the
obvious what. Prose style (plain, no AI tells) is in
`.github/copilot-instructions.md`; markdown-file mechanics are in
`.github/instructions/markdown.instructions.md`. This skill is the how.

## Start from the reader

- Name the audience and their question: new user, integrator, maintainer, on-call.
  Put the answer to the most common one first; detail below it.
- Document intent and usage, not the mechanics the code already shows. If a comment
  just restates the line beneath it, delete it. Put a comment on its own line above
  the code it explains, never trailing it.
- Show, don't assert: a short runnable example beats adjectives. Every feature ships
  with a way to run and verify it.

## What to write, and where

- **README**: what it is in one line, a quickstart (install, run), the common tasks,
  and where to go next. An entry point, not the whole manual.
- **Docstrings** (the convention set in `pyproject.toml`, google by default): every
  public module, class, and function. Keep them short and to the point: the purpose,
  the key decisions, and how it works, plus args, returns, and raises. Don't narrate
  every internal step; defer implementation detail to a comment. Keep them true to the
  code; a wrong docstring is worse than none.
- **Guides and how-tos**: task-oriented, one goal each, ordered steps a reader can
  follow start to finish.

## Diagrams

When structure is easier shown than told, add a Mermaid or LikeC4 diagram and keep it
in the repo as text so it diffs and reviews like code. Prefer a diagram over a wall of
prose for architecture, flows, and state.

## Keep it current

- Update docs in the same change as the behaviour (the flow's document step). Docs
  that lie erode trust faster than missing docs.
- One source of truth: link, don't copy. Duplicated docs drift apart.
- Delete docs for removed behaviour instead of leaving stale text behind.

## Specific artifacts have their own homes

- Architecture and design decisions: the `writing-adrs` skill (`tara new adr`).
- User-facing changes: the changelog, via the `release-semver-changelog` skill.
- Runbooks and post-mortems: `tara new runbook`, `tara new post-mortem`.
- Epics and stories: the `writing-epics-stories` skill.
