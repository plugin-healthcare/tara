# Core: Generic DevOps Cycle

These instructions apply to all projects regardless of stack. Focus is on the
plan, code, build, test, and release phases.

## Basic rules

- **Never commit code.** The developer always reviews and commits. Stage or edit
  files, draft commit messages, and open pull requests, but do not run `git commit`
  or `git push`. This follows the Linux Foundation agentic coding guidelines.
- Keep responses short and to the point. Be precise, don't flatter, and ask for
  clarification when unsure.
- Write plainly and avoid typical AI formulation: no em dashes, emoji, hype adjectives,
  or filler. For how to document, see the `writing-documentation` skill.
- Prefer open source and open standards over proprietary, closed alternatives.
- Prefer official documentation and code over blogs and articles.
- Don't reinvent tools or frameworks when a good existing one fits the job.
- Use the `tara` CLI for setup, scaffolding, checks, and standards (`tara new`,
  `tara check`, `tara standards`); run `tara --help` to discover commands
  instead of hand-rolling them.
- Prefer clear over clever; code is read more than written. Flag debt with
  `# TODO(name): reason` so it stays searchable.
- Follow composable-stack principles: modular software with clear interfaces and
  contracts built on open standards.
- Work agile: every session produces a working, reviewable, tested increment.
- Standardize the code and the way of working, so any developer or agent can pick
  up another's work.

## Workflow: the fixed flow

Every change follows the same loop through the DevOps cycle (plan, code, test,
review, release). Don't skip steps; if one genuinely doesn't apply, say why.

1. **Understand**: read the story/task and its Definition of Done before touching code.
2. **Plan**: draft a short execution plan (files to change, edge cases, steps) and
   confirm it for anything non-trivial.
3. **Test first**: write a failing test for the next behaviour (TDD); test each
   behaviour once and keep tests independent, so one failure points to one cause.
4. **Implement**: the minimum code to pass, in small reviewable increments, one
   logical change at a time.
5. **Check**: run the gate (`tara check`: lint, format, types, tests, security)
   and fix until it is green; don't pile new work on a red gate.
6. **Document**: update docs/README and the runnable example for new behaviour;
   update the changelog if the change is user-facing.
7. **Review & hand off**: verify the Definition of Done, stage changes, and draft the
   commit message for the developer to run (see Basic rules). Log the hand-off (below)
   so the next session can pick up.

When blocked, say so; don't silently guess.

## Agent memory / working docs

`tara init` creates a framework-agnostic `.agents/` doc store (tracked in git,
shared working knowledge) with a folder per standardized doc you produce:

- `.agents/plan/` -- plans and execution plans.
- `.agents/design/` -- design docs; finalized ADRs live in `docs/decisions/`.
- `.agents/review/` -- code and maturity reviews.
- `.agents/memory/` -- freeform session notes and handover scratch.

- Name each doc `YYYYMMDDHHMM_<short-descriptive-title>.md`: a timestamp to the
  minute (no spaces), so files sort by time and rarely collide across sessions.
- Keep each folder's `index.md` current: one row per doc (date, file, one-line
  summary), newest first, so the next session can scan it instead of opening
  every file.
- At the end of each phase (refine, design, implement, review, integrate), and
  whenever you hand work off, drop a short note in `.agents/memory/` and file
  any plan, design, or review under the matching `.agents/` folder.
- Keep docs short and current: what was done, what's left, and any open
  decisions. Don't duplicate them into commits or the repo's real docs.
- This store holds working plans, designs, reviews, and handover notes only.
  ADRs belong in `docs/decisions/`; stories and epics in your tracker or board.
- To keep a subfolder local instead of committed, list it under
  `[agents] gitignore` in `.tara/config.toml` (for example `["memory"]`).
- Never put secrets or credentials here; by default the store is committed
  and shared.

## Safety: destructive operations

Never run a destructive or irreversible command on your own. Stop and ask the
developer to run it, or to confirm it explicitly, first. This keeps the harness
safe for everyone, especially less experienced developers.

Do not do these without explicit confirmation:

- **Rewrite or discard history**: `git push --force`, `git reset --hard`,
  `git rebase` on shared branches, `git commit --amend` on pushed commits.
- **Delete work**: `rm -rf`, `git clean -fdx`, deleting branches, tags, or
  remotes, dropping a database/table, `TRUNCATE`, `DROP`, destructive migrations.
- **Overwrite the environment**: recursive `chmod`/`chown -R`, editing files
  outside the repo, changing global git or system config.
- **Touch production or shared infrastructure** in any way.

Prefer the safe form first: dry-run flags, `git status`, list what would change
before changing it. When in doubt, explain the command and let the developer run it.

## Definition of done

A change is done only when all of these hold. The pre-commit hook and `tara check`
gate enforce the mechanical items; you are responsible for the rest.

- [ ] The new behaviour is covered by tests, and the full gate passes (`tara check`:
  lint, format, types, tests, security).
- [ ] The increment runs: an integration test plus a small runnable example demonstrate it.
- [ ] Docs updated for the changed behaviour; changelog updated if the change is user-facing.
- [ ] No secrets, credentials, or local config staged; the developer makes the commit.
- [ ] Handover notes in `.agents/memory/` are current so the next session can continue.
