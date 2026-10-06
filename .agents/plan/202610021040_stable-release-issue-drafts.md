# Issue drafts for the stable release

Date: 2026-10-02
These are the bodies of #33 to #48.
#33 to #41 were posted before review, and #42 to #48 were posted after review of the design docs.
Edit them here, and the approved text will be synced back to the issues.

## #34 Allow skill themes to be preselected in the picker (2.0.0)

### Problem

Skill themes in `src/tara/data/skills/index.toml` cannot be preselected in the `tara init` and `tara add` pickers.
Only MCP catalog entries read a `default` key (`src/tara/catalog.py:154`), and skill themes are always built with `checked=False` (`src/tara/catalog.py:102-107`).

### Required changes

- Add an optional `default` field to `SkillSet` and read it from `[sets.*]` in `index.toml`.
- Pass it through as `checked` when the picker items are built.
- Document the key in the `index.toml` header comment and the README.

### Definition of done

- [ ] A theme with `default = true` is checked in the picker, and a theme without it is not.
- [ ] Non-interactive `tara init` behaviour is unchanged.
- [ ] Tests cover both cases.

Part of #33.

## #35 Add a mattpocock skill theme (2.0.0)

Superseded by draft E.
Proposal: close #35 with a comment that points to draft E and to the conflict warnings below.

### Comment for #35

Tara will not curate a selection of `mattpocock/skills`.
With draft E, users browse the repository with `tara skill list mattpocock` and pick the skills they want.
Tara shows a warning on skills that conflict with its workflow, for example `implement-spec` (commits and opens pull requests) and the skills that need `/setup-matt-pocock-skills`.
@thomas, does this work for you?

## #36 Add a scheduled health check for the skill index (2.0.0)

### Problem

Every theme in `src/tara/data/skills/index.toml` tracks a moving branch (`main` or `master`).
When an upstream repository renames or removes a skill folder, or changes the `name:` in a `SKILL.md`, `tara skill add <theme>` breaks, and nobody notices until a user runs it.

### Required changes

- Add a scheduled CI job (weekly, and on changes to `index.toml`) that resolves every theme against its upstream `ref`.
- Fail when a member path is missing or a `SKILL.md` `name:` does not match the member name.
- Report each skill's size, so token-heavy changes upstream are visible.

### Definition of done

- [ ] The job runs on a schedule and on pull requests that touch `index.toml`.
- [ ] A broken member fails the job with a message that names the theme and the skill.

Part of #33.

## #37 Protect main and require release checks (2.0.0)

### Problem

`main` has no branch protection, so a pull request can merge with a red gate and stable releases are not tied to verified commits.

### Required changes

- Protect `main`: require pull requests, require review, and block force pushes and deletion.
- Require the gate, pre-commit, Python compatibility matrix, and package smoke jobs from #22.
- Document the required checks in `CONTRIBUTING.md` or the release runbook.

### Definition of done

- [ ] A pull request with a failing required check cannot merge.
- [ ] The required check names match the job names in `.github/workflows/`.

Depends on #22 for the matrix and smoke jobs. Part of #33.

## #38 Add SECURITY.md, support policy, and deprecation policy (2.0.0)

### Problem

The release-readiness review lists missing governance documents as a gap for a stable release.
Users have no documented way to report a vulnerability, no statement of which versions are supported, and no deprecation policy for CLI flags and config keys.

### Required changes

- Add `SECURITY.md` with a private reporting route (GitHub private vulnerability reporting).
- Document the supported Tara versions and Python versions.
- Document the deprecation policy: deprecated CLI aliases and config keys keep working with a warning for at least one minor release and are removed only in a major release.

### Definition of done

- [ ] `SECURITY.md` exists and private vulnerability reporting is enabled.
- [ ] The support and deprecation policy is linked from the README.

Part of #33.

## #39 Add end-to-end lifecycle tests in fixture repositories (2.0.0)

### Problem

File transformations are well unit-tested, but nothing exercises the full lifecycle on a real repository with the built package.
Regressions in rerun idempotency, restore from the lockfile, and integration removal are found by users.

### Required changes

Add integration tests that run the installed wheel in temporary fixture repositories and cover these scenarios.

- `tara init` with every integration, then a rerun that changes nothing.
- `tara skill add <theme>`, deletion of the skill folders, and restore through `tara rebuild`.
- A hand-edited generated file is skipped in non-interactive mode.
- `tara integrations` add and remove touches only Tara-owned files.
- A 1.0 `.tara/config.toml` migrates without errors.
- Clean removal of all Tara-generated files.

### Definition of done

- [ ] The scenarios run in CI against the built wheel.
- [ ] They are required checks for release (see the branch protection issue).

Part of #33.

## #40 Record source and license of third-party skills in the lock (2.0.0)

### Problem

Tara references third-party skills and does not vendor them.
After #25, the skill files may be gitignored, so a reader of a consuming repository has no visible provenance or license for the installed skills.

### Required changes

- When a skill is installed, record its upstream repo, commit, and SPDX license in its `.tara/skills.lock` entry.
- Show the source and license in `tara skill list`.
- Keep the lockfile backwards compatible, so entries without a license still load.

### Definition of done

- [ ] New lock entries contain repo, commit, and license.
- [ ] Old lockfiles load without errors.
- [ ] `tara skill list` shows the source and license.

Related to #25. Part of #33.

## #41 Show the token cost of skills in the picker and audit (2.x)

### Problem

Some skill sets are large and expensive in context tokens.
For example, superpowers `systematic-debugging` has 283 lines plus 10 support files, and `test-driven-development` has 330 lines.
Users cannot see this cost when they pick a theme, so they install more context than they need.

### Required changes

- Estimate each skill's token footprint (for example, characters divided by 4) for the `SKILL.md` and for its total files.
- Show the estimate per theme in the `tara init` and `tara add` pickers and in `tara skill list`.
- Report it in `tara audit` next to the existing line-count warning.
- Point users in the picker hint to `tara skill add <skill>`, which already installs one member of a theme.

### Definition of done

- [ ] The pickers and `tara skill list` show an approximate token cost.
- [ ] `tara audit` reports the estimate per skill.

Part of #33.

## #33 Tracking: roadmap to a stable 2.0.0 release

Tracking issue for the first stable release on PyPI (`tara-dev`).
The full plan and release runbook are in `.agents/plan/202610021025_stable-release-roadmap.md`.

### Current state

- The only release is the GitHub release `v1.0.0`, and nothing is published on PyPI yet.
- `pyproject.toml` says `1.1.0`, while `CHANGELOG.md` lists breaking changes under 1.1.0 (#21).
- PR #17 conflicts with `main`, `main` has no branch protection, and CI tests only one Python version.

### Principle for external skills

Tara references third-party skills and does not copy them.
An external skill gets an import route (an `index.toml` theme, `tara skill add`, and a commit pin in `.tara/skills.lock`) and is restored on demand.
Neither the Tara package nor a consuming repository should have to commit the skill's files.
This is why #25 and #26 are release requirements.

### M0: land the in-flight work

- [ ] Commit the WIP on `feat/claude-code-support` with the gate green.
- [ ] Rebase #17 onto `main` and resolve the conflicts.
- [ ] #31 / #32 superpowers theme (@dkapitan). Data only, so it does not block the release.

### M1: release blockers (2.0.0-rc1)

- [ ] #18 Integration lifecycle and strict config.
- [ ] #20 Keep generated paths inside the repository.
- [ ] #30 Do not overwrite `copilot-instructions.md`.
- [ ] #24 `rebuild` keeps locally modified catalog artifacts.
- [ ] #26 `rebuild` restores library skills.
- [ ] #25 Offer to gitignore vendored third-party skills.
- [ ] #21 SemVer decision. The breaking changes and the empty PyPI history favour 2.0.0 with the deprecated aliases kept.
- [ ] #34 Preselectable skill themes (`default = true` for `[sets.*]`).
- [ ] #35 `mattpocock` skill theme.
- [ ] #42 Spike and ADR: move the catalog to a fetched registry outside `src/`. Before 2.0.0, decide only the lock and config schema parts.

### M2: release engineering

- [ ] #22 Release pipeline: Python 3.12 to 3.14 matrix, build once, smoke tests, trusted publishing, attestations.
- [ ] #37 Protect `main` and require the gate, pre-commit, matrix, and package smoke jobs.
- [ ] #38 `SECURITY.md`, support policy, and deprecation policy.
- [ ] #36 Scheduled CI health check that resolves every `index.toml` theme against its upstream `ref`.
- [ ] #39 End-to-end tests in fixture repositories for init, sync, integration add/remove, legacy migration, and uninstall.
- [ ] #40 Record the upstream repo, commit, and license of installed third-party skills in the lock entry.

### M3: release candidate and stable

- [ ] Publish `2.0.0rc1` following the runbook.
- [ ] Use the release candidate for at least a week and collect feedback.
- [ ] Promote the same code to `2.0.0` and verify `uvx --from tara-dev tara` from a clean machine.

### After stable (2.x)

- #23 Sensitivity scan, run pre-push.
- #41 Show the token cost of skills in the picker and audit.
- #43 Rust and TypeScript stacks (@dkapitan), with sub-issues #44 to #48. Stack content will live in the registry, so it is versioned separately from the package.
- #28, #29 Vault-LD and oxivault (@dkapitan). Step 1 of #29 is an import route and needs no Tara change.
- #19 Open canonical formats. Proposal: merge #4 into this spike.
- #1, #3 OpenCode and goose, after #19.
- #15 `maplib` and `ottr` themes (data only, can ship any time).
- #14, #9 Re-scope against oxivault and close what it covers.

### Proposal for #31 (superpowers)

`tara add skill obra/superpowers --path test-driven-development` already works.
There are three levels of "default", and they need different changes.

| Level | What it means | Change needed |
| ----- | ------------- | ------------- |
| Per repository | Run `tara skill add` once. It is recorded in `.tara/skills.toml` and restored by `tara rebuild` or `tara skill sync`. | None. |
| Offered by Tara | The theme shows up in the `tara init` and `tara add` pickers, and `tara skill add superpowers` works. | Data only, as in #32. It ships with the next release. |
| Preselected | The theme is checked by default in the picker. | Code. Skill themes ignore a `default` key today, and only MCP entries read it (`src/tara/catalog.py:154`). This is the "preselectable skill themes" item above. |

Recommendation: offer superpowers as an opt-in theme and do not preselect it.
The set is large and token-expensive, but single skills are useful, and `tara skill add <skill>` installs one member of a theme.
#41 makes the token cost visible in the picker.

Review notes for the four skills in #32:

- `test-driven-development` points to the excluded `superpowers:writing-skills`. That is a pointer and not a required step, so it is acceptable, but the PR description should mention it.
- `systematic-debugging` (283 lines) and `test-driven-development` (330 lines) exceed the 200-line `SKILL.md` limit, so `tara audit` warns. Tara cannot shorten upstream skills, so the theme should accept the warning.
- Recommend one TDD skill only. Tara warns when a second TDD skill is installed, and does not exclude either.

### Matt Pocock skills

No curated theme. Users pick skills themselves, and Tara warns on conflicts (draft E).

### Open decisions

- [ ] 2.0.0 or 1.1.0 (#21).
- [ ] Superpowers preselected or only offered (@dkapitan). Proposal: offer it and do not preselect it, because the set is large and token-expensive (see below).
- [ ] Recommended debugging skill: superpowers `systematic-debugging` or `diagnosing-bugs`.
- [ ] Which ideas from the Matt Pocock review to adopt in Tara's own instructions.
- [ ] #30 approach: prompt to merge, or a separate `tara.instructions.md`.

## #42 Spike and ADR: move the catalog to a fetched registry outside src/ (2.0.0)

### Question

Should Tara's catalog (templates, instructions, agents, prompts, internal skills, hooks, and MCP entries) move from `src/tara/data/` to a `registry/` folder in this repository that Tara fetches from GitHub, instead of shipping it inside the package?

### Motivation

- The catalog can grow and get updates without a package release, and the package stays small.
- Tara's own content uses the same import route as third-party skills: reference it, pin it in the lock, and restore it on demand.
- A registry with its own CI can enforce size and token budgets on every skill.

### Problems to solve

| Topic | Direction |
| ----- | --------- |
| Offline use | Keep a small core bundled (base instructions, config templates, standards), cache fetched content, and fall back to the cache with a warning. |
| Compatibility | Pin the registry to a tag or commit per Tara version or per repository, and check a format version in `registry.toml`. |
| Ownership checks | `_matches_catalog_source` (`src/tara/cli.py:1108`) compares against the bundled copy. Replace it with content hashes in the lock. |
| Supply chain | Hooks run code and MCP entries start processes, so fetch only pinned commits and never a branch head. |
| Access | Use `gh` or a token when available, and allow a registry URL override in `.tara/config.toml`. |
| Testing | Use a local registry fixture in tests, and validate the registry in its own CI job (#36). |

### Timing

The lock format and config schema are the surface 2.0.0 should keep stable.
Decide the ADR before 2.0.0 and add only the schema parts (registry ref, content hashes in the lock).
Implement remote fetching in 2.x with the bundled catalog as fallback, so the change is not breaking.

### Spike (timebox 2 days)

- [ ] Prototype fetching `registry/` at a pinned commit with a cache and an offline fallback.
- [ ] Replace the ownership comparison with lock content hashes for one artifact kind.
- [ ] Measure `tara init` with a cold and a warm cache.
- [ ] Write the ADR with the decision and the migration path for existing configs.

### Open questions

1. Registry in this repository or a separate `tara-registry` repository?
2. Which content stays bundled as the offline core?
3. Is the registry size and token budget a hard limit or a warning?

Part of #33.

## #43 Add Rust and TypeScript stacks (2.x)

### Goal

Support Rust and TypeScript next to Python, including repositories that mix them (for example Python with a PyO3 extension, or a TypeScript frontend).

### How a stack works today

A stack is mostly data looked up by name: `data/instructions/<stack>.md`, `data/mcp/<stack>.json`, `data/checks/<stack>.toml`, and `data/standards/<stack>/`.
Python is still hard-coded in `tara init` (`src/tara/cli.py:283-286`), in `standards.py` (only `pyproject.toml`), in `tara sync` (dependencies only from `pyproject.toml`), in the `packages` keys (PyPI names only), and in the config (one `stack` string).

### Plan

- Stack rules become scoped instruction files (`rust.instructions.md` with `**/*.rs`, `typescript.instructions.md` with `**/*.ts,**/*.tsx`), so they only load for matching files and do not cost tokens elsewhere.
- The config holds a list of stacks, with silent migration from `stack`.
- `tara sync` reads `Cargo.toml` and `package.json`, and `packages` entries accept an ecosystem prefix.

### Proposed tooling baselines

| Category | Python (current) | Rust | TypeScript |
| -------- | ---------------- | ---- | ---------- |
| Format | `ruff format` | `cargo fmt --check` | Biome or Prettier |
| Lint | `ruff check` | `cargo clippy --all-targets -- -D warnings` | Biome or ESLint |
| Types | `ty check` | Covered by the compiler | `tsc --noEmit` with `strict` |
| Test | `pytest` | `cargo test` or `cargo nextest run` | `vitest run` |
| Security | `uv audit` | `cargo deny check` or `cargo audit` | `pnpm audit` or `npm audit` |

### Milestone

This work is planned for 2.x, after the stable release.
Stack content will live in the catalog registry (see the registry spike), so it is versioned separately from the Tara package.

### Request for @dkapitan

Skills written by an agent only contain what the agent already knows, so we prefer existing human-curated skills for Rust and TypeScript, referenced through the skill index and not copied.

- Have you found good Rust or TypeScript skills or instruction sets we could reference?
- Which TypeScript package manager and linter do you prefer? For Rust, `cargo nextest` or `cargo test`, and `cargo deny` or `cargo audit`?
- Do you want to own the Rust and TypeScript content?

@dkapitan let me know if this works for you.

Part of #33.

## #44 Support a list of stacks in config and tara init (2.x)

### Problem

`.tara/config.toml` holds one `stack` string (`src/tara/config.py:123`), so a repository that mixes Python with Rust or TypeScript cannot select both.

### Required changes

- Add `stacks: list[str]` and read a legacy `stack = "python"` as `stacks = ["python"]` without a warning.
- `tara init --stack` accepts a comma-separated list, like `--integrations`, and stores explicit names.
- Instructions, MCP servers, checks, and standards are merged across all configured stacks.

### Definition of done

- [ ] Old configs with `stack` load and are written back as `stacks`.
- [ ] Two stacks produce merged checks and MCP servers without duplicates.
- [ ] Tests cover migration and merging.

## #45 Read Cargo.toml and package.json dependencies in tara sync (2.x)

### Problem

`tara sync` reads direct dependencies from `pyproject.toml` only (`src/tara/sync.py:90-100`), and `packages` entries in `skills/index.toml` and `catalog/instructions/index.toml` are PyPI names without an ecosystem.
Package-triggered skills and instructions never fire for Rust or TypeScript projects.

### Required changes

- Read direct dependencies from `Cargo.toml` and `package.json` as well.
- Accept an ecosystem prefix in `packages`, such as `"crates:polars"` and `"npm:@duckdb/node-api"`.
- A bare name keeps meaning PyPI, so existing indexes keep working.

### Definition of done

- [ ] A `Cargo.toml` or `package.json` dependency triggers the matching theme or instruction file.
- [ ] Existing bare names behave as before.
- [ ] Tests cover each manifest type.

## #46 Make standards and tara init stack-generic (2.x)

### Problem

`tara init` runs the standards and dev-tool steps only for the `python` stack (`src/tara/cli.py:283-286`), and `standards.py` only compares against `pyproject.toml`.

### Required changes

- Run the standards step for every configured stack.
- Add a comparison per manifest type (`pyproject.toml`, `Cargo.toml` with `rustfmt.toml` and `clippy.toml`, `package.json` with `tsconfig.json`).
- Merge the per-stack pre-commit configs into one `.pre-commit-config.yaml`.
- Keep the standards report-only for existing manifests.

### Definition of done

- [ ] `tara standards` reports per stack.
- [ ] Python behaviour is unchanged.

## #47 Add the Rust stack (2.x)

### Goal

Add Rust as a stack.
Prefer referencing existing human-curated skills over writing new ones, because agent-written skills only contain what the agent already knows.

### Required changes

- A short scoped `rust.instructions.md` with `applyTo: "**/*.rs"`.
- `data/checks/rust.toml` with the tooling baseline agreed in the parent issue.
- `data/standards/rust/` with the pre-commit hooks and the config baseline.
- Index entries for good existing Rust skills, referenced and not copied.

### Definition of done

- [ ] `tara init --stack rust` sets up instructions, checks, and standards.
- [ ] `tara check` runs the Rust gate in a sample project.
- [ ] The README lists the stack.

## #48 Add the TypeScript stack (2.x)

### Goal

Add TypeScript as a stack.
Prefer referencing existing human-curated skills over writing new ones, because agent-written skills only contain what the agent already knows.

### Required changes

- A short scoped `typescript.instructions.md` with `applyTo: "**/*.ts,**/*.tsx"`.
- `data/checks/typescript.toml` with the tooling baseline agreed in the parent issue.
- `data/standards/typescript/` with the pre-commit hooks and the config baseline.
- Index entries for good existing TypeScript skills, referenced and not copied.

### Definition of done

- [ ] `tara init --stack typescript` sets up instructions, checks, and standards.
- [ ] `tara check` runs the TypeScript gate in a sample project.
- [ ] The README lists the stack.

# Proposed edits to #43 to #48 (not posted)

Scope decision on 2026-10-04: Python is the only stack Tara sets up in full.
Other stacks are contributed through the registry and maintained by their contributor.
See `.agents/design/202610021055_rust-typescript-stacks.md`.

## #43 new title: Let contributors add stacks through the registry (2.x)

### Goal

Let anyone add a language stack, such as Rust or TypeScript, without code changes in Tara.
Python stays the only stack with full setup help from Tara's maintainers.

### Stack contract

A stack is a folder `stacks/<name>/` in the registry.

- `stack.toml` (required): name, description, and owner.
- `<name>.instructions.md` (required): scoped instructions with their own `applyTo`.
- `checks.toml` (optional): commands for `tara check`.
- `pre-commit.yaml` (optional): hooks that `tara init` offers to add.
- `mcp.json` (optional): extra MCP servers.

Tara does not compare manifests, install toolchains, or read dependencies for contributed stacks.

### Request for @dkapitan

- Do you want to own the Rust and TypeScript stacks?
- Have you found good human-written Rust or TypeScript skills? Users can add those directly from their repositories (draft E).

@dkapitan let me know if this works for you.

## #44: no change

## #45: close as not planned

Comment: Tara will not read `Cargo.toml` or `package.json` dependencies.
Users pick skills for any language from external sources themselves, which draft E covers.

## #46 new title: Install a contributed stack from its folder (2.x)

### Required changes

- `tara init` and `tara rebuild` install the files of every configured stack that follows the contract.
- Show the stack's owner in `tara init`.
- Keep the Python-only steps as they are.

### Definition of done

- [ ] A sample stack folder with only `stack.toml` and an instructions file installs without code changes.
- [ ] Optional `checks.toml` and `pre-commit.yaml` are picked up when present.
- [ ] Python behaviour is unchanged.

## #47 and #48: data only, owned by the contributor

Replace the required changes with: a stack folder that follows the contract in #43, maintained by its contributor.
Remove the standards comparison and the dependency triggers.

## Draft F: Move the language-neutral testing rules to base.md (2.x)

Move test-first, GIVEN/WHEN/THEN, mocking only at system boundaries, and the test anti-patterns from `python.md` to `base.md`.
`python.md` keeps only `uv`, `pytest`, `parametrize`, and the `tests/` layout.

# Drafts not yet posted

Found on 2026-10-03 while checking the plan for untracked defects.
These are not on the board.

## Draft A: Fix the five tests that fail on HEAD (2.0.0)

### Problem

`tara check` fails on commit `4188e01` of `feat/claude-code-support`, so no change on the branch can be verified and PR #17 cannot merge.
The failures do not depend on uncommitted work.

- `tests/test_hooks.py::test_merge_does_not_deduplicate_across_different_matchers`
- `tests/test_hooks.py::test_merge_appends_only_missing_actions_for_the_same_matcher`
- `tests/test_hooks.py::test_install_rejects_a_symlinked_settings_file`
- `tests/test_hooks.py::test_install_rejects_a_symlinked_settings_directory`
- `tests/test_catalog.py::test_install_instruction_skips_a_symlinked_destination_directory`

### Required changes

- Decide per test whether the code or the test is wrong, and fix that side.
- Fix the symlink cases with the shared containment check from #20, so the hook and catalog installers use the same rule.

### Definition of done

- [ ] `tara check` passes on the branch.
- [ ] No test is skipped or marked as expected to fail to get there.

## Draft B: Stop the default git MCP server from contradicting the never-commit rule (2.0.0)

### Problem

`git` is a default MCP server (`src/tara/data/mcp/catalog.toml:26-31`).
`mcp-server-git` exposes write tools such as `git_add`, `git_commit`, `git_reset`, `git_checkout`, and `git_create_branch`.
The base instructions tell agents never to commit, so the default setup grants a capability the instructions forbid, and the outcome depends on whether the agent follows the prose.

### Required changes

- Remove `default = true` from the `git` server, so it stays available in the picker but is not selected by default. Agents can read history through the shell.
- Add a `tara audit` finding when `.mcp.json` configures the `git` server while the instructions forbid committing.
- Note the change in the changelog.

### Definition of done

- [ ] A fresh `tara init` cannot give an agent a commit tool by default.
- [ ] `tara audit` reports the contradiction in an existing repository.
- [ ] Existing repositories keep their current `.mcp.json` until the developer changes it.

## Draft C: Load Python rules from one place (2.x)

### Problem

Python guidance lives in the always-on `src/tara/data/instructions/python.md`, which is appended to `copilot-instructions.md`, and in the scoped catalog file `python.instructions.md` (`applyTo` Python files).
A repository with both loads overlapping rules twice, and the two files drift apart.
Earlier plans parked this because it changes generated output for every repository.

### Required changes

- Move the Python coding rules into the scoped `python.instructions.md` and keep only stack-level tooling commands in `python.md`, or remove `python.md`.
- Install the scoped file by default for the Python stack.
- Regenerate `copilot-instructions.md` through the existing ownership checks, so a hand-edited file is not replaced (#30).

### Definition of done

- [ ] Each Python rule exists in exactly one bundled file.
- [ ] `tara init` for a Python repository installs the scoped file.
- [ ] `tara rebuild` on an existing repository updates the generated `copilot-instructions.md` and leaves a hand-edited one alone.
- [ ] The changelog describes the change in generated output.

## Draft D: Generate the skill theme list from index.toml (2.x)

### Problem

The list of skill themes is written by hand in both `README.md` and `docs/skills.md`.
PR #32 already updates only the README, so the two lists drift apart.

### Required changes

- Generate the theme list from `src/tara/data/skills/index.toml`, the same way `docs/cli.md` is generated.
- Keep the list in `docs/skills.md` only, and link to it from the README.
- Fail the docs check when the generated list is out of date.

### Definition of done

- [ ] Adding a theme to `index.toml` and regenerating the docs updates the list.
- [ ] The README no longer has its own copy.

## Draft E: Browse and add skills from one index of Tara and external sources (2.x)

### Problem

Tara's own skills and external skills are handled in different ways.
Bundled skills come from the catalog, external collections need a curated theme in `index.toml`, and anything else needs a git URL plus the exact `--path` of one skill.
`tara skill list` only shows external skills that are already installed, so users cannot see what is available.

### Proposal

Use one index of sources.
A source is a repository plus an optional folder, and Tara's own skills are one of those sources.
The index only references external repositories and never copies their content.
The skills inside a source are read from the repository's own folders at a pinned commit, so nobody curates members by hand.

```toml
[sources.tara]
repo = "https://github.com/plugin-healthcare/tara"
path = "src/tara/data/catalog/skills"

[sources.superpowers]
repo = "https://github.com/obra/superpowers"
path = "skills"

[sources.mattpocock]
repo = "https://github.com/mattpocock/skills"
path = "skills"
```

### Required changes

- `tara skill list` shows the installed skills grouped by source, with the upstream folder as category.
- `tara skill list <source>` browses one source without installing, and also accepts `owner/repo` for a repository that is not in the index.
- `tara skill add <source>` opens a picker in an interactive session. `tara skill add <source>/<skill>` adds one skill without a prompt.
- Every source other than Tara's own is shown as external wherever it appears: in `tara skill list`, in the picker, and in the output of `tara skill add`.
  The label names the upstream repository and its license, and states that Tara does not maintain the content.
- Adding an external skill prints the repository, the pinned commit, and the license before it installs.
- A source in the index can carry a short note per skill, which Tara shows in the list, in the picker, and before it installs the skill.
  Notes warn about conflicts with Tara's workflow and never hide or block a skill.

```toml
[sources.mattpocock.notes]
implement-spec = "Commits and opens pull requests. Conflicts with Tara's rule that only the developer commits."
tdd = "Install only one TDD skill."
```

- Every added skill is recorded on its own in `.tara/skills.toml` and `skills.lock`, so `rebuild`, `update`, and `remove` work unchanged.
- Existing theme names and `--path` keep working as aliases.

### Definition of done

- [ ] `tara skill list mattpocock` shows the skills grouped by `engineering`, `productivity`, and `misc`.
- [ ] `tara skill add superpowers/test-driven-development` installs one skill and pins it in the lock.
- [ ] `tara skill add obra/superpowers` works without an index entry.
- [ ] External skills are labelled as external with their repository and license in the list, the picker, and the add output.
- [ ] A note on a skill is shown in the list, the picker, and before install, and the skill can still be installed.
- [ ] Existing theme names from 1.x still install the same skills.
- [ ] The index format matches the registry decision in #42.

## Draft G: Write backlog drafts and post-mortems to .agents/ (2.x)

Posted as #55.

Labels: enhancement.
Milestone: 2.x.

### Problem

`tara new story|epic|bug|spike` writes one file per item to `docs/stories/`, `docs/epics/`, `docs/bugs/`, and `docs/spikes/`.
These items belong on the board, so a file per item duplicates the tracker and drifts out of date once the item is posted.
`tara new post-mortem` writes to `docs/post-mortems/`, but `docs/` is reserved for package documentation and ADRs.
The base instructions already say that backlog items belong in the tracker, so the scaffolding contradicts them.

### Required changes

- `tara new story|epic|bug|spike "<title>"` appends a section to one drafts file per batch in `.agents/plan/`, named `YYYYMMDDHHMM_<batch>-backlog-drafts.md`.
- Add a `--batch <name>` option to choose or create the drafts file, and default to the newest drafts file of the day.
- `tara new post-mortem "<title>"` writes `.agents/review/YYYYMMDDHHMM_<slug>.md`, and the template ends with a list of follow-up actions to post as issues.
- Each written file gets a row in the folder's `index.md`.
- Existing files under `docs/stories`, `docs/epics`, `docs/bugs`, `docs/spikes`, and `docs/post-mortems` are never moved or deleted.
- Update `base.md`, `docs/agent-working-docs.md`, and the changelog with a migration note.

### Definition of done

- [ ] Running `tara new story` twice in one batch adds two sections to the same drafts file.
- [ ] `tara new post-mortem` writes to `.agents/review/` and updates its index.
- [ ] Existing files under the old `docs/` folders are left untouched.
- [ ] The docs describe the flow from draft file to board.

## Amendments to existing issues

- #40: also verify that installed skill files still match the lock, and report a mismatch in `tara audit`.
- #38: document that `tara check` runs the commands in a repository's `.tara/checks.toml`, so running it in an untrusted clone executes that repository's commands.
