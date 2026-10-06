# Roadmap, missing issues, and runbook to a stable release

Date: 2026-10-02
Inputs: open issues #1 to #31, PRs #17 and #32, `.agents/review/202609011046_release-readiness-review.md`, and the current state of `feat/claude-code-support`.

## Current state

- The only release is the GitHub release `v1.0.0`, and nothing is published on PyPI as `tara-dev` yet.
- `pyproject.toml` says `1.1.0`, while `CHANGELOG.md` lists breaking changes under 1.1.0 (#21).
- PR #17 (`feat/claude-code-support`) is open and conflicts with `main`, and it carries uncommitted WIP (hooks, catalog instructions, rebuild).
- `main` has no branch protection, and CI tests only one Python version (#22).
- Daniel is working on oxivault (#28, #29) and the superpowers theme (#31, PR #32).
- Thomas uses Matt Pocock's skills (`mattpocock/skills`, MIT), which have no issue yet.

## Principle for external skills

Tara references third-party skills and does not copy them.
An external skill gets an import route (an `index.toml` theme, `tara skill add`, and a commit pin in `.tara/skills.lock`) and is restored on demand.
Neither the Tara package nor a consuming repository should have to commit the skill's files.
This makes #25 (gitignore vendored skills) and #26 (rebuild restores all skills) release requirements, because restoring from the lock must be reliable once the files are no longer committed.

## Superpowers as a default skill

Daniel owns this through #31 and PR #32.
This section records how it should be done so the review of PR #32 and later themes follow the same route.

`tara add skill obra/superpowers --path test-driven-development` works today.
There are three levels of "default", and they need different changes.

| Level | What it means | Change needed |
| ----- | ------------- | ------------- |
| Per repository | Run `tara skill add` once. It is recorded in `.tara/skills.toml` and restored by `tara rebuild` or `tara skill sync`. | None. |
| Offered by Tara | The `superpowers` theme shows up in the `tara init` and `tara add` pickers, and `tara skill add superpowers` works. | Data only: PR #32 adds the theme to `src/tara/data/skills/index.toml`. It ships with the next release. |
| Preselected | The theme is checked by default in the picker. | Code: skill themes ignore a `default` key today. Only MCP entries read it (`src/tara/catalog.py:154`). This needs a `default` field on `SkillSet`, and the picker must pass it through (about 5 lines plus a test). |

PR #32 currently includes `dispatching-parallel-agents`, `systematic-debugging`, `test-driven-development`, and `verification-before-completion`.
The Copilot review flagged `brainstorming`, `writing-plans`, and `executing-plans` because they depend on excluded workflow skills, and those three are no longer in the diff.
A cross-reference check of the four remaining skills found two points for the PR #32 review.

- `test-driven-development` references `superpowers:writing-skills`, which is excluded because it overlaps with `skill-creator`. The reference is a pointer and not a required step, so it is acceptable, but the PR description should mention it.
- `systematic-debugging` (283 lines) and `test-driven-development` (330 lines) exceed the 200-line `SKILL.md` limit, so `tara audit` will warn on them. Tara cannot shorten upstream skills, so the theme should accept the warning.

PR #32 also edits `README.md`, so remember to regenerate the CLI docs if the theme list is generated.

## Matt Pocock skills

Tara does not curate or exclude skills from this repository.
Users browse it with `tara skill list mattpocock` and pick what they want (draft E).
Tara shows a warning on skills that conflict with its way of working, such as `implement-spec`, which commits and opens pull requests, and the skills that need `/setup-matt-pocock-skills`.
`tdd` stays available, because it fits Tara's test-first step; the warning only advises installing one TDD skill.

The warnings and the ideas worth adopting in Tara's own instructions are in `.agents/review/202610041740_mattpocock-skills-conflicts-and-ideas.md`.

## Roadmap

### M0: land the in-flight work

1. Commit the WIP on `feat/claude-code-support` (hooks, catalog instructions, rebuild, base instructions), with the gate green.
2. Rebase PR #17 onto `main` and resolve the conflicts.
3. Split anything that is not Claude support out of PR #17 if review requires it.
4. Daniel lands PR #32 (superpowers theme). It is data only, so it does not block the release.
5. Fix the five tests that fail on HEAD (draft A below) before PR #17 merges.

### M1: release blockers (target 2.0.0-rc1)

| Issue | Topic |
| ----- | ----- |
| #18 | Integration lifecycle and strict config: rerun `init` keeps integrations, prune stale outputs, atomic config writes. |
| #20 | Reject symlinked ancestors and keep every generated path inside the repository. |
| #30 | `copilot-instructions.md` gets overwritten. Ask to overwrite, merge, or skip, or move Tara's content into a separate `tara.instructions.md`. |
| #24 | `rebuild` drops locally modified catalog artifacts from the manifest. |
| #26 | `rebuild` does not restore library skills. |
| #25 | Offer to gitignore vendored third-party skills (follows from the principle above). |
| #21 | SemVer decision. The documented breaking changes and the empty PyPI history favour releasing as 2.0.0 with the deprecated aliases kept. |
| #34 | Preselectable skill themes (`default = true`). |
| #35 | `mattpocock` theme. |
| #42 | Registry spike and ADR. Decide the lock and config schema parts before 2.0.0. |
| draft B | The default `git` MCP server lets agents commit, which contradicts the never-commit rule. |
| draft C | Overlapping Python rules are loaded from both the always-on `python.md` and the scoped `python.instructions.md`. |

### M2: release engineering

| Issue | Topic |
| ----- | ----- |
| #22 | Python 3.12 to 3.14 matrix, build once, smoke-test the wheel and sdist, trusted publishing to `tara-dev`, attestations. |
| #37 | Protect `main` and require the gate, pre-commit, matrix, and package smoke jobs. |
| #38 | `SECURITY.md`, support policy, and deprecation policy. |
| #36 | Upstream skill index health check in CI. |
| #39 | End-to-end fixture-repository tests for init, sync, integration add/remove, legacy migration, and uninstall. |
| #40 | Record the source and license of third-party skills in the lock. |
| draft D | The skill theme list is maintained by hand in both `README.md` and `docs/skills.md`. |

### M3: release candidate and stable

Follow `.agents/runbooks/release-a-new-version.md`.
Publish `2.0.0rc1`, use it for at least a week, and promote the same artifacts to `2.0.0`.

### After stable (2.x minor releases)

| Issue | Topic |
| ----- | ----- |
| #23 | Sensitivity scan, run pre-push. |
| #41 | Token cost of skills in the picker and audit. |
| #43 | Contributed stacks through the registry, such as Rust and TypeScript (sub-issues #44 to #48). Python is the only stack Tara sets up in full. Proposed edits are in the drafts doc. |
| later | Retention and cleanup for `.agents/`: the store grows with every session, and not every plan, review, or memory note needs to be kept. Runbooks are always kept. Not drafted yet. |
| #28, #29 | Vault-LD ADR and oxivault integration (Daniel). Step 1 of #29 is an import route and needs no Tara change, so it does not block. |
| #19, #4 | Open canonical formats and the Open Plugin spec. These overlap, so merge #4 into the #19 spike. |
| #1, #3 | OpenCode and goose support. Both depend on the #19 outcome. |
| #15 | `maplib` and `ottr` themes (data only, can ship any time). |
| #14, #9 | Storage spike and roborev features. Re-scope against oxivault and close what it covers. |

## Missing issues

The seven issues found on 2026-10-02 were created as #34 to #40, with #41 added for token cost.
Milestones `2.0.0` and `2.x` exist, and every open issue is assigned to one of them.
Issue hygiene that remains: #9 and #31 have empty bodies, and #14 still refers to wingman paths.

### Gaps found on 2026-10-03 (posted as #49 to #55)

A check of the open issues, the failing tests, and the earlier plans and reviews found five gaps that cause inconsistent behaviour and are not tracked.
The review copies of the issue bodies are in `.agents/plan/202610021040_stable-release-issue-drafts.md`.

| Issue | Title | Milestone | Why it matters |
| ----- | ----- | --------- | -------------- |
| #49 | Fix the five tests that fail on HEAD | 2.0.0 (M0) | The gate is red, so no change can be verified and PR #17 cannot merge. |
| #50 | Stop the default `git` MCP server from contradicting the never-commit rule | 2.0.0 (M1) | Agents get `git_commit`, `git_add`, and `git_reset` by default, while the instructions forbid committing. |
| #51 | Load Python rules from one place | 2.x | Overlapping guidance lives in two files that drift apart and are both loaded. Changing generated output fits a major release. |
| #52 | Generate the skill theme list from `index.toml` | 2.x | The list exists in two docs by hand, and PR #32 already updates only one of them. |
| #53 | Browse and add skills from one index of Tara and external sources | 2.x | One index references Tara's own skills and external repositories without copying them, and users browse and pick from the upstream folders. It replaces #35 and the curated theme in PR #32. |
| #54 | Move the language-neutral testing rules to `base.md` | 2.x | Stack files then hold only the runner, so a Rust or TypeScript stack does not inherit the uv and pytest setup. |
| #55 | Write backlog drafts and post-mortems to `.agents/` | 2.x | `tara new` writes one file per story, epic, bug, or spike to `docs/`, which duplicates the board. |

Two smaller items fold into existing issues instead of new ones.

- #40: also verify that installed skill files still match the lock, and report a mismatch in `tara audit`.
- #38: document that `tara check` runs the commands in a repository's `.tara/checks.toml`, so running it in an untrusted clone executes that repository's commands.

## Release runbook

The release procedure lives in `.agents/runbooks/release-a-new-version.md`.
The steps to close the 2.0.0 blockers are in `.agents/plan/202610041800_release-2.0.0-execution-runbook.md`.

## Open decisions

1. Release as 2.0.0 or keep 1.x compatibility for 1.1.0 (#21).
2. Whether superpowers should be preselected or only offered. Daniel decides this in PR #32, and preselection needs the new "preselectable skill themes" issue.
3. Which debugging skill to recommend, superpowers `systematic-debugging` or Matt Pocock's `diagnosing-bugs`.
4. Which ideas from the Matt Pocock review to adopt in Tara's own instructions.
5. The #30 approach: prompt to merge, or a separate `tara.instructions.md`.
6. Draft B: remove `git` from the defaults, or keep it and deny its write tools per integration.
7. Draft C: keep the Python rules always-on in `python.md` or move them to the scoped file only.
8. Draft E: close #35 in favour of E, and ask Daniel to replace the curated theme in PR #32 with a docs example of `tara skill add obra/superpowers`.
