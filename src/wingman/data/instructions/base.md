# Core: Generic DevOps Cycle

These instructions apply to all projects regardless of stack. Focus is on the
plan, code, build, test, and release phases.

## Basic rules

- **Never commit code.** The developer always reviews and commits. Stage or edit
  files, draft commit messages, and open pull requests, but do not run `git commit`
  or `git push`. This follows the Linux Foundation agentic coding guidelines.
- Keep responses short and to the point. Be precise, don't flatter, and ask for
  clarification when unsure.
- Prefer open source and open standards over proprietary, closed alternatives.
- Prefer official documentation and code over blogs and articles.
- Don't reinvent tools or frameworks when a good existing one fits the job.
- Follow composable-stack principles: modular software with clear interfaces and
  contracts built on open standards.
- Work agile: every session produces a working, reviewable, tested increment.
- Standardize the code and the way of working, so any developer or agent can pick
  up another's work.

## Workflow: the fixed flow

Every change follows the same loop through the DevOps cycle (plan, code, test,
review, release). Don't skip steps; if one genuinely doesn't apply, say why.

1. **Understand** — read the story/task and its Definition of Done before touching code.
2. **Plan** — draft a short execution plan (files to change, edge cases, steps) and
   confirm it for anything non-trivial.
3. **Test first** — write a failing test for the next behaviour (TDD, see Testing).
4. **Implement** — the minimum code to pass, in small reviewable increments, one
   logical change at a time.
5. **Check** — run the gate (`wingman check`: lint, format, types, tests, security)
   and fix until it is green.
6. **Document** — update docs/README and the runnable example for new behaviour;
   update the changelog if the change is user-facing.
7. **Review & hand off** — verify the Definition of Done, then stage changes and draft
   a commit message for the developer. Never commit or push. Record the hand-off in
   the log (see below) so the next session can pick up.

When blocked, say so; don't silently guess.

## Agent memory / handover

- Write session notes, handover docs, and scratch memory to the `.agent/memory/`
  folder (framework-agnostic, created by `wingman init`). Its contents are
  git-ignored by default, so use it freely for work-in-progress state that the
  next session or agent can pick up.
- Keep these docs short and current: what was done, what's left, and any open
  decisions. Don't duplicate them into commits or the repo's real docs.
- Never put secrets or credentials here; git-ignored is not private.

### Hand-off log (queryable)

`.agent/tracking/handoffs.db` is a structured companion to the prose notes: an
append-only SQLite log of each flow phase's hand-off (see `docs/decisions/0001-*.md`).
Wingman creates the empty database; you write the rows. `sqlite3` is in the Python
standard library, so this needs no dependency.

- **When**: at the end of each phase (`/refine`, `/design`, `/implement`, `/review`,
  `/integrate`) and whenever you hand work off, append one row.
- **How**: insert one row with the standard-library `sqlite3` module (parameterised,
  so values never need escaping):

  ```sh
  uv run python - <<'PY'
  import json, sqlite3
  con = sqlite3.connect(".agent/tracking/handoffs.db")
  con.execute(
      "INSERT INTO handoffs (session_id, branch, phase, summary, next_step, files) "
      "VALUES (?, ?, ?, ?, ?, ?)",
      ("<session>", "<branch>", "<phase>", "<summary>", "<next_step>", json.dumps(["path/one.py"])),
  )
  con.commit()
  PY
  ```

- **Query** the whole log, newest first:

  ```sh
  uv run python - <<'PY'
  import sqlite3
  con = sqlite3.connect(".agent/tracking/handoffs.db")
  for row in con.execute("SELECT ts, phase, summary, next_step FROM handoffs ORDER BY ts DESC"):
      print(row)
  PY
  ```

  Prefer DuckDB's SQL ergonomics? It reads the SQLite file directly, no export:
  `uv run --with duckdb python -c "import duckdb; print(duckdb.sql(\"SELECT * FROM sqlite_scan('.agent/tracking/handoffs.db', 'handoffs') ORDER BY ts DESC\"))"`.

- The log is git-ignored by default; opt in to commit and push it via
  `[tracking] gitignore = false` in `.wingman/config.toml`. Never write secrets here.

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

## Testing

We work test-first (TDD): write a failing test, then the minimal code to pass, then
refactor. Test each behaviour once and keep tests independent, so one failure points
to one cause.

Every increment ships something runnable: integration tests plus a small example
(sample data or a short script) that demonstrates the new functionality. Stack-level
instructions cover the concrete test framework and layout.

## Definition of done

A change is done only when all of these hold. The pre-commit hook and `wingman check`
gate enforce the mechanical items; you are responsible for the rest.

- [ ] The new behaviour is covered by tests, and the full gate passes (`wingman check`:
  lint, format, types, tests, security).
- [ ] The increment runs: an integration test plus a small runnable example demonstrate it.
- [ ] Docs updated for the changed behaviour; changelog updated if the change is user-facing.
- [ ] No secrets, credentials, or local config staged; the developer makes the commit.
- [ ] Handover notes in `.agent/memory/` are current so the next session can continue.

## Git

- Never commit or push; the developer does that (see Basic rules).
- Commit messages (when drafting for the developer): imperative mood, subject line
  max 72 chars.
- Never stage secrets, credentials, or local config files.
- Branch names: `<type>/<short-description>` (e.g. `feat/add-auth`, `fix/null-pointer`).

## Code Review

- Prefer clear over clever. Code is read more than written.
- Flag todos and tech debt with `# TODO(name): reason` so they're searchable.
- Tests are not optional. New behaviour without tests is not done.

## CI / Build

- A failing build or test suite must be fixed before adding new work.
- If a CI step is flaky, flag it; don't re-run until it passes by luck.
- Keep build times fast: avoid unnecessary dependencies.

## Communication

- Surface ambiguity early. Wrong assumptions compound.
- Document decisions that aren't obvious from the code (why, not what).
