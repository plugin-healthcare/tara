# Core: Generic DevOps Cycle

These instructions apply to every project, whatever the stack.

## Basic rules

- **Never commit code.** Stage files, draft the commit message, and let the developer
  run `git commit` and `git push`.
- Work on a `<type>/<short-description>` branch (`feat/add-auth`, `fix/null-pointer`).
  Imperative commit subjects of 72 characters or less, one logical change per commit.
- Be short, precise and direct. Don't flatter. Ask when unsure, and say so when
  blocked instead of guessing.
- Write plainly: no overuse of em dashes, no emoji, hype adjectives, filler, or a
  colon followed by a noun-phrase fragment. See the `writing-documentation` skill.
- Prefer open source and open standards, official documentation over blogs, and an
  existing good tool over a new one.
- Use the `tara` CLI for setup, scaffolding, checks and standards. Run `tara --help`
  instead of hand-rolling commands.
- Prefer clear over clever; code is read more than written. Flag debt with
  `# TODO(name): reason` so it stays searchable.
- Build modular software with clear interfaces and contracts on open standards.
- Standardize the code and the way of working, so any developer or agent can pick up
  another's work.

## Workflow

Every change runs the same loop and ends in a working, reviewable, tested increment.
Don't skip a step; if one genuinely doesn't apply, say why.

1. **Understand**: read the task and its Definition of Done before touching code.
2. **Plan**: for anything non-trivial, confirm a short plan (files, edge cases, steps).
3. **Test first**: write the failing test. One behaviour per test, tests independent,
   so one failure points to one cause.
4. **Implement**: the minimum code to pass, in small reviewable increments.
5. **Check**: run `tara check` (lint, format, types, tests, security) until it is
   green. Report a flaky test instead of re-running it until it passes by luck.
6. **Document**: update the docs, the runnable example, and the changelog if the
   change is user-facing.
7. **Hand off**: verify the Definition of Done, stage the changes, draft the commit
   message, and log the hand-off in `.agents/memory/`.

## Agent working docs

`tara init` creates `.agents/`, a git-tracked doc store: `plan/` for plans, `design/`
for design docs, `review/` for code and maturity reviews, and `memory/` for session
notes and handovers.

- Name each doc `YYYYMMDDHHMM_<short-descriptive-title>.md` so files sort by time and
  rarely collide across sessions.
- Keep each folder's `index.md` current: one row per doc (date, file, one-line
  summary), newest first.
- File a note at the end of every phase and at every hand-off. Record what was done,
  what is left, and the open decisions.
- Working docs only. Finalized ADRs belong in `docs/decisions/`, stories and epics in
  the tracker.
- Never put secrets or credentials here; the store is committed and shared. To keep a
  subfolder local, list it under `[agents] gitignore` in `.tara/config.toml`.

## Safety: destructive operations

Never run a destructive or irreversible command on your own. Ask the developer to run
it or to confirm it explicitly. Prefer the safe form first: dry-run flags,
`git status`, list what would change before changing it.

- **Rewriting history**: `git push --force`, `git reset --hard`, `git rebase` on a
  shared branch, `git commit --amend` on pushed commits.
- **Deleting work**: `rm -rf`, `git clean -fdx`, deleting branches, tags or remotes,
  dropping a database or table, `TRUNCATE`, `DROP`, destructive migrations.
- **Overwriting the environment**: recursive `chmod`/`chown -R`, editing files outside
  the repo, changing global git or system config.
- **Touching production or shared infrastructure**, in any way.

## Definition of done

- [ ] The new behaviour is covered by tests and `tara check` passes.
- [ ] The increment runs: an integration test plus a small runnable example.
- [ ] Docs updated; changelog updated if the change is user-facing.
- [ ] No secrets, credentials or local config staged; the developer makes the commit.
- [ ] Hand-off notes in `.agents/memory/` are current.
