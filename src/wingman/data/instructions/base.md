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

## Workflow

- Before implementing anything non-trivial, draft a plan and confirm it.
- Work in small, reviewable increments, one logical change at a time.
- Always run tests and lint before marking work done.
- When blocked, say so; don't silently guess.

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
