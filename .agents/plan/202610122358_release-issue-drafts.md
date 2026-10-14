# Release issue drafts

Date: 2026-10-12.
Status: release milestone assignments applied on 2026-10-13; issue-body amendments remain in draft.
Release grouping was approved, but these complete issue bodies remain available for the developer to revise before posting.
This document includes every open issue in the captured backlog once, including the proposed cross-release roadmap.
Published bodies without proposed amendments are retained for editing, not treated as implementation-ready specifications.

## Actual GitHub state

The `2.1.0` milestone and issues #63, #64, and #65 have been created.
Issue #63 is in 2.0.0, #65 is in 2.1.0, and #64 is unscheduled.
The approved milestone assignments were applied on 2026-10-13 without changing existing issue bodies, titles, states, labels, or assignees.
Milestone 2.1.0 contains #25, #39, #40, #51, #52, #54, #55, and #65.
Other open work from `2.x` is now unscheduled, and the empty `2.x` milestone is closed.
Issue #33 still tracks 2.0.0 on GitHub because its proposed cross-release body has not been posted.
The live 2.0.0 milestone therefore contains 15 work issues plus #33.
No issue was closed and no code fix was implemented during this planning work.

## Proposed release structure

| Group | Count | Goal |
| --- | --- | --- |
| Roadmap without a milestone | 1 | Reuse #33 for release goals, acceptance criteria, and links to milestone scope. |
| 2.0.0 | 15 | Fix setup safety, configuration and gate correctness, independent review, and package publication. |
| 2.1.0 | 8 | Improve managed-content restoration, provenance, working records, instructions, and generated CI. |
| Unscheduled backlog | 22 | Resolve design and ownership before assigning larger features to a release. |

The numbered release assignments and closure of the empty `2.x` bucket are complete.
Moving #33 outside the release milestone remains part of its pending roadmap rewrite.
Keep closed issue history, existing assignees, and issue discussion.
Do not add release dates or implement uncertain contracts without agreement.
Release candidates are stages of a stable release, not separate work milestones.

## Latest PR review

Copilot submitted a new review of PR #17 on 2026-10-12 at 19:34 UTC.
It reports eight open findings.
The relevant current source paths were checked and support these findings.
The review's 15 resolved older threads are not proof that the underlying code changed.
Do not close the corresponding issues without checking the implementation and regression tests.

| Finding | Reported severity | Evidence | Draft issue and acceptance change |
| --- | --- | --- | --- |
| Catalog installs overwrite existing files. | High | `src/tara/catalog.py:299-305`; [comment](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664086). | #30 adds collision protection to direct catalog installs, including bulk selection. |
| Invalid frontmatter can remove tool restrictions. | High | `src/tara/frontmatter.py:37-49`; [comment](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664129). | #56 covers malformed YAML, missing fences, and both translators. |
| Skipped installs are recorded as successful artifacts. | Medium | `src/tara/catalog.py:264-266`, `src/tara/cli.py:509-518`; [comment](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664164). | #18 requires explicit outcomes and success-only recording at all callers. |
| Config writes erase legacy discovery state. | Medium | `src/tara/config.py:227-230`; [comment](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664212). | #18 preserves an absent artifacts table until migration discovers existing content. |
| Multiline TOML values survive partial replacement and corrupt the file. | Medium | `src/tara/config.py:297-309`; [comment](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664248). | #18 tests complete-value replacement and preservation of unrelated content. |
| Forced generated-file writes fail on directory destinations. | Medium | `src/tara/generate.py:159-170`; [comment](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664301). | #30 rejects non-file destinations before force handling. |
| Forced configuration writes fail on directory destinations. | Medium | `src/tara/generate.py:176-196`; [comment](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664347). | #30 covers the configuration writer separately, with errors coordinated through #60. |
| Restoration checks existence before path safety. | Medium | `src/tara/skills.py:411-425`; [comment](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664387). | #20 checks safety before existence and dry-run handling. |

These fit existing issues.
No duplicate bug issues are needed.
The legacy-discovery repair is proposed for 2.0.0 as part of #18 instead of leaving that defect in the later backlog.

## Coverage of the independent plans review

The source is `.agents/review/202610122253_independent-plans-review.md`.

| Review finding | Draft destination |
| --- | --- |
| 1. Setup safety promises. | #18, #24, #30. |
| 2. Empty successful gate. | #60. |
| 3. Publication provenance. | #22, #37. |
| 4. Release prerequisites and RC checks. | #21, #22 and the release runbook. |
| 5. Competing roadmap and board state. | #33 and the local-record changes below. |
| 6. Integration shorthand compatibility. | #18, #21. |
| 7. Generated CI differs from the project gate. | #65. |
| 8. Installed-package behavior is insufficiently checked. | #22 for minimum smoke cases; #39 for the broader matrix. |
| 9. Independent review and runtime limits. | #63, #37, #38, #50. |
| 10. Pi safety claim. | #64, #38. |
| 11. Pi instruction delivery and dependencies. | #64. |
| 12. Local-only continuation information. | #55, #14, #29. |
| 13. Executable stale plans and inaccurate indexes. | #55 and the local-record changes below. |
| 14. Registry justification and exact-revision restoration. | #42. |
| 15. Stack merge contracts. | #44, #46. |
| 16. Skill-source CLI ambiguity. | #53. |

## Fix and re-review order

1. Add regression cases and fix the current PR's ownership, frontmatter, manifest, TOML, and destination-safety defects.
2. Run targeted tests and `tara check`, then record the exact commit or diff and the issue-to-test mapping.
3. Ask a clean agent to review the changed paths and their lifecycle callers.
   Re-request the PR review after the developer pushes the fixes.
   Do not mark a finding resolved only because an issue or plan now mentions it.
4. Complete the remaining 2.0.0 release and governance work.
5. Run the independent release-readiness review and installed-artifact checks before the RC.

Do not request another review of unchanged implementation now.
Do not treat the current green CI as evidence that these missing regression cases pass.
Keep ordinary fixes within the approved issues; return to the developer if a behavior decision changes the release contract.

## Local records to update after approval

Replace the old roadmap's issue inventory with links to the published roadmap and numbered milestones.
Mark posted drafts and completed plans as historical, and update their indexes.
Update the execution plan to include #63, the latest review cases, and the chosen compatibility contract.
Update the release runbook for exact-commit artifacts, exact-version RC verification, and developer-controlled publication.
Keep #33 open across releases if its proposed cross-release role is approved.
Record shared continuation state in a tracked plan, review, or official issue when session memory stays local.
These changes have not yet been applied to the older plans or the published roadmap.

## How to use this draft

Edit the proposed bodies below.
Each issue names its milestone captured on 2026-10-12 and its proposed milestone.
Use GitHub for current membership; the captured values preserve the draft's original baseline.
Retained bodies may still need better scope or acceptance criteria; empty bodies are explicitly marked.
After approval, update existing issues rather than creating duplicates.
Retire this draft as a historical snapshot after posting so it cannot become a second editable board.

<!-- BEGIN ISSUE DRAFTS -->

## Roadmap without a milestone


| Issue | Proposed title | Body changes |
| --- | --- | --- |
| [#33](#issue-33) | Roadmap: lightweight harness and release milestones | Proposed amendments. |


<a id="issue-33"></a>

### #33: Roadmap: lightweight harness and release milestones

Source: https://github.com/plugin-healthcare/tara/issues/33.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: none.
Body status: proposed replacement, not posted.

##### Direction

Keep Tara a lightweight setup and verification harness.
Tara maintains readable project rules, safe generated files, explicit content selections, and the project's check gate.
The coding agent and its execution environment own runtime permissions and isolation.
GitHub owns merge and publication controls.

##### Releases

| Release | Goal | Authoritative scope |
| --- | --- | --- |
| 2.0.0 | Establish safe setup and a verified first stable release. | [2.0.0 milestone](https://github.com/plugin-healthcare/tara/milestone/1) |
| 2.1.0 | Improve repeatable setup and the daily workflow. | [2.1.0 milestone](https://github.com/plugin-healthcare/tara/milestone/3) |
| Unscheduled | Resolve design choices before making release commitments. | [Open issues without a milestone](https://github.com/plugin-healthcare/tara/issues?q=is%3Aissue%20is%3Aopen%20no%3Amilestone) |

The milestone is the release issue list; do not duplicate that list in this roadmap.
This cross-release tracker has no milestone and stays open when a release ships.
Release candidates are stages of the corresponding stable release.
Dates and additional release numbers are not committed.

##### 2.0.0 acceptance

- Safe setup and reruns preserve developer-owned files and explicit integrations.
- Invalid or empty check configurations cannot pass without running the intended gate.
- The compatibility decision, migrations, install route, and package metadata agree.
- Independent review is recorded through #63 and required PR review through #37.
- #22 binds the protected release commit, passing checks, artifact identity, and trusted publication.
- An exact-version RC is verified before stable; final-version artifacts are rebuilt and tested from the accepted source.

The current execution plan is `.agents/plan/202610041800_release-2.0.0-execution-runbook.md`.
The reusable release procedure is `.agents/runbooks/release-a-new-version.md`.
Do not close issue #49 until its fix has landed, even when PR #17 CI is green.

##### 2.1.0 acceptance

- Managed content can be restored and inspected through the lifecycle and provenance work.
- Shared working records have clear ownership, status, and continuation information.
- Python and language-neutral instructions avoid duplication.
- Generated CI uses the same project gate as local development through #65.
- The installed-wheel lifecycle matrix is required for this release.

The release follows the stable baseline; it does not require a remote registry, new runtime, or storage backend.

##### Unscheduled decisions

- Evaluate the optional registry in #42 before implementing remote catalog delivery.
- Resolve canonical formats in #19 and the contributed-stack contract in #43 before scheduling that expansion.
- Define shared-information needs in #14 before committing to the optional backend in #29.
- Evaluate Pi through spike #64; no adapter or safety guarantee is approved.
- Keep skill discovery, other integrations, and remaining feature work in the backlog until their release scope is approved.

##### Ways of working

- Draft proposed issue and milestone changes in `.agents/plan/` and obtain developer approval before posting.
- After posting, GitHub issues and milestones are authoritative; local drafts become historical records.
- Keep each change testable, independently reviewed, and small enough to release.
- Record the last completed step and commit, next action, blockers, and required decision in a shared plan, review, or issue.
- Keep raw local scratch optional and never publish ignored notes in bulk.
- The developer makes commits, pushes, merges, and production or repository-setting changes.

Release grouping approved on 2026-10-12.
This issue body is a draft and has not replaced the published roadmap.


## 2.0.0


| Issue | Proposed title | Body changes |
| --- | --- | --- |
| [#18](#issue-18) | Stabilize integration lifecycle and configuration | Proposed amendments. |
| [#20](#issue-20) | Contain generated paths within the repository | Proposed amendments. |
| [#21](#issue-21) | Align the next release version with SemVer | Proposed amendments. |
| [#22](#issue-22) | Add a reproducible package release pipeline | Proposed amendments. |
| [#24](#issue-24) | rebuild silently drops locally modified catalog artifacts from the manifest | Published body retained. |
| [#26](#issue-26) | rebuild does not restore library skills from library-skills.json | Published body retained. |
| [#30](#issue-30) | tara seems to overwrite copilot-instructions | Proposed amendments. |
| [#37](#issue-37) | Protect main and require release checks | Proposed amendments. |
| [#38](#issue-38) | Add SECURITY.md, support policy, and deprecation policy | Proposed amendments. |
| [#49](#issue-49) | Fix the five tests that fail on HEAD | Published body retained. |
| [#50](#issue-50) | Stop the default git MCP server from contradicting the never-commit rule | Proposed amendments. |
| [#56](#issue-56) | Fail closed when agent frontmatter does not parse | Proposed amendments. |
| [#60](#issue-60) | One error hierarchy and clean CLI errors | Proposed amendments. |
| [#61](#issue-61) | Small correctness fixes from the quality review | Published body retained. |
| [#63](#issue-63) | Require independent review in the bundled workflow | Published body retained. |


<a id="issue-18"></a>

### #18: Stabilize integration lifecycle and configuration

Source: https://github.com/plugin-healthcare/tara/issues/18.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: proposed replacement, not posted.

##### Problem

The Claude Code integration branch works, but the final structural review found four lifecycle and configuration defects that should be resolved before release.

##### Required changes

- [ ] Preserve configured integrations when `tara init` is rerun without `--integrations`.
- [ ] When `tara init --integrations` explicitly removes an integration, remove only Tara-owned generated artifacts, matching `tara integrations`.
- [ ] Prune stale generated agents and commands when their Copilot source is deleted. Preserve hand-written files and restore starter commands when a formerly shadowing prompt disappears.
- [ ] Forbid unknown top-level and nested configuration fields after migrating supported legacy `tool` and `tools` keys.
- [ ] Write `.tara/config.toml` atomically and report persistence failures as `ConfigError`.
- [ ] Avoid removing integration artifacts before the new configuration can be persisted successfully.
- [ ] Report malformed or unreadable `opencode.json` during integration removal instead of presenting cleanup as successful.

##### Minimal structural cleanup

- Move integration selection, adapter dispatch, and lifecycle orchestration into a small `integrations` service module.
- Keep Claude and OpenCode translation in their existing adapter modules.
- Keep ownership-safe filesystem operations in `generate.py`.
- Remove duplicate integration-target calculation.

##### Compatibility requirements

- Persist explicit integration names. Expand `all` and `*` when writing config.
- Preserve legacy `tool`, `tools`, `--tool`, `--tools`, and hidden `tara tools` compatibility.
- Preserve legacy scalar `tool = "all"` as Copilot plus OpenCode.
- Never delete or overwrite hand-written files.

##### Definition of done

- [ ] Regression tests cover every required change.
- [ ] Generated CLI documentation and changelog are current.
- [ ] `tara check` passes.

##### Proposed review follow-up (2026-10-12)

- [ ] Before the 2.0.0 version freeze, approve a compatibility table with #21 for canonical flags, deprecated aliases, legacy scalar configuration, explicit lists, `all`, and `*`.
- [ ] Cover the current difference between CLI `all` and legacy scalar `tool = "all"` with tests and an explicit migration decision.
- [ ] Document any opt-in integration exclusions in help before adding them.
- [ ] Keep safe reruns and developer-owned-file preservation ahead of new integrations.

The minimal service-module refactor is not a separate 2.0.0 feature requirement.
Do only the structural work needed to fix the lifecycle safely; leave broader package reorganization to #59.
Do not infer the unresolved shorthand behavior from the new Pi spike.

###### October 12 PR review cases

- [ ] Record selected artifacts only after successful installation, including picker installs, direct agent installs, and package-triggered sync.
- [ ] Use a structured installation outcome or a handled refusal; do not parse display strings to decide success.
- [ ] Preserve an absent artifacts table in an existing legacy config until discovery runs; initialize an empty table only for a genuinely new config.
- [ ] Rewrite whole multiline TOML values and preserve unrelated content.
- [ ] Test legacy integration selection followed by rebuild, skipped installs, and multiline artifact arrays independently.

These map to PR #17 comments [recording](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664164), [legacy discovery](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664212), and [multiline TOML](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664248).
The legacy-discovery repair is proposed for 2.0.0 here because it is part of preserving existing configuration behavior.



<a id="issue-20"></a>

### #20: Contain generated paths within the repository

Source: https://github.com/plugin-healthcare/tara/issues/20.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: proposed replacement, not posted.

##### Problem

Generation and cleanup reject a symlink only when the final destination is itself a symlink. A symlinked parent directory can therefore redirect child writes, copies, unlinks, or recursive deletion outside the repository.

For example, with `.claude/skills` symlinked to an external directory, `.claude/skills/demo` is not itself reported as a symlink. The current lifecycle code can operate on that external path.

##### Required changes

- Reject generated writes, copies, unlinks, and recursive deletion when any destination ancestor below the repository root is a symlink.
- Verify the resolved destination remains beneath the resolved repository root.
- Centralize the containment check in the ownership-safe filesystem layer instead of duplicating it in each integration adapter.
- Preserve existing behavior for normal in-repository paths and hand-written files.

##### Definition of done

- [ ] Regression tests cover symlinked Claude agent, command, and skill parents.
- [ ] Regression tests cover equivalent OpenCode paths.
- [ ] Cleanup and integration removal cannot affect files outside the repository.
- [ ] `tara check` passes.

##### Proposed review follow-up (2026-10-12)

- [ ] Check destination safety before existence and dry-run branches in `restore_missing`.
- [ ] Report existing and dangling symlinks, symlinked ancestors, and outside-root destinations without treating them as restored.
- [ ] Keep safe existing managed skills unchanged.
- [ ] Cover remaining writes to generated state, agent documents, artifact records, skill manifests and locks, and docs with the shared containment rule.

The October 12 restore finding is [PR #17 comment 4251664387](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664387).
The shared containment helper is already on the branch, but this issue stays open until all required call sites are covered and the work lands.



<a id="issue-21"></a>

### #21: Align the next release version with SemVer

Source: https://github.com/plugin-healthcare/tara/issues/21.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: proposed replacement, not posted.

##### Problem

`CHANGELOG.md` describes breaking behavior for the proposed 1.1.0 release while the project states that it follows Semantic Versioning. A stable release needs an explicit compatibility and version decision.

The PyPI project-name conflict is accepted and is outside this issue.

##### Decision

Release as 2.0.0, following the reduced scope approved in roadmap #33.
Publish 2.0.0rc1 before stable.
Keep supported legacy aliases and document each deliberate behavior change.
The distribution is `tara-dev`; the command and import module remain `tara`.

##### Required changes

- Inventory every documented breaking change and affected CLI/config behavior.
- Decide which compatibility behavior is retained or removed.
- Update `pyproject.toml`, `CHANGELOG.md`, generated CLI docs, and migration guidance consistently.
- Publish a release candidate before the stable tag.

##### Definition of done

- [ ] The selected version follows SemVer.
- [ ] Compatibility tests cover supported legacy CLI flags and configuration migration.
- [ ] The changelog and migration guidance match actual behavior.
- [ ] The release candidate version and final tag are derived from the protected release commit.

##### Proposed review follow-up (2026-10-12)

- [ ] Approve the `all` and legacy alias compatibility table with #18 before freezing the version.
- [ ] Include the version-lookup repair folded in from #57 and verify it against the installed `tara-dev` distribution.
- [ ] Align package metadata, README install commands, CLI documentation, changelog, and migration guidance.
- [ ] Use an exact distribution version in post-publication checks, including release candidates.
- [ ] Build and verify final-version artifacts from the accepted source; do not rename or reuse RC bytes as stable artifacts.

Publication provenance and the single supported release procedure are covered by #22.



<a id="issue-22"></a>

### #22: Add a reproducible package release pipeline

Source: https://github.com/plugin-healthcare/tara/issues/22.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: proposed replacement, not posted.

##### Problem

The current CI does not provide a complete package release path.
A release must bind the approved commit, checks, artifacts, and publication to the same source.
The distribution name is `tara-dev`.

##### Required changes

- Test Python 3.12, 3.13, and 3.14 in PR CI and require package smoke checks.
- Define one release workflow that accepts only an eligible version tag on an approved protected-branch commit.
- Build the wheel and sdist once for the release from that exact commit in CI.
- Run the required gate, compatibility checks, and isolated artifact smoke checks before publication.
- Pass the same tested artifact bytes to PyPI and the GitHub release, with commit and artifact identity recorded in attestations.
- Publish through a developer-approved `pypi` environment and trusted publishing without a long-lived token.
- Reject unrelated tags and mismatches between tag, package metadata, workflow commit, or selected artifacts.
- Coordinate required checks and current PR approval with #37.
- Replace the manual local-upload release route in the runbook.

##### Minimum installed-artifact checks

- Verify the exact version for both the wheel and sdist in clean environments.
- Exercise `tara init --dry-run` and the public `python -m tara.markdown_lint` entry point.
- Exercise bundled-data access, setup and an unchanged rerun, a developer-owned collision, and one integration add/remove cycle.
- Use isolated local fixtures and compare file contents, not only `git status`.
- Keep the broader lifecycle matrix in #39 for 2.1.0.

##### Release procedure

- Treat RCs as stages of the stable milestone.
- Use exact-version installation checks, such as `uvx --from 'tara-dev==2.0.0rc1' tara --version`.
- Build and test final-version artifacts from the accepted candidate source.
- Keep roadmap #33 open across releases and outside release milestones.
- Mark PR creation, merge, tag push, publication approval, and repository changes as developer-controlled.
- Retain rollback through yanking and a corrected release without moving a published tag.

##### Definition of done

- [ ] PRs run the supported Python matrix and artifact smoke checks.
- [ ] An RC can publish without a long-lived token.
- [ ] Ineligible tags and failed checks cannot publish.
- [ ] The package index and GitHub release receive exactly the artifacts tested for the recorded commit.
- [ ] Installation of the exact published version is verified.
- [ ] The runbook has one supported publication route and explicit developer stops.
- [ ] #37 prevents unverified merges and documents the required check names.

Part of the 2.0.0 milestone and roadmap #33.



<a id="issue-24"></a>

### #24: rebuild silently drops locally modified catalog artifacts from the manifest

Source: https://github.com/plugin-healthcare/tara/issues/24.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: current published body, retained for editing.

##### Problem

`tara rebuild` records `[artifacts]` in `.tara/config.toml` via `_rebuild_manifest` (`src/tara/cli.py:1206-1223`). When `cfg.artifacts is None` it discovers installed items and keeps only those where `_matches_catalog_source(item)` holds, i.e. the on-disk file still matches the catalog copy.

An artifact the user has edited locally therefore does not match, is left out of the recorded manifest, and is silently not restored by a later `rebuild`.

##### Why it matters

This turns into data loss as soon as a repo gitignores generated artifacts, which is a reasonable thing to do (see the sibling issue about vendored third-party skills).

Observed in `plugin-healthcare/pluginlake`:

- `tara rebuild --dry-run` reported `record 19 recognized catalog artifacts`.
- `.github/skills/writing-epics-stories/` and `.github/instructions/markdown.instructions.md` were both **absent** from that set, because both had diverged from the catalog copy.
- Had those paths been gitignored on the strength of "rebuild restores it", both would have been lost with no warning.

The failure is silent. Nothing in the output says an installed artifact was skipped, so the user cannot tell the manifest is incomplete.

##### Expected

At minimum, report it:

```
  recorded 19 catalog artifacts
  skipped 2 locally modified (not restorable by rebuild):
    skills/writing-epics-stories
    instructions/markdown.instructions.md
```

Better: record modified artifacts in the manifest too, flagged as locally modified, so `rebuild` can restore the catalog version on request or at least warn that a local edit exists and will not be recreated.

##### Notes

`skills.restore_missing` (`src/tara/skills.py:402`) does the right thing for manifest-managed skills: it restores at the locked commit. The gap is only in the catalog-artifact path, which has no lockfile equivalent and relies on content matching.



<a id="issue-26"></a>

### #26: rebuild does not restore library skills from library-skills.json

Source: https://github.com/plugin-healthcare/tara/issues/26.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: current published body, retained for editing.

##### Problem

Skill restoration is split across two commands and only one of them is covered by `tara rebuild`.

- `skills.restore_missing` (`src/tara/skills.py:402`) restores skills from `.tara/skills.toml` + `skills.lock`, and is called by `rebuild` (`src/tara/cli.py:1281`).
- Skills recorded in `.tara/library-skills.json`, the embedded/library-skills standard from `sync.py`, are only installed by `tara skill sync`.

So after a fresh clone of a repo that gitignores `.github/skills/`, `tara rebuild` silently leaves library skills missing.

Observed in `plugin-healthcare/pluginlake`: `fastapi` is present in `.tara/library-skills.json` as `{"package": "fastapi", "version": "0.141.1"}`. `tara rebuild` restores the 17 lockfile skills and the catalog artifacts, but not `fastapi`.

##### Expected

Either:

1. `tara rebuild` also runs the embedded-skills phase, so one command fully reconstructs the setup from `.tara/`; or
2. `rebuild` reports what it did not restore and names the command that will:

```
  note: 1 library skill not restored by rebuild (run `tara skill sync`): fastapi
```

Option 1 matches the documented promise of `rebuild`, "Reconstruct the Tara-managed setup from .tara/config.toml". Right now that reconstruction is incomplete, and the gap is invisible.



<a id="issue-30"></a>

### #30: tara seems to overwrite copilot-instructions

Source: https://github.com/plugin-healthcare/tara/issues/30.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: proposed replacement, not posted.

##### Problem

Tara must not silently replace developer-owned instructions, configuration, or catalog content.
Core setup still uses unconditional writers, and direct catalog installation can copy over an existing agent, prompt, or instruction without ownership checks.
The shared writers also attempt to write to directory destinations when force is enabled.

##### Required changes

- Route core instructions and MCP setup through ownership-safe writers.
- Apply the same collision policy to direct catalog agents, prompts, instructions, and bundled skill directories.
- Show a diff and ask before replacing developer-owned content interactively.
- Skip and report collisions non-interactively unless an applicable explicit override was approved.
- Preserve developer-authored hook settings and OpenCode configuration values.
- Reject non-file destinations before any force branch; force never makes a directory a valid file destination.
- Keep path containment independent of ownership and confirmation.
- Keep the alternative separate `tara.instructions.md` approach as a decision to evaluate, not an assumed migration.

##### Definition of done

- [ ] Core `init` preserves hand-written instructions and MCP configuration by default.
- [ ] Catalog selection, including unattended bulk selection, preserves developer-owned file and skill collisions.
- [ ] Interactive confirmation includes a useful diff.
- [ ] Both `write_generated` and `write_configured` preserve directory destinations with and without force and report the refusal.
- [ ] Hook and OpenCode updates preserve user-owned values and remove only Tara-owned values.
- [ ] Regression tests cover the CLI entry points and shared writer behavior.
- [ ] The README and changelog describe behavior that the tests establish.

Coordinate installation outcome recording with #18 and clean CLI errors with #60.
October 12 PR findings: [catalog collisions](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664086), [generated-file directories](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664301), and [configuration directories](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664347).



<a id="issue-37"></a>

### #37: Protect main and require release checks

Source: https://github.com/plugin-healthcare/tara/issues/37.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: proposed replacement, not posted.

##### Problem

`main` has no branch protection, so a pull request can merge with a red gate and stable releases are not tied to verified commits.

##### Required changes

- Protect `main`: require pull requests, require review, and block force pushes and deletion.
- Require the gate, pre-commit, Python compatibility matrix, and package smoke jobs from #22.
- Document the required checks in `CONTRIBUTING.md` or the release runbook.

##### Definition of done

- [ ] A pull request with a failing required check cannot merge.
- [ ] The required check names match the job names in `.github/workflows/`.

Depends on #22 for the matrix and smoke jobs. Part of #33.

##### Proposed review follow-up (2026-10-12)

- [ ] Require an independent PR review and dismiss stale approval when the reviewed change changes.
- [ ] Record the reviewed commit and any unresolved findings through the workflow in #63.
- [ ] Verify that the enforced status-check names match the jobs actually produced by #22.
- [ ] Document that branch protection does not itself restrict publication from arbitrary tags.
- [ ] Coordinate tag eligibility and developer approval of the publishing environment with #22.

This issue authorizes planning the settings change, not an agent applying repository protections without the developer's explicit execution approval.



<a id="issue-38"></a>

### #38: Add SECURITY.md, support policy, and deprecation policy

Source: https://github.com/plugin-healthcare/tara/issues/38.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: proposed replacement, not posted.

##### Problem

The release-readiness review lists missing governance documents as a gap for a stable release.
Users have no documented way to report a vulnerability, no statement of which versions are supported, and no deprecation policy for CLI flags and config keys.

##### Required changes

- Add `SECURITY.md` with a private reporting route (GitHub private vulnerability reporting).
- Document the supported Tara versions and Python versions.
- Document the deprecation policy: deprecated CLI aliases and config keys keep working with a warning for at least one minor release and are removed only in a major release.

##### Definition of done

- [ ] `SECURITY.md` exists and private vulnerability reporting is enabled.
- [ ] The support and deprecation policy is linked from the README.

Part of #33.

##### Also

- Document that `tara check` runs the commands in a repository's `.tara/checks.toml`, so running it in an untrusted clone executes that repository's commands.

##### Proposed review follow-up (2026-10-12)

- [ ] Distinguish mechanically checked configuration, advisory instructions, runtime tool permissions, and execution isolation.
- [ ] State that removing an MCP server does not prevent equivalent shell operations.
- [ ] State that pinned external content and conflict warnings do not establish that content is safe.
- [ ] Keep the baseline offline setup usable without a registry, storage backend, or extra agent integration.

Do not describe a generated policy file as proof that a runtime loaded or enforced it.



<a id="issue-49"></a>

### #49: Fix the five tests that fail on HEAD

Source: https://github.com/plugin-healthcare/tara/issues/49.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: current published body, retained for editing.

###### Problem

`tara check` fails on commit `4188e01` of `feat/claude-code-support`, so no change on the branch can be verified and PR #17 cannot merge.
The failures do not depend on uncommitted work.

- `tests/test_hooks.py::test_merge_does_not_deduplicate_across_different_matchers`
- `tests/test_hooks.py::test_merge_appends_only_missing_actions_for_the_same_matcher`
- `tests/test_hooks.py::test_install_rejects_a_symlinked_settings_file`
- `tests/test_hooks.py::test_install_rejects_a_symlinked_settings_directory`
- `tests/test_catalog.py::test_install_instruction_skips_a_symlinked_destination_directory`

###### Required changes

- Decide per test whether the code or the test is wrong, and fix that side.
- Fix the symlink cases with the shared containment check from #20, so the hook and catalog installers use the same rule.

###### Definition of done

- [ ] `tara check` passes on the branch.
- [ ] No test is skipped or marked as expected to fail to get there.

Part of #33.



<a id="issue-50"></a>

### #50: Stop the default git MCP server from contradicting the never-commit rule

Source: https://github.com/plugin-healthcare/tara/issues/50.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: proposed replacement, not posted.

###### Problem

`git` is a default MCP server (`src/tara/data/mcp/catalog.toml:26-31`).
`mcp-server-git` exposes write tools such as `git_add`, `git_commit`, `git_reset`, `git_checkout`, and `git_create_branch`.
The base instructions tell agents never to commit, so the default setup grants a capability the instructions forbid, and the outcome depends on whether the agent follows the prose.

###### Required changes

- Remove `default = true` from the `git` server, so it stays available in the picker but is not selected by default. Agents can read history through the shell.
- Add a `tara audit` finding when `.mcp.json` configures the `git` server while the instructions forbid committing.
- Note the change in the changelog.

###### Definition of done

- [ ] A fresh `tara init` does not select the Git MCP server by default.
- [ ] `tara audit` reports the contradiction in an existing repository.
- [ ] Existing repositories keep their current `.mcp.json` until the developer changes it.

Part of #33.

##### Proposed review follow-up (2026-10-12)

Removing the default server reduces capabilities; it does not block `git commit` through a shell or another tool.
Document that limit with #38.
Keep the server explicitly selectable and preserve existing repositories until the developer changes their selection.



<a id="issue-56"></a>

### #56: Fail closed when agent frontmatter does not parse

Source: https://github.com/plugin-healthcare/tara/issues/56.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: proposed replacement, not posted.

###### Problem

`frontmatter.parse` returns an empty mapping when the YAML in an agent file fails to parse.
The Claude translator then omits `tools` and the OpenCode translator omits `permission`, so a tool-restricted agent gets every tool.
An unquoted colon in a description is enough to trigger it, and the raw frontmatter ends up in the generated body.

###### Required changes

- When a source file starts with `---` and the frontmatter does not parse, skip the file and report it with the parse error.
- Never generate an agent without its tool restriction.

###### Definition of done

- [ ] A test with `description: Reviewer. Use when: reviewing diffs` and `tools: [read, search]` shows the agent is skipped and reported for both Claude and OpenCode.
- [ ] Valid agents still translate unchanged.
- [ ] The changelog lists the fix.

Found in the review of the PR #17 branch.

##### Proposed review follow-up (2026-10-12)

- [ ] Distinguish malformed YAML, a missing closing fence, and a non-mapping frontmatter value from genuinely absent frontmatter.
- [ ] Skip and report malformed agents in both translators rather than inventing an unrestricted replacement.
- [ ] Test malformed descriptions and missing fences while preserving valid explicit tool restrictions.

This is confirmed again in [PR #17 comment 4251664129](https://github.com/plugin-healthcare/tara/pull/17#discussion_r4251664129).
Do not treat a resolved older review thread as evidence that the parser or translators were fixed.



<a id="issue-60"></a>

### #60: One error hierarchy and clean CLI errors

Source: https://github.com/plugin-healthcare/tara/issues/60.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: proposed replacement, not posted.

###### Problem

Tara has four unrelated exception bases and also raises built-in `ValueError` and `FileNotFoundError` as domain errors.
`tara add`, `tara standards`, `tara init`, and `tara rebuild` let a `ConfigError` or `HookError` escape as a traceback, and a malformed `.tara/mcp.local.json` or `.claude/settings.json` crashes the command.
Two `except Exception` blocks in `cli.py` turn bugs in Tara itself into one-line warnings.

###### Required changes

- Add `errors.py` with `TaraError`, and make the existing exception classes subclass it while staying importable from their current modules.
- Add a `main()` entry point that prints `error: <message>` and exits 1 for a `TaraError`, and point `[project.scripts]` at it.
- Raise a `TaraError` subclass for malformed `.mcp.json`, `.tara/mcp.local.json`, `.claude/settings.json`, and `.tara/checks.toml`.
- Replace both `except Exception` blocks with `except TaraError`.

###### Definition of done

- [ ] Tests show that a malformed config, settings file, or checks file gives one error line and exit code 1 for `add`, `standards`, `init`, `rebuild`, and `check`.
- [ ] The CLI surface snapshot in `tests/test_cli_docs.py` is unchanged.

Found in the code quality review of the PR #17 branch.

##### Proposed review follow-up (2026-10-12)

The independent review reproduced exit code 0 with no checks run for an empty `.tara/checks.toml` or a valid TOML file using `[[checks]]` instead of `[[check]]`.

- [ ] Validate the check schema before execution and reject missing or empty check definitions.
- [ ] Reject misspelled check tables, invalid entry shapes, and empty command strings with an actionable `TaraError` message and nonzero exit.
- [ ] Add separate regression cases for empty input, `[[checks]]`, and unusable commands.
- [ ] Preserve valid repository-specific check commands.
- [ ] Never present a disabled or empty gate as a successful gate.

This extends the existing error-boundary work; do not create a duplicate issue.



<a id="issue-61"></a>

### #61: Small correctness fixes from the quality review

Source: https://github.com/plugin-healthcare/tara/issues/61.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: current published body, retained for editing.

###### Problem

- `tara audit --deep` exits 0 when the Copilot review fails.
- `--dry-run` still asks "Overwrite?" in `write_generated` and `mirror_skills`, and then does nothing.
- `tara skill add ... --name foo.v2` writes an unquoted TOML key, and every later read of `.tara/skills.toml` fails with `KeyError`.
- PEP 503 name normalisation exists twice, and `core.port_targets` is unused.

###### Required changes

- Exit 1 when the deep review fails.
- Return before the confirmation prompt when `dry_run` is set.
- Quote skill names as TOML keys in `.tara/skills.toml`.
- Remove `skills._normalize` in favour of `sync.normalize_package_name`, and remove `core.port_targets` and the empty helper section in `core.py`.

###### Definition of done

- [ ] One test per fix.
- [ ] The changelog lists the user-facing fixes.


###### Also in scope, from #62

###### Problem

The generated `check` starter command for Claude and OpenCode runs `ruff` and `pytest` directly, so it skips types, security, and `.tara/checks.toml`.
The `review` starter command names the `gilfoyle` agent, which only exists when the user installed it.
No test checks that every bundled catalog file has valid frontmatter, and a broken file would now be skipped or granted the wrong tools.

###### Required changes

- Make the `check` starter command run `uv run tara check`, and make the `review` starter command independent of any agent.
- Add a test that parses every `src/tara/data/catalog/**/*.md` and runs the audit rules over it with no errors.

###### Definition of done

- [ ] Generated starter commands match for Claude and OpenCode.
- [ ] The catalog test fails when a bundled file has broken frontmatter.


Found in the code quality review of the PR #17 branch.



<a id="issue-63"></a>

### #63: Require independent review in the bundled workflow

Source: https://github.com/plugin-healthcare/tara/issues/63.
Milestone captured on 2026-10-12: 2.0.0.
Proposed milestone: 2.0.0.
Body status: current published body, retained for editing.

##### Goal

Require an independent review in Tara's bundled workflow before a change is handed off.
This tracks step 3 of the 2.0.0 execution plan and finding 9 of the independent plans review.

##### Required changes

- Add a review step between Check and Document in the bundled base instructions and require a filed review in the Definition of Done.
- Run the review in a clean agent with fresh context, preferably a different model, never the agent that implemented the change.
- Record the reviewed commit or exact uncommitted diff, the reviewer, unresolved findings, and developer acceptance.
- Re-review changed work before accepting it.
- Check project invariants, duplicated parsers and writers, and malformed permission-relevant input.
- Add the existing execution plan's instruction lessons to their bundled sources, including approved issue drafts, binary story points, terse rule files, and no unsolicited commit trailers.
- Keep review instructions separate from runtime permissions and isolation.
- Keep commits, pushes, and shared infrastructure changes under developer control.

##### Definition of done

- [ ] The bundled workflow and review prompt agree on when and how review occurs.
- [ ] The review record identifies exactly what was reviewed and what remains unresolved.
- [ ] The instructions require new approval when the reviewed change changes.
- [ ] Content checks pass and the changelog describes the updated workflow.
- [ ] The developer reviews the instruction changes independently.

Depends on #37 for enforced PR review and required checks.
Part of the 2.0.0 milestone and roadmap #33.


## 2.1.0


| Issue | Proposed title | Body changes |
| --- | --- | --- |
| [#25](#issue-25) | Offer to gitignore vendored third-party skills instead of committing them | Published body retained. |
| [#39](#issue-39) | Add end-to-end lifecycle tests in fixture repositories | Proposed amendments. |
| [#40](#issue-40) | Record source and license of third-party skills in the lock | Published body retained. |
| [#51](#issue-51) | Load Python rules from one place | Published body retained. |
| [#52](#issue-52) | Generate the skill theme list from index.toml | Published body retained. |
| [#54](#issue-54) | Move the language-neutral testing rules to base.md | Published body retained. |
| [#55](#issue-55) | Write backlog drafts and post-mortems to .agents/ | Proposed amendments. |
| [#65](#issue-65) | Use the project gate in generated CI | Published body retained. |


<a id="issue-25"></a>

### #25: Offer to gitignore vendored third-party skills instead of committing them

Source: https://github.com/plugin-healthcare/tara/issues/25.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: 2.1.0.
Body status: current published body, retained for editing.

##### Problem

`tara skill add` / `tara skill sync` fetch skills from upstream repos into `.github/skills/`, and nothing suggests excluding them from version control. The result is that third-party content gets vendored into the consuming repository.

Measured in `plugin-healthcare/pluginlake`:

- `.github/skills/` = **274 files, 1.7 MB**, 25 skills
- 17 pinned by commit in `.tara/skills.lock`, sourced from `duckdb/duckdb-skills`, `dagster-io/skills`, `anthropics/skills`, `streamlit/agent-skills`, `likec4/likec4`, `github/gh-stack`
- 3 carry their own `LICENSE.txt`
- `dagster-expert` alone is 173 files

This is redistribution of other projects' licensed material, in a public repo, with no clear provenance for a reader of that repo.

It is also redundant. `.tara/skills.lock` pins every managed skill to an exact commit, and `skills.restore_missing` already restores them at that revision. Verified: deleted `.github/skills/query`, ran `tara rebuild`, got it back byte-identical at `7feda8e01e22`.

##### Proposal

Have `tara init` (and `tara skill add`) offer to write a `.gitignore` block, on the same pattern as the existing `[agents] gitignore` mechanism in `agent_docs.ensure_gitignored`:

```gitignore
# Tara-managed skills, restored from .tara/ via `tara rebuild` + `tara skill sync`.
.github/skills/*
!.github/skills/<locally-authored-skill>/
```

Requirements:

- Keep locally authored skills tracked. The negation entries must be generated from what tara does *not* manage, so a hand-written skill is never ignored.
- Depends on the sibling issue about locally modified catalog artifacts: ignoring is only safe once `rebuild` reliably restores everything it claims to manage.
- Make it opt-in with a clear prompt. Some teams will prefer vendoring for offline or air-gapped builds, which is legitimate.

##### Notes

`.tara/` (`config.toml`, `skills.toml`, `skills.lock`, `library-skills.json`) becomes the committed source of truth, which is a much better artifact to review in a PR than 274 vendored files.



<a id="issue-39"></a>

### #39: Add end-to-end lifecycle tests in fixture repositories

Source: https://github.com/plugin-healthcare/tara/issues/39.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: 2.1.0.
Body status: proposed replacement, not posted.

##### Problem

File transformations are well unit-tested, but nothing exercises the full lifecycle on a real repository with the built package.
Regressions in rerun idempotency, restore from the lockfile, and integration removal are found by users.

##### Required changes

Add integration tests that run the installed wheel in temporary fixture repositories and cover these scenarios.

- `tara init` with every integration, then a rerun that changes nothing.
- `tara skill add <theme>`, deletion of the skill folders, and restore through `tara rebuild`.
- A hand-edited generated file is skipped in non-interactive mode.
- `tara integrations` add and remove touches only Tara-owned files.
- A 1.0 `.tara/config.toml` migrates without errors.
- Clean removal of all Tara-generated files.

##### Definition of done

- [ ] The scenarios run in CI against the built wheel.
- [ ] They are required checks for the 2.1.0 release and subsequent releases, coordinated with #37.

Part of #33.

##### Proposed review follow-up (2026-10-12)

Keep the broader installed-wheel lifecycle matrix here in 2.1.0.
The minimum installed-artifact smoke fixture remains in #22 for 2.0.0.
Use offline fixtures, explicit integration selections, and before-and-after content snapshots.
Do not use an unchanged-looking `git status` as the sole idempotency assertion.



<a id="issue-40"></a>

### #40: Record source and license of third-party skills in the lock

Source: https://github.com/plugin-healthcare/tara/issues/40.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: 2.1.0.
Body status: current published body, retained for editing.

##### Problem

Tara references third-party skills and does not vendor them.
After #25, the skill files may be gitignored, so a reader of a consuming repository has no visible provenance or license for the installed skills.

##### Required changes

- When a skill is installed, record its upstream repo, commit, and SPDX license in its `.tara/skills.lock` entry.
- Show the source and license in `tara skill list`.
- Keep the lockfile backwards compatible, so entries without a license still load.

##### Definition of done

- [ ] New lock entries contain repo, commit, and license.
- [ ] Old lockfiles load without errors.
- [ ] `tara skill list` shows the source and license.

Related to #25. Part of #33.

##### Also

- Verify that installed skill files still match the lock, and report a mismatch in `tara audit`.
- Show the license next to external skills, as described in #53.



<a id="issue-51"></a>

### #51: Load Python rules from one place

Source: https://github.com/plugin-healthcare/tara/issues/51.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: 2.1.0.
Body status: current published body, retained for editing.

###### Problem

Python guidance lives in the always-on `src/tara/data/instructions/python.md`, which is appended to `copilot-instructions.md`, and in the scoped catalog file `python.instructions.md` (`applyTo` Python files).
A repository with both loads overlapping rules twice, and the two files drift apart.
Earlier plans parked this because it changes generated output for every repository.

###### Required changes

- Move the Python coding rules into the scoped `python.instructions.md` and keep only stack-level tooling commands in `python.md`, or remove `python.md`.
- Install the scoped file by default for the Python stack.
- Regenerate `copilot-instructions.md` through the existing ownership checks, so a hand-edited file is not replaced (#30).

###### Definition of done

- [ ] Each Python rule exists in exactly one bundled file.
- [ ] `tara init` for a Python repository installs the scoped file.
- [ ] `tara rebuild` on an existing repository updates the generated `copilot-instructions.md` and leaves a hand-edited one alone.
- [ ] The changelog describes the change in generated output.

Part of #33.



<a id="issue-52"></a>

### #52: Generate the skill theme list from index.toml

Source: https://github.com/plugin-healthcare/tara/issues/52.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: 2.1.0.
Body status: current published body, retained for editing.

###### Problem

The list of skill themes is written by hand in both `README.md` and `docs/skills.md`.
PR #32 already updates only the README, so the two lists drift apart.

###### Required changes

- Generate the theme list from `src/tara/data/skills/index.toml`, the same way `docs/cli.md` is generated.
- Keep the list in `docs/skills.md` only, and link to it from the README.
- Fail the docs check when the generated list is out of date.

###### Definition of done

- [ ] Adding a theme to `index.toml` and regenerating the docs updates the list.
- [ ] The README no longer has its own copy.

Part of #33.



<a id="issue-54"></a>

### #54: Move the language-neutral testing rules to base.md

Source: https://github.com/plugin-healthcare/tara/issues/54.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: 2.1.0.
Body status: current published body, retained for editing.

###### Required changes

Move test-first, GIVEN/WHEN/THEN, mocking only at system boundaries, and the test anti-patterns from `python.md` to `base.md`.
`python.md` keeps only `uv`, `pytest`, `parametrize`, and the `tests/` layout.

Part of #33.



<a id="issue-55"></a>

### #55: Write backlog drafts and post-mortems to .agents/

Source: https://github.com/plugin-healthcare/tara/issues/55.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: 2.1.0.
Body status: proposed replacement, not posted.

###### Problem

`tara new story|epic|bug|spike` writes one file per item to `docs/stories/`, `docs/epics/`, `docs/bugs/`, and `docs/spikes/`.
These items belong on the board, so a file per item duplicates the tracker and drifts out of date once the item is posted.
`tara new post-mortem` writes to `docs/post-mortems/`, but `docs/` is reserved for package documentation and ADRs.
The base instructions already say that backlog items belong in the tracker, so the scaffolding contradicts them.

###### Required changes

- `tara new story|epic|bug|spike "<title>"` appends a section to one drafts file per batch in `.agents/plan/`, named `YYYYMMDDHHMM_<batch>-backlog-drafts.md`.
- Add a `--batch <name>` option to choose or create the drafts file; choose an open draft automatically only when the target is unambiguous, otherwise ask or require `--batch` non-interactively.
- `tara new post-mortem "<title>"` writes `.agents/review/YYYYMMDDHHMM_<slug>.md`, and the template ends with a list of follow-up actions to post as issues.
- Each written file gets a row in the folder's `index.md`.
- Existing files under `docs/stories`, `docs/epics`, `docs/bugs`, `docs/spikes`, and `docs/post-mortems` are never moved or deleted.
- Update `base.md`, `docs/agent-working-docs.md`, and the changelog with a migration note.

###### Definition of done

- [ ] Running `tara new story` twice in one batch adds two sections to the same drafts file.
- [ ] `tara new post-mortem` writes to `.agents/review/` and updates its index.
- [ ] Existing files under the old `docs/` folders are left untouched.
- [ ] The docs describe the flow from draft file to board.

##### Proposed review follow-up (2026-10-12)

- [ ] Define draft, posted, completed, and superseded states and keep folder indexes current.
- [ ] Never append new work implicitly to a posted or completed draft batch.
- [ ] Cover multiple same-day batches and concurrent append conflicts without losing content.
- [ ] Keep approved issues authoritative after posting; historical copies are not a second editable board.
- [ ] Require a minimal shared continuation record in a tracked plan, review, or official issue when session memory is local.
- [ ] Record the last completed step and commit, next action, blockers, and required developer decision.
- [ ] Keep useful historical decisions without automatic deletion or bulk publication of ignored notes.

Coordinate the shared-information contract with #14 and #29 without making this release depend on a storage backend.



<a id="issue-65"></a>

### #65: Use the project gate in generated CI

Source: https://github.com/plugin-healthcare/tara/issues/65.
Milestone captured on 2026-10-12: 2.1.0.
Proposed milestone: 2.1.0.
Body status: current published body, retained for editing.

##### Problem

Tara's own CI runs `tara check`, but its generated CI template repeats the default Python commands.
A repository's `.tara/checks.toml` therefore changes the local gate without changing generated CI.
Initialization does not clearly connect users to the separate CI setup step.

##### Required changes

- Make the bundled CI workflow run the project's configured gate.
- Make Tara available through the documented project dependency setup.
- Keep additional secret scanning and workflow linting explicit.
- Offer CI setup or report its absence after initialization.
- Preserve existing workflows and require confirmation before any replacement.
- Keep the default command surface small and use the existing `tara new ci` route.

##### Definition of done

- [ ] A custom `.tara/checks.toml` is honored by the generated workflow.
- [ ] The generated workflow and local execution use the same gate entry point.
- [ ] An existing developer-owned workflow is preserved.
- [ ] Initialization clearly states the remaining CI setup step when needed.
- [ ] The template checks and documentation cover the supported installation route.

This is consumer-project CI work, separate from Tara's package release pipeline in #22.
Part of the 2.1.0 milestone and roadmap #33.


## Unscheduled backlog


| Issue | Proposed title | Body changes |
| --- | --- | --- |
| [#1](#issue-1) | Add support for OpenCode | Published body retained. |
| [#3](#issue-3) | Add support for goose | Published body retained. |
| [#4](#issue-4) | Restructure .github folder to Open Plugin specification | Published body retained. |
| [#9](#issue-9) | WINGMAN - add roborev features | Needs scope and acceptance criteria. |
| [#14](#issue-14) | Spike: investigate storage structures for fast agent information storage and retrieval | Proposed amendments. |
| [#15](#issue-15) | Feature: add maplib and ottr skill | Published body retained. |
| [#19](#issue-19) | Spike and ADR: adopt open canonical agent formats | Published body retained. |
| [#23](#issue-23) | Add a sensitivity scan for content that should not be published | Published body retained. |
| [#28](#issue-28) | Draft ADR: Adopt Vault-LD with graceful OKF compatibility | Published body retained. |
| [#29](#issue-29) | Integrate oxivault as structured, queryable store for the `.agents/` doc store | Proposed amendments. |
| [#31](#issue-31) | Add obra/superpowers as skill set | Needs scope and acceptance criteria. |
| [#36](#issue-36) | Add a scheduled health check for the skill index | Published body retained. |
| [#41](#issue-41) | Show the token cost of skills in the picker and audit | Published body retained. |
| [#42](#issue-42) | Spike and ADR: move the catalog to a fetched registry outside src/ | Proposed amendments. |
| [#43](#issue-43) | Let contributors add stacks through the registry | Published body retained. |
| [#44](#issue-44) | Support a list of stacks in config and tara init | Proposed amendments. |
| [#46](#issue-46) | Install a contributed stack from its folder | Proposed amendments. |
| [#47](#issue-47) | Add the Rust stack | Published body retained. |
| [#48](#issue-48) | Add the TypeScript stack | Published body retained. |
| [#53](#issue-53) | Browse and add skills from one index of Tara and external sources | Proposed amendments. |
| [#59](#issue-59) | Split cli.py and group modules into packages | Published body retained. |
| [#64](#issue-64) | Spike optional Pi integration and its protection boundary | Published body retained. |


<a id="issue-1"></a>

### #1: Add support for OpenCode

Source: https://github.com/plugin-healthcare/tara/issues/1.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

#### Plan: opencode support in wingman

##### Context

Wingman is setup/management tooling for GitHub Copilot. This plan extends it to also support **opencode** as a second agent harness, additively — both can coexist in the same project repo.

##### Concept mapping

| GitHub Copilot | opencode | Notes |
|---|---|---|
| `.github/copilot-instructions.md` | `AGENTS.md` | Same markdown content, different path |
| `.github/skills/<name>/SKILL.md` | `.opencode/skills/<name>/SKILL.md` | **Identical** SKILL.md format |
| `.mcp.json` (`mcpServers` key) | `opencode.json` (`mcp.servers` key) | Same servers, different schema |
| `.github/agents/*.agent.md` | `.opencode/agents/<name>.md` | Different frontmatter schema |
| `.github/prompts/*.prompt.md` | `.opencode/commands/<name>.md` | Similar intent, different syntax |

##### Decisions

1. **Additive**: both harnesses get files written simultaneously. No "pick one" mode.
2. **Skills install to both dirs by default**. A `--agent copilot|opencode|all` flag restricts to one target when needed. Default is `all`.
3. **`opencode.json` `instructions` field** lists both `AGENTS.md` and `.github/copilot-instructions.md` so opencode picks up the unified instructions.
4. **Bundled opencode agents and commands** are shipped in package data and installed via `wingman opencode agent add` / `wingman opencode command add`.

##### File layout after implementation

```
# opencode-specific runtime config
AGENTS.md                          ← mirrors .github/copilot-instructions.md content
opencode.json                      ← mcp servers + instructions refs (both files)

# Skills — same SKILL.md installed in both locations
.github/skills/<name>/SKILL.md    ← Copilot (existing)
.opencode/skills/<name>/SKILL.md  ← opencode (new, identical content)

# opencode agents — opencode-format versions of the existing bundled Copilot agents
.opencode/agents/
  gilfoyle.md                      ← same prompt, opencode frontmatter
  marvin.md
  skill-reviewer.md
  yoda.md

# opencode commands (new — analogous to .github/prompts/*.prompt.md)
.opencode/commands/
  check.md                         ← /check → runs ruff + pytest gate
  review.md                        ← /review → @ mentions review agent
```

##### Planned code changes

###### 1. `src/wingman/core.py`

Add new output path constants:
```python
OPENCODE_AGENTS_MD   = Path("AGENTS.md")
OPENCODE_CONFIG      = Path("opencode.json")
OPENCODE_SKILLS_DIR  = Path(".opencode") / "skills"
```

Add new writer functions alongside existing Copilot writers:
- `assemble_opencode_config(stack)` → builds `opencode.json` dict with merged MCP servers (under `mcp.servers`) plus `instructions: ["AGENTS.md", ".github/copilot-instructions.md"]`
- `write_agents_md(stack, dry_run)` → writes `AGENTS.md` (same content as copilot-instructions)
- `write_opencode_config(stack, dry_run)` → writes `opencode.json`

###### 2. `src/wingman/skills.py`

- Rename `SKILLS_DIR` → `COPILOT_SKILLS_DIR` (keep old name as alias for back-compat)
- Add `OPENCODE_SKILLS_DIR = Path(".opencode") / "skills"`
- Add `agent: str = "all"` parameter to `add()`, `add_set()`, `update()`, `remove()`
- `_target_dirs(agent)` helper returns list of dirs to operate on
- `fetch_skill()` gains `dest` list support — copies to all target dirs
- `list_skills()` gains `agent` param to filter by target

###### 3. `src/wingman/sync.py`

- Update import: `SKILLS_DIR` → `COPILOT_SKILLS_DIR`
- Pass `agent="all"` to skill operations so synced skills land in both dirs

###### 4. `src/wingman/data/opencode/` *(not needed — removed)*

No bundled data directory. Both agents and commands are generated directly into the project repo by `wingman init` / the opencode module (see sections 5 and 6).

###### 5. Copilot → opencode agent translation *(new)*

When writing `.opencode/agents/`, wingman reads each installed `.github/agents/*.agent.md` and translates the frontmatter. The **prompt body is copied unchanged**.

Frontmatter translation rules:
- `description` → kept as-is
- `tools: [read, search]` → `mode: subagent` (all persona agents are subagents)
- If tools list lacks write/edit tools → `permissions: {edit: deny}`
- If tools list lacks `bash`/`shell` → `permissions: {bash: deny}`
- `user-invocable` → dropped (opencode subagents are always @ mentionable)
- Filename: `<name>.agent.md` → `<name>.md`

Example — `yoda.agent.md`:
```yaml
# Copilot (source)                 # opencode (generated)
description: "Mentor and teach…"  description: "Mentor and teach…"
tools: [read, search]              mode: subagent
user-invocable: true               permissions:
                                     edit: deny
                                     bash: deny
```

###### 6. opencode command generation *(new)*

Commands are generated directly into `.opencode/commands/` by `wingman init`.
Content is hardcoded in `opencode.py` — no bundled data files needed.

Two starter commands:
- `check.md` — runs the project's lint/format/test gate
- `review.md` — invokes the review subagent via @ mention

```markdown
# .opencode/commands/check.md
---
description: Run lint and test gate
---
Run the project check gate:
!`uv run ruff check --fix && uv run ruff format && uv run pytest`
```

These are generated once by `wingman init` and then belong to the project (users can edit them freely).

Both are implemented in `opencode.py`:
- `write_opencode_agents(dry_run) -> list[str]` — translates all installed agents
- `write_opencode_commands(dry_run) -> list[str]` — writes starter commands

###### 7. `src/wingman/catalog.py`

No changes needed — opencode agents and commands are not catalog items.

###### 8. `src/wingman/cli.py`

**`init` command** — extend to write opencode files:
```
wingman init [--stack STACK] [--dry-run]
```
Now also writes `AGENTS.md`, `opencode.json`, and translates any installed `.github/agents/` to `.opencode/agents/`.

**`sync` command** — no change to signature; skills land in both dirs via skills.py.

**`skill` sub-commands** — add `--agent` flag:
```
wingman skill add <name> [--agent all|copilot|opencode]
wingman skill remove <name> [--agent all|copilot|opencode]
wingman skill update [name] [--agent all|copilot|opencode]
```

**New `opencode` sub-typer**:
```
wingman opencode agent list   ← shows installed .github/agents/ + opencode translation status
wingman opencode agent sync   ← (re)translate all .github/agents/ → .opencode/agents/
```
Commands are written by `wingman init` and not separately managed (users edit them freely in `.opencode/commands/`).

###### 9. `tests/test_opencode.py` *(new)*

Tests covering:
- `write_agents_md` writes `AGENTS.md` with correct content
- `write_opencode_config` writes `opencode.json` with `mcp` + `instructions` keys
- `translate_agent` correctly rewrites Copilot frontmatter to opencode format
- `write_opencode_agents` translates all installed `.github/agents/` files
- `write_opencode_commands` writes `.opencode/commands/check.md` and `review.md`
- Dual skill install: `skills.add()` creates files in both `.github/skills/` and `.opencode/skills/`
- `--agent copilot` restricts to only `.github/skills/`
- `--agent opencode` restricts to only `.opencode/skills/`

###### 10. `tests/test_skills.py` — update existing tests

Tests that reference `skills.SKILLS_DIR` update to `skills.COPILOT_SKILLS_DIR`.

##### Implementation order

1. `core.py` — new constants + writers
2. `opencode.py` *(new)* — `translate_agent()`, `write_opencode_agents()`, `write_opencode_commands()`
3. `skills.py` — dual-target logic (COPILOT_SKILLS_DIR rename + agent param)
4. `sync.py` — fix import after rename
5. `cli.py` — init extension + opencode sub-typer + skill --agent flag
6. `tests/test_opencode.py` + update `test_skills.py` + `test_core.py`
7. Lint: `uv run ruff check --fix && uv run ruff format`
8. Full test run: `uv run pytest`

##### Out of scope

- opencode TUI config (`tui.json`) — user preference, not project config
- opencode plugins — no equivalent in Copilot; separate concern
- `catalog.py` changes — no new catalog kinds needed
- Migrating existing Copilot-only repos automatically — `wingman init` is idempotent, re-running it adds the opencode files



<a id="issue-3"></a>

### #3: Add support for goose

Source: https://github.com/plugin-healthcare/tara/issues/3.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

#### Porting Wingman to goose

**Date:** 2026-06-28
**Source project:** <https://github.com/plugin-healthcare/wingman>
**Target:** goose-compatible repository layout using `.agents/`, `.goose/recipes/`, and goose configuration patterns.
**Agent used:** GPT-5.5 on Github Copilot

##### Executive summary

Wingman is a GitHub Copilot guardrail toolkit. Its repository artifacts are organized around GitHub Copilot conventions:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `.github/agents/*.agent.md`
- `.github/prompts/**/*.prompt.md`
- `.mcp.json`
- `.wingman/skills.toml` and `.wingman/skills.lock`

The goose port should preserve the original Wingman guardrails while translating runtime behavior into goose-supported mechanisms:

- Use `.agents/plugins/wingman/` as the single project plugin bundle for Open Plugins-compatible skills, hooks, stdio MCP servers, source-copy agents, source-copy prompts, and helper scripts.
- Keep goose-discoverable custom agents in `.agents/agents/` only if direct `@agent-name` invocation is required; otherwise preserve source agents under the plugin bundle.
- Use `.goose/recipes/` for recipe-backed slash commands.
- Convert `.github/copilot-instructions.md` into project context as `AGENTS.md` at the repository root.
- Convert HTTP MCP server entries from `.mcp.json` into goose `extensions` configuration.

##### Current Wingman artifacts inspected

The Wingman repository currently contains these relevant files:

```text
.github/
  agents/
    gilfoyle.agent.md
    marvin.agent.md
    skill-reviewer.agent.md
    yoda.agent.md
  copilot-instructions.md
  instructions/
    python.instructions.md
  prompts/
    plan.prompt.md
    review.prompt.md
    python/
      add-types.prompt.md
      fix-lint.prompt.md
.mcp.json
.wingman/
  skills.toml
  skills.lock
```

No `.github/skills/` or `.github/hooks/` directory was present when inspected.

##### Recommended target directory structure

Use the Open Plugins project plugin as the primary organizing boundary:

```text
.
├── AGENTS.md
│
├── .agents/
│   └── plugins/
│       └── wingman/
│           ├── .plugin/
│           │   └── plugin.json
│           ├── agents/
│           │   ├── gilfoyle.md
│           │   ├── marvin.md
│           │   ├── skill-reviewer.md
│           │   └── yoda.md
│           ├── instructions/
│           │   └── python.md
│           ├── skills/
│           │   └── <skill-name>/
│           │       ├── SKILL.md
│           │       └── <supporting files>
│           ├── hooks/
│           │   └── hooks.json
│           ├── scripts/
│           │   ├── audit.py
│           │   ├── check.py
│           │   ├── sync.py
│           │   └── <hook scripts>
│           ├── commands/
│           │   ├── plan.md
│           │   ├── review.md
│           │   └── python/
│           │       ├── add-types.md
│           │       └── fix-lint.md
│           └── .mcp.json
│
└── .goose/
    ├── config.yaml
    └── recipes/
        ├── plan.yaml
        ├── review.yaml
        ├── python-add-types.yaml
        └── python-fix-lint.yaml
```

Important caveats:

1. Goose discovers project plugins from `.agents/plugins/<plugin-name>/`, plural `plugins`. The singular `.agents/plugin/wingman/` path is not documented and should not be used for runtime discovery.
2. Goose documentation says Open Plugins support skills and hooks. Goose source also supports plugin `.mcp.json` for stdio MCP servers. Goose documentation does not currently document plugin `agents/`, `commands/`, or `instructions/` as auto-loaded runtime components.
3. Therefore `.agents/plugins/wingman/agents/`, `.agents/plugins/wingman/commands/`, and `.agents/plugins/wingman/instructions/` are source-preservation locations unless a future goose version documents plugin-agent or plugin-command discovery.
4. If direct goose custom-agent invocation is required, duplicate or symlink the agent files into `.agents/agents/`. The simplified structure avoids that duplicate by default.
5. `AGENTS.md` should live at the repository root, not `.agents/AGENTS.md`, if the goal is automatic project instruction loading. Goose looks for `AGENTS.md` and `.goosehints` in the working directory hierarchy by default. A `.agents/AGENTS.md` file is treated as a global agents-home instructions file only when it is in the user agents home, not as a project-local context file inside the repository.

##### Mapping table

| Wingman source | goose target | Porting notes |
|---|---|---|
| `.github/agents/gilfoyle.agent.md` | `.agents/plugins/wingman/agents/gilfoyle.md` | Source-preservation plugin location. Duplicate to `.agents/agents/gilfoyle.md` only if goose direct `@gilfoyle` invocation is required. |
| `.github/agents/marvin.agent.md` | `.agents/plugins/wingman/agents/marvin.md` | Source-preservation plugin location. Duplicate to `.agents/agents/marvin.md` only if direct invocation is required. |
| `.github/agents/skill-reviewer.agent.md` | `.agents/plugins/wingman/agents/skill-reviewer.md` | Source-preservation plugin location. Duplicate to `.agents/agents/skill-reviewer.md` only if direct invocation is required. |
| `.github/agents/yoda.agent.md` | `.agents/plugins/wingman/agents/yoda.md` | Source-preservation plugin location. Duplicate to `.agents/agents/yoda.md` only if direct invocation is required. |
| `.github/prompts/plan.prompt.md` | `.agents/plugins/wingman/commands/plan.md` and `.goose/recipes/plan.yaml` | Preserve source command text, then convert to recipe for goose slash-command use. |
| `.github/prompts/review.prompt.md` | `.agents/plugins/wingman/commands/review.md` and `.goose/recipes/review.yaml` | Preserve source and generate recipe. |
| `.github/prompts/python/add-types.prompt.md` | `.agents/plugins/wingman/commands/python/add-types.md` and `.goose/recipes/python-add-types.yaml` | Use recipe-backed slash command such as `/python-add-types`. |
| `.github/prompts/python/fix-lint.prompt.md` | `.agents/plugins/wingman/commands/python/fix-lint.md` and `.goose/recipes/python-fix-lint.yaml` | Use recipe-backed slash command such as `/python-fix-lint`. |
| `.github/instructions/python.instructions.md` | `.agents/plugins/wingman/instructions/python.md`; optionally `AGENTS.md` or `.agents/plugins/wingman/skills/python-conventions/SKILL.md` | GitHub `applyTo` globs do not directly map to goose project instructions. |
| `.github/copilot-instructions.md` | `AGENTS.md` | Put active project instructions at repository root for automatic goose context loading. Preserve original wording or adapt it from Copilot to goose. |
| `.github/skills/<name>/SKILL.md`, if added later | `.agents/plugins/wingman/skills/<name>/SKILL.md` | Preserve supporting files. |
| `.github/hooks/*`, if added later | `.agents/plugins/wingman/hooks/hooks.json` plus scripts | Goose hooks live in plugins and currently support command hooks. |
| `.mcp.json` | Split between `.agents/plugins/wingman/.mcp.json` and `.goose/config.yaml` | Stdio entries can become plugin `.mcp.json`; HTTP entries should become goose `streamable_http` extensions. |
| `.wingman/skills.toml` and `.wingman/skills.lock` | `.agents/plugins/wingman/skills/` | Vendor locked skill versions or generate this directory from the lock file. |
| `src/wingman/audit.py` | `.agents/plugins/wingman/scripts/audit.py` | Deterministic guardrail artifact linter. Keep optional LLM review out of this script. |
| `src/wingman/check.py` | `.agents/plugins/wingman/scripts/check.py` | Deterministic check-gate runner for lint/format/test commands. |
| `src/wingman/sync.py` | `.agents/plugins/wingman/scripts/sync.py` | Deterministic installed-package skill discovery/sync script. Adapt output paths from `.github/skills/` to `.agents/plugins/wingman/skills/`. |

##### Wingman deterministic script modules

The `src/wingman/*.py` modules were reviewed to distinguish deterministic helper scripts from library/runtime modules. The assumption that exactly three modules should move under `.agents/plugins/wingman/scripts/` is technically correct for the simplified plugin-centered layout. Goose documentation describes scripts as supporting files in skills and plugins, and hook scripts under plugin `scripts/`; it does not document `.agents/scripts` as an automatically loaded component.

The three modules to extract are:

| Module | Why it is deterministic | Target | Porting notes |
|---|---|---|---|
| `src/wingman/audit.py` | Parses local Markdown/frontmatter and emits deterministic findings. It does not invoke a model. | `.agents/plugins/wingman/scripts/audit.py` | Keep the deterministic linter. Do not fold in `review.py`; that module shells out to Copilot for optional LLM review. |
| `src/wingman/check.py` | Loads check commands from `.wingman/checks.toml` or bundled defaults and runs them in order. Given the same repo and environment, behavior is deterministic. | `.agents/plugins/wingman/scripts/check.py` | Retarget default config paths as needed for goose, for example a plugin-local config file or a recipe parameter. |
| `src/wingman/sync.py` | Runs a fixed discovery script in the project `uv` environment, parses discovered `SKILL.md` files, and copies them into a target skills directory. | `.agents/plugins/wingman/scripts/sync.py` | Change `SKILLS_DIR` usage so synced skills land in `.agents/plugins/wingman/skills/` rather than `.github/skills/`. |

The other Python modules should not be moved wholesale into the plugin scripts directory:

- `cli.py` is a Typer command dispatcher, not a deterministic helper script by itself.
- `core.py` and `catalog.py` are library/orchestration modules used by multiple commands. Port their useful constants/helpers into the scripts only where needed.
- `skills.py` performs git fetch/install/update operations and is better treated as implementation support for vendoring skills, not a deterministic runtime helper script.
- `docs.py` probes PyPI and remote documentation URLs and mutates MCP config, so it is network-dependent rather than purely deterministic.
- `review.py` shells out to the Copilot CLI for an LLM review and is explicitly non-deterministic.
- `__init__.py` is package metadata only.

Recommended script layout:

```text
.agents/plugins/wingman/scripts/
├── audit.py
├── check.py
└── sync.py
```

These scripts can be referenced from goose recipes, skills, or hooks when needed. This layout also matches goose hook documentation, which uses plugin-local `scripts/` with `${PLUGIN_ROOT}`.

##### Open Plugins investigation

Open Plugins defines a plugin as a self-contained directory with optional manifest metadata and default component locations.

The relevant Open Plugins default layout is:

```text
my-plugin/
├── .plugin/
│   └── plugin.json
├── commands/
├── agents/
├── skills/
├── rules/
├── hooks/
│   └── hooks.json
├── .mcp.json
├── .lsp.json
├── scripts/
└── assets/
```

The Open Plugins specification says tools should ignore component types they do not support. That matters for goose because goose does not document support for every Open Plugins component.

###### goose Open Plugins compatibility

| Open Plugins component | goose support assessment | Plan |
|---|---|---|
| `skills/` | Supported by goose plugins. Skills are namespaced with the plugin name. | Use `.agents/plugins/wingman/skills/`. |
| `hooks/hooks.json` | Supported by goose plugins. Goose currently supports `command` actions. | Use `.agents/plugins/wingman/hooks/hooks.json`. |
| `.mcp.json` | Supported in goose source for plugin stdio MCP servers. Not emphasized in official docs. | Use only for stdio MCP entries. |
| `agents/` | Open Plugins supports this, but goose docs document project agents under `.agents/agents/` and do not document plugin-agent discovery. | Keep agents under `.agents/plugins/wingman/agents/` as source copies; duplicate to `.agents/agents/` only if direct invocation is required. |
| `commands/` | Open Plugins supports slash-command skills, but goose slash commands are recipe-backed. | Preserve source prompts in `commands/`, but generate `.goose/recipes/*.yaml`. |
| `rules/*.mdc` | Not documented as goose plugin support. | Convert to `.goosehints` or `AGENTS.md` if needed. |
| `.lsp.json` | Not documented as goose plugin support. | Omit unless future goose support is confirmed. |

###### Recommended plugin manifest

Create:

```text
.agents/plugins/wingman/.plugin/plugin.json
```

with:

```json
{
  "name": "wingman",
  "version": "0.1.0",
  "description": "Wingman guardrails ported to goose as Open Plugins-compatible skills, hooks, and stdio MCP servers.",
  "skills": "./skills/",
  "hooks": "./hooks/hooks.json",
  "mcpServers": "./.mcp.json"
}
```

Do not list `agents`, `commands`, or `instructions` in the manifest for goose runtime behavior unless goose documents support for those plugin components. Keep those directories in the plugin as source-preservation locations.

Open Plugins component paths should be relative to the plugin root and start with `./`.

##### `.mcp.json` investigation

###### Conclusion

Goose should not be expected to consume Wingman's repository-root `.mcp.json` directly.

Goose can load an Open Plugins-style `.mcp.json` from an enabled plugin directory, for example:

```text
.agents/plugins/wingman/.mcp.json
```

However, goose's plugin `.mcp.json` support is for stdio MCP servers with this shape:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "some-command",
      "args": ["arg1"],
      "env": {
        "KEY": "value"
      },
      "cwd": "${PLUGIN_ROOT}"
    }
  }
}
```

The server is converted to a goose stdio extension named:

```text
<plugin-name>:<server-name>
```

Goose source indicates `${PLUGIN_ROOT}` is expanded in `command`, `args`, `env`, and `cwd`.

###### Wingman `.mcp.json` compatibility

Wingman's current `.mcp.json` is mixed:

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git"]
    },
    "polars": {
      "type": "http",
      "url": "https://mcp.pola.rs/mcp"
    },
    "docs": {
      "command": "uvx",
      "args": [
        "--from",
        "mcpdoc",
        "mcpdoc",
        "--urls",
        "Pydantic:https://docs.pydantic.dev/latest/llms.txt",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

| Server | Current shape | Plugin `.mcp.json` compatible? | Porting action |
|---|---:|---:|---|
| `github` | HTTP `type` + `url` | No | Convert to goose `streamable_http` extension. |
| `git` | stdio `command` + `args` | Yes | Move to plugin `.mcp.json` or convert to goose `stdio` extension. |
| `polars` | HTTP `type` + `url` | No | Convert to goose `streamable_http` extension. |
| `docs` | stdio `command` + `args` | Yes | Move to plugin `.mcp.json` or convert to goose `stdio` extension. |

###### Recommended split

Use `.agents/plugins/wingman/.mcp.json` for stdio servers only:

```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git"]
    },
    "docs": {
      "command": "uvx",
      "args": [
        "--from",
        "mcpdoc",
        "mcpdoc",
        "--urls",
        "Pydantic:https://docs.pydantic.dev/latest/llms.txt",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

Use goose config for HTTP servers:

```yaml
extensions:
  github:
    enabled: true
    name: github
    type: streamable_http
    uri: "https://api.githubcopilot.com/mcp/"
    timeout: 300
    description: "GitHub Copilot MCP endpoint."

  polars:
    enabled: true
    name: polars
    type: streamable_http
    uri: "https://mcp.pola.rs/mcp"
    timeout: 300
    description: "Polars MCP server."
```

Caveat: goose documentation clearly documents the primary config file as `~/.config/goose/config.yaml`. It documents local recipes under `.goose/recipes/`, but does not clearly state that a repository-local `.goose/config.yaml` is automatically loaded. Treat `.goose/config.yaml` as a checked-in project template or merge target unless the target goose version or wrapper confirms local config loading.

##### Agent conversion details

Each Wingman agent has Copilot-style frontmatter similar to:

```yaml
---
description: "..."
tools: [read, search]
user-invocable: true
---
```

For source preservation in the simplified structure, convert agents to Markdown files with `name` frontmatter under `.agents/plugins/wingman/agents/`. If direct goose invocation is required, duplicate these files under `.agents/agents/`, which is the goose-documented project-agent location:

```markdown
---
name: marvin
description: "Plan and review work to an exacting standard in the gloomy, brilliant voice of Marvin the Paranoid Android."
---

You are Marvin, the Paranoid Android...
```

Conversion rules:

1. Rename `*.agent.md` to `<name>.md`.
2. Add `name: <name>`.
3. Keep `description`.
4. Store the source copy in `.agents/plugins/wingman/agents/`.
5. Duplicate to `.agents/agents/` only when direct goose `@agent-name` invocation is required.
6. Drop unsupported Copilot frontmatter such as `tools` and `user-invocable`.
7. If tool restrictions matter, move them into the body as guidance.

##### Prompt and slash command conversion details

Goose custom slash commands are recipe-backed. Convert Wingman's `.github/prompts/**/*.prompt.md` files into `.goose/recipes/*.yaml`.

Example recipe for `plan.prompt.md`:

```yaml
version: "1.0.0"
title: "Plan"
description: "Plan before implementing. Use when about to start a feature, fix, or refactor to think it through first."
instructions: |
  Before writing any code, produce a concise implementation plan:

  1. Restate the goal in one sentence.
  2. List the files/modules that will change and why.
  3. Identify edge cases, unknowns, or risks.
  4. Propose the sequence of steps.

  Do not write code yet. Wait for confirmation before proceeding.
```

Example slash command mappings:

```yaml
slash_commands:
  - command: "plan"
    recipe_path: ".goose/recipes/plan.yaml"
  - command: "review"
    recipe_path: ".goose/recipes/review.yaml"
  - command: "python-add-types"
    recipe_path: ".goose/recipes/python-add-types.yaml"
  - command: "python-fix-lint"
    recipe_path: ".goose/recipes/python-fix-lint.yaml"
```

##### Instructions conversion details

###### `.github/copilot-instructions.md`

Convert this file to repository-root project context:

```text
AGENTS.md
```

This is preferable to `.agents/AGENTS.md` for project-local instructions. Goose documentation says it looks for `AGENTS.md` and `.goosehints` at each level of the working-directory hierarchy by default. Goose source confirms project hint loading checks the working directory and ancestors for configured context filenames.

A `.agents/AGENTS.md` path should not be used for this project-local file. Goose source separately supports a global agents-home `AGENTS.md`, but that is for the user agents home, not a repository-local `.agents/AGENTS.md` file.

The migrated `AGENTS.md` should adapt Copilot-specific wording to goose where needed:

```markdown
# Project instructions

This project uses Python and uv.

Follow these project conventions:
- Plan before implementing non-trivial changes.
- Work in small, reviewable increments.
- Run tests and lint before considering work complete.
- Use uv for dependency and environment management.
- Use ruff for linting and formatting.
- Prefer pathlib.Path over os.path.
- Prefer polars over pandas for tabular data.
- Use pytest for tests.
- Do not commit secrets, credentials, or local config files.
```

###### `.github/instructions/python.instructions.md`

Preserve the source under the plugin bundle:

```text
.agents/plugins/wingman/instructions/python.md
```

Then either:

1. Fold the Python conventions into root `AGENTS.md`, or
2. Convert them into a loadable skill at `.agents/plugins/wingman/skills/python-conventions/SKILL.md`.

##### Skills conversion details

The current Wingman repository tracks external skills in `.wingman/skills.toml` and `.wingman/skills.lock`.

Recommended approach:

1. Treat `.wingman/skills.lock` as the source of pinned skill versions.
2. Fetch each locked repository/path/commit.
3. Copy each skill directory into:

   ```text
   .agents/plugins/wingman/skills/<skill-name>/
   ```

4. Preserve supporting files such as `references/`, `scripts/`, `templates/`, and assets.
5. Ensure each `SKILL.md` has goose-compatible frontmatter:

   ```yaml
   ---
   name: <skill-name>
   description: <when goose should use this skill>
   ---
   ```

When installed or discovered as an Open Plugin, goose namespaced skill names may appear as `wingman:<skill-name>`.

##### Hooks conversion details

No Wingman `.github/hooks/` directory was present when inspected.

If hooks are added later, convert them into:

```text
.agents/plugins/wingman/
├── hooks/
│   └── hooks.json
└── scripts/
    └── <script>.sh
```

Example goose-compatible hook:

```json
{
  "hooks": {
    "AfterFileEdit": [
      {
        "matcher": "\\.py$",
        "hooks": [
          {
            "type": "command",
            "command": "${PLUGIN_ROOT}/scripts/after-python-edit.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

Goose currently supports command hooks. Do not use Open Plugins `prompt` or `agent` hook actions unless goose support is confirmed.

##### Implementation phases

###### Phase 1: Preserve source artifacts

Create the target directories and copy Wingman source artifacts into stable source-preservation locations:

```text
AGENTS.md
.agents/plugins/wingman/commands/
.agents/plugins/wingman/agents/
.agents/plugins/wingman/instructions/
```

###### Phase 2: Convert custom agents

Convert each `.github/agents/*.agent.md` file into `.agents/plugins/wingman/agents/*.md` with normalized frontmatter. Duplicate into `.agents/agents/*.md` only if direct goose custom-agent discovery is required.

###### Phase 3: Extract deterministic Wingman scripts

Create `.agents/plugins/wingman/scripts/` and port these modules as standalone helper scripts:

- `audit.py` for deterministic artifact linting
- `check.py` for check-gate execution
- `sync.py` for installed-package skill discovery and sync

During extraction, remove Copilot-specific output paths and retarget them to the goose/Open Plugins layout. In particular, any sync logic that wrote to `.github/skills/` should write to `.agents/plugins/wingman/skills/`. Keep `review.py` out of plugin scripts because it delegates to an LLM through the Copilot CLI.

###### Phase 4: Create the Open Plugin bundle

Create `.agents/plugins/wingman/.plugin/plugin.json`, then add:

- `skills/` for vendored skills
- `hooks/` if hooks exist later
- `.mcp.json` for stdio MCP servers only
- `commands/` to preserve original Copilot prompt source

###### Phase 5: Convert prompts into recipes

Generate `.goose/recipes/*.yaml` from `.github/prompts/**/*.prompt.md`.

###### Phase 6: Configure slash commands

Add recipe-backed slash command mappings to the goose config template.

###### Phase 7: Convert project instructions

Create repository-root `AGENTS.md` from the core rules in `.github/copilot-instructions.md` and `.github/instructions/python.instructions.md`. Keep `.agents/plugins/wingman/instructions/python.md` as the source-preserved scoped instruction file.

###### Phase 8: Convert MCP configuration

Split Wingman's `.mcp.json`:

- Move stdio servers (`git`, `docs`) into plugin `.mcp.json`, or convert them to goose `stdio` extensions.
- Convert HTTP servers (`github`, `polars`) to goose `streamable_http` extensions.

###### Phase 9: Validate

Validate these outcomes:

- `.agents/plugins/wingman/agents/*.md` source-copy files have `name` frontmatter and non-empty bodies.
- If direct goose agent invocation is required, corresponding `.agents/agents/*.md` files also exist.
- `.agents/plugins/wingman/.plugin/plugin.json` has a valid Open Plugins name and relative component paths.
- `.agents/plugins/wingman/scripts/audit.py`, `.agents/plugins/wingman/scripts/check.py`, and `.agents/plugins/wingman/scripts/sync.py` exist and do not depend on Copilot-only runtime paths.
- `.agents/plugins/wingman/skills/*/SKILL.md` exists for every vendored skill.
- `.agents/plugins/wingman/.mcp.json` contains only stdio-compatible MCP server entries.
- `.goose/recipes/*.yaml` files include `version`, `title`, `description`, and `instructions` or `prompt`.
- Root `AGENTS.md` exists for project instructions; no reliance is placed on `.agents/AGENTS.md` for project-local context.
- Slash command names are unique and contain no spaces.
- No secrets or credentials are committed.

##### Key risks and decisions

1. **`.goose/recipces/` is likely a typo.** Use `.goose/recipes/`.
2. **Repo-local `.goose/config.yaml` auto-loading is not clearly documented.** Treat it as a template or merge target unless verified in the target environment.
3. **Goose docs document Open Plugins skills and hooks.** Goose source also supports plugin `.mcp.json`, but this is not as prominent in the docs.
4. **Open Plugins `.mcp.json` is stdio-oriented.** Wingman's HTTP `type` + `url` MCP entries need conversion.
5. **Open Plugins `commands/` do not replace goose recipe-backed slash commands.** Generate recipes for runtime use.
6. **Open Plugins `agents/`, `rules/`, and `.lsp.json` should not be assumed to work in goose.** Use goose-documented equivalents.
7. **`.agents/plugins/wingman/scripts/` is a plugin-local supporting-files location, not an auto-invoked goose component.** Reference these scripts explicitly from recipes, skills, or hooks.
8. **`.agents/plugin/wingman/` singular is not a goose-discovered project plugin location.** Use `.agents/plugins/wingman/`.
9. **`.agents/AGENTS.md` is not the right project-local instruction path.** Use root `AGENTS.md` for automatic project hints.

##### Verification sources

###### Official goose documentation used

- `docs/guides/context-engineering/plugins.md`
- `docs/guides/context-engineering/hooks.md`
- `docs/guides/context-engineering/using-skills.md`
- `docs/guides/context-engineering/custom-agents.md`
- `docs/guides/context-engineering/slash-commands.md`
- `docs/guides/context-engineering/using-goosehints.md`
- `docs/guides/config-files.md`
- `docs/getting-started/using-extensions.md`
- `docs/guides/recipes/recipe-reference.md`
- `docs/guides/recipes/storing-recipes.md`

###### Wingman source checked for deterministic scripts

The following Wingman modules were inspected and classified:

- `src/wingman/audit.py`
- `src/wingman/check.py`
- `src/wingman/sync.py`
- `src/wingman/review.py`
- `src/wingman/docs.py`
- `src/wingman/skills.py`
- `src/wingman/catalog.py`
- `src/wingman/core.py`
- `src/wingman/cli.py`
- `src/wingman/__init__.py`

Only `audit.py`, `check.py`, and `sync.py` meet the deterministic-helper-script bar for `.agents/plugins/wingman/scripts/`.

###### Goose source checked for `.mcp.json`

The official docs did not clearly describe plugin `.mcp.json` support, so the following goose source files were checked:

- `crates/goose/src/plugins/formats/open_plugins.rs`
- `crates/goose/src/plugins/mcp_servers.rs`
- `crates/goose/src/plugins/discovery.rs`
- `crates/goose/src/hooks/mod.rs`
- `crates/goose-cli/src/session/builder.rs`

Findings from source:

- Open Plugins plugin discovery recognizes `.mcp.json`.
- Plugin `.mcp.json` is parsed as a document with top-level `mcpServers`.
- Each MCP server must have a non-empty `command`.
- Supported plugin MCP server fields are `command`, `args`, `env`, and `cwd`.
- Plugin MCP servers are converted into stdio goose extensions.
- Plugin MCP server names are namespaced as `<plugin-name>:<server-name>`.

###### Open Plugins documentation used

- <https://open-plugins.com/plugin-builders/specification>
- <https://open-plugins.com/agent-builders/components/mcp-servers>
- <https://open-plugins.com/agent-builders/components/skills>
- <https://open-plugins.com/agent-builders/components/hooks>
- <https://open-plugins.com/agent-builders/components/agents>
- <https://open-plugins.com/agent-builders/components/rules>
- <https://open-plugins.com/agent-builders/components/lsp-servers>

##### Documentation links

- <https://goose-docs.ai/docs/guides/context-engineering/plugins>
- <https://goose-docs.ai/docs/guides/context-engineering/hooks>
- <https://goose-docs.ai/docs/guides/context-engineering/using-skills>
- <https://goose-docs.ai/docs/guides/context-engineering/custom-agents>
- <https://goose-docs.ai/docs/guides/context-engineering/slash-commands>
- <https://goose-docs.ai/docs/guides/context-engineering/using-goosehints>
- <https://goose-docs.ai/docs/guides/config-files>
- <https://goose-docs.ai/docs/getting-started/using-extensions>
- <https://goose-docs.ai/docs/guides/recipes/recipe-reference>
- <https://goose-docs.ai/docs/guides/recipes/storing-recipes>
- <https://open-plugins.com/plugin-builders/specification>



<a id="issue-4"></a>

### #4: Restructure .github folder to Open Plugin specification

Source: https://github.com/plugin-healthcare/tara/issues/4.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

@yannick-vinkesteijn Refinement of #3 shows that GitHub Copilot is fully compatible with the [Open Plugin Specification v1.0.0](https://open-plugins.com/plugin-builders/specification).

Shouldn't we restructure the project to follow that specification, before implementing support for OpenCode (which btw also support the Open Plugin spec, so that would come 'for free') and goose (not fully compliant yet).



<a id="issue-9"></a>

### #9: WINGMAN - add roborev features

Source: https://github.com/plugin-healthcare/tara/issues/9.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

##### Scope needed

The published issue has no body.
Define the problem, owner, scope, dependencies, and acceptance criteria before scheduling implementation.
Do not infer requirements from the title alone.



<a id="issue-14"></a>

### #14: Spike: investigate storage structures for fast agent information storage and retrieval

Source: https://github.com/plugin-healthcare/tara/issues/14.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: proposed replacement, not posted.

#### Spike: storage structures for fast agent information storage and retrieval

##### Question to Answer
What shared information and retrieval operations do agents need beyond the current plain Markdown `.agents/` store, and is another storage structure justified?

##### Timebox
2 days

##### Background
Tara currently uses Markdown and indexes under `.agents/`, as documented in `src/tara/agent_docs.py` and `docs/agent-working-docs.md`.
This repository ignores `.agents/memory/`, so required continuation information must also have a shared record.
The old Wingman SQLite setup is historical, not the current baseline.
Compare alternatives only after defining the shared-information contract with #55 and the optional oxivault proposal in #29.

##### Approach
- Define what agents actually need: cheap append at each phase, fast lookup/query, no heavy deps, portable, human-inspectable.
- Compare options: SQLite (stdlib `sqlite3` / DuckDB `sqlite_scan`), a search tree / prefix index, an embedded key-value store, DuckDB or Parquet.
- Look at how roborev stores and retrieves this (see #9).
- Prototype the query paths an agent runs in practice.

##### Output
A recommendation, an ADR that confirms or supersedes ADR-0001, and follow-up stories.

##### Result
<!-- Filled in at the end of the spike -->

###### Findings


###### Recommendation


###### Follow-up stories
-

##### Proposed review follow-up (2026-10-12)

- [ ] Identify the minimum shared continuation state and the intended readers, including remote agents and colleagues.
- [ ] Measure the existing Markdown-and-index approach before adding a backend.
- [ ] Separate raw local session scratch from reviewed shared records.
- [ ] Keep plain documents usable without optional metadata or a database.
- [ ] Record a recommendation and remaining decisions before assigning backend implementation to a release.

This spike is unscheduled and does not block the 2.1.0 document-workflow improvements.



<a id="issue-15"></a>

### #15: Feature: add maplib and ottr skill

Source: https://github.com/plugin-healthcare/tara/issues/15.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

I expect we will be doing quite some RDF and SPARQL work, so maplib seems a relevant skill to include https://github.com/DataTreehouse/maplib-skill https://github.com/DataTreehouse/ottr-skill



<a id="issue-19"></a>

### #19: Spike and ADR: adopt open canonical agent formats

Source: https://github.com/plugin-healthcare/tara/issues/19.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

##### Goal

Determine whether Tara should use open, integration-neutral agent formats as its canonical source and generate product-specific files for Copilot, Claude Code, OpenCode, and future integrations.

Implementation is out of scope until the spike is complete and an ADR is accepted.

##### Motivation

Tara currently treats the GitHub Copilot `.github/` layout as its source of truth. This couples the domain model to one integration and requires other products to be projections of Copilot-specific files.

Relevant open projects and specifications include:

- [AGENTS.md](https://agents.md/) for project instructions
- [Agent Skills](https://agentskills.io/specification) for portable `SKILL.md` packages
- [Model Context Protocol](https://modelcontextprotocol.io/) for tool and data integrations
- [Agentic AI Foundation projects](https://aaif.io/projects)

##### Phase 1: spike

- [ ] Inventory Tara's current canonical and generated files.
- [ ] Verify what each open specification standardizes, including what it does not standardize.
- [ ] Confirm discovery locations supported by Copilot, Claude Code, OpenCode, and at least one additional open client.
- [ ] Evaluate `AGENTS.md` as the canonical instruction source.
- [ ] Evaluate a neutral Tara convention such as `.agents/skills/` for Agent Skills, clearly distinguishing Tara convention from specification mandate.
- [ ] Determine whether agents and prompts have portable standards or require Tara-owned neutral models.
- [ ] Evaluate MCP configuration portability. MCP standardizes the protocol, but clients may use different configuration locations and schemas.
- [ ] Design migration from existing `.github/`-canonical repositories without overwriting or deleting hand-written files.
- [ ] Produce a small compatibility matrix and prototype one round trip.

##### Phase 2: ADR

The ADR must decide:

- Canonical locations and schemas for instructions, skills, agents, prompts, and MCP configuration.
- Which locations are open standards versus Tara conventions.
- Adapter responsibilities and ownership boundaries.
- Migration and backward-compatibility policy.
- Whether generated integration files are committed.
- How additions, updates, removals, conflicts, and malformed files behave.
- How new integrations can be added without changing existing configuration semantics.

##### Proposed direction to evaluate

```text
Open or neutral canonical files
            |
            v
Tara integration adapters
            |
            +-- .github/
            +-- .claude/
            +-- .opencode/
```

##### Definition of done

- [ ] Spike findings are recorded under `.agents/design/` or `.agents/memory/`.
- [ ] ADR is created under `docs/decisions/`.
- [ ] Compatibility and migration risks are explicit.
- [ ] Follow-up implementation issues are created only after ADR acceptance.



<a id="issue-23"></a>

### #23: Add a sensitivity scan for content that should not be published

Source: https://github.com/plugin-healthcare/tara/issues/23.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

##### Problem

`gitleaks` in the pre-commit gate only matches credential *shapes* (token formats, private key blocks, high-entropy strings near keywords). It says nothing about sensitive *content*, which is the thing that actually bites when a repo is public.

Real example found while preparing `plugin-healthcare/pluginlake` (a public repo) for a commit. `gitleaks` passed clean on the staged files, while the staged `.agents/` docs contained:

- a curated list of currently unremediated weaknesses, with exact `file:line` pointers to the affected deployment and middleware code;
- a statement that the running deployment relies on network whitelisting rather than authentication;
- a named third-party security vendor plus a critical assessment of the quality of their paid report;
- a reference to a non-public PDF, and an internal audience ("security officer, product owner").

None of that is a credential, so no secret scanner would ever flag it. All of it was one `git push` away from a public repo.

##### Proposal

Add a sensitivity auditor to `tara audit`, rather than a separate parallel tool. The existing machinery already fits:

- `audit.Finding(path, level, message)` with `ERROR` / `WARNING` / `INFO`
- `_AUDITORS` keyed by artifact kind
- `--deep` already shells out to the Copilot CLI for LLM content review
- `--strict` and non-zero exit already wire it into a gate

Categories to detect:

- unremediated vulnerability detail: weaknesses tied to concrete `file:line`, exposed ports/services, missing authn/authz;
- named third parties: companies, vendors, partners, packages, especially with an evaluative or negative judgement attached;
- confidentiality markers: references to non-public documents, internal-only audiences, "vertrouwelijk"/"confidential";
- personal data: names, emails, participant lists in meeting and handover notes;
- commercial detail: pricing, quotes, contract or licensing terms.

Scope it to `.agents/` and `docs/` by default, since that is where prose accumulates.

##### Semi-structured output

Findings should be machine-readable, not just printed prose, so the scan can gate CI and be diffed between runs. Suggested per-finding fields:

```json
{
  "path": ".agents/review/20260909_second-opinion.md",
  "line": 19,
  "category": "unremediated-vulnerability",
  "severity": "error",
  "confidence": "high",
  "excerpt": "<redacted snippet>",
  "rationale": "Lists concrete unfixed weaknesses with file:line pointers",
  "recommendation": "Keep local or move to a private repo"
}
```

Add `--format json` and `--report-path`, mirroring how `gitleaks` reports, so the output can be consumed by CI. Keep the human-readable table as the default.

##### Notes

- Repository visibility matters: the same document is fine in a private mirror and not fine in a public repo. The auditor should take visibility into account, or at least let the caller declare it, so public repos get a stricter default.
- Deterministic pattern rules will not carry this on their own. The judgement calls ("is this vendor criticism a problem?") suit the existing `--deep` LLM path, with patterns handling the cheap, obvious cases first.
- Redact excerpts by default, as `gitleaks --redact` does, so the report itself does not leak the content it is warning about.



<a id="issue-28"></a>

### #28: Draft ADR: Adopt Vault-LD with graceful OKF compatibility

Source: https://github.com/plugin-healthcare/tara/issues/28.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

#### Draft ADR: Use Vault-LD for portable, progressively structured agent knowledge

- **Status:** Proposed
- **Date:** 2026-09-27
- **Authors:** @dkapitan, with AI-assisted research and drafting
- **ADR number:** Assign when this draft is promoted into `docs/decisions/`.

##### Context and Problem Statement

Tara's agent document store holds plans, designs, reviews, and handover notes as Markdown under `.agents/`, while finalized ADRs live in `docs/decisions/` and requirements primarily live in the issue tracker.
Its flat files and manually maintained indexes preserve working knowledge but do not provide typed relationships for retrieving architectural intent, understanding rejected alternatives, or tracing the impact of a change.
How can Tara make this knowledge queryable without replacing readable, Git-versioned documents with a service-owned database or requiring a graph engine for small projects?

###### Research baseline and decision drivers

The research inspected the locally known `origin/main` at `3ba1466`, where `src/tara/agent_docs.py` describes the flat store as an interim design and explicitly defers structured knowledge retention.
The feature branch used for the exploration predates that implementation; implementation work must first reconcile its baseline with main.
An older Parquet/DuckDB handoff ledger is historical, not the current migration target.

The decision must preserve:

- Human-readable, reviewable documents and their architectural rationale.
- Existing document locations, user-authored content, and `[agents] gitignore` privacy choices.
- A useful plain-Markdown mode without an ontology, database, embeddings, or model calls.
- Explicit semantics when projects need relationship-aware retrieval and impact analysis.
- Tara's role as a setup and guardrail toolkit, rather than a replacement agent runtime.
- Open formats and the ability to change query engines without rewriting authored knowledge.

##### Considered Options

| Option | Benefits | Why selected or not selected |
| --- | --- | --- |
| Keep the flat Markdown store | Lowest complexity; readable and already integrated | Retained as the usability baseline, but insufficient for typed retrieval and impact analysis |
| OKF alone | Minimal Markdown/YAML envelope, standard links, portable indexes, and optional provenance | Required compatibility floor, but does not supply the shared RDF semantics needed for the richer mode |
| Vault-LD with an OKF-compatible authoring profile | Adds explicit RDF semantics through an external context without abandoning Markdown | Selected: progressive adoption and a portable data model |
| Graft as the primary memory store | Generated code maps, structural relationships, and source-linked context | Not selected as the authority for architectural intent; defer an adapter for derived code evidence |
| Basic Memory | Ready-made Markdown memory, SQLite indexing, and MCP retrieval | Viable alternative, but its relation format is not Vault-LD-native and its current AGPL-3.0 license adds integration considerations |
| Graphiti or Cognee | Rich temporal or extracted knowledge and retrieval infrastructure | More operational and extraction machinery than required for the initial authored-document graph |
| MCP reference memory server | Simple local entity/relation storage | JSONL-oriented, with insufficient document lifecycle and semantic governance for this use case |

##### Decision Outcome

Chosen option: **Vault-LD as an optional semantic layer over an OKF-compatible Markdown knowledge store**, because it provides typed, portable relationships while allowing the same documents to remain useful without graph tooling.

Use the compatibility approach in [Vault-LD Appendix B](https://github.com/The-Knowledge-Graph-Guys/vault-ld/blob/main/SPEC.md#appendix-b-lifting-an-okf-bundle-compatibility-profile).
Add a Graft adapter in a later stage.
If measured query performance degrades as the graph grows, evaluate **maplib as the preferred scale-up query engine**, without changing the source format.

###### 1. Markdown is authoritative; graph stores are derived

Authored Markdown owns approved decisions, rationale, and explicit relationships.
The issue tracker remains authoritative for requirements and ticket state; local knowledge documents reference those records rather than becoming competing copies.
Code remains authoritative for implementation facts.

RDF exports, query indexes, and generated code maps are rebuildable artifacts, not independent editable sources of truth.
Deleting an index must not lose knowledge.
RDF export alone is not a complete backup: Vault-LD projects frontmatter into triples, while document bodies retain the prose and rationale.

Do not automatically rewrite accepted ADR bodies, migrate authored files, or replace existing indexes.
Changed decisions require successor ADRs; any migration of existing metadata or content requires a reviewable diff and approval.

###### 2. Graceful scale-down to OKF is a compatibility contract

Support two capability levels over the same documents:

| Capability | OKF-compatible baseline | Vault-LD semantic layer |
| --- | --- | --- |
| Reading and editing | Markdown and YAML in any editor | Identical authored files |
| Types | Plain strings such as `ArchitectureDecisionRecord` | Context maps those strings to class IRIs |
| Navigation | Standard Markdown body links and optional indexes | Adds explicit typed frontmatter relationships |
| Retrieval | File discovery, text search, metadata filtering, and navigational links | Adds typed traversal, validation, and impact queries |
| Runtime requirements | No RDF engine or model required | Local context resolution and an optional graph query implementation |

Use plain `type` values as described by Appendix B, rather than requiring class wikilinks in every note.
A minimal external context can lift those values into RDF:

```json
{
  "@context": {
    "@base": "https://example.org/project/knowledge/",
    "@vocab": "https://example.org/project/vocab#",
    "type": "@type"
  }
}
```

The namespace above is illustrative; each project must have a stable namespace.
Promote types and fields through explicit context mappings as their semantics mature.
Quote frontmatter wikilinks, for example `constrains: ["[[APIGateway]]"]`.

Adding or disabling the semantic layer must not require rewriting document bodies.
An OKF consumer must still be able to discover and navigate important relationships through ordinary Markdown links; wikilinks alone are insufficient for that fallback.
Typed frontmatter is authoritative for relationship semantics, and validation should flag contradictory navigation links rather than silently inventing or synchronizing relationships.
Body links remain navigational and are not automatically promoted to typed RDF edges.

When the semantic layer is intentionally absent, report the available capabilities and continue with baseline retrieval.
When a configured context is invalid or a graph rebuild fails, report the error or stale state explicitly; do not disguise failure as successful OKF fallback.

###### 3. Pin the compatibility profile and preserve metadata semantics

The canonical [OKF specification](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md) has moved from the older knowledge-catalog location linked by Vault-LD.
Pin the supported OKF version and Vault-LD revision, and maintain compatibility fixtures rather than assuming their specifications evolve in lockstep.

For the current OKF v0.2 profile:

- Keep `type` the only universally required concept field; unknown extension fields remain readable and preserved.
- Reserve `index.md` and `log.md` for navigation/history, not typed concept nodes.
- Keep those files outside the RDF graph; only the root index may carry OKF's permitted version metadata.
- Keep OKF lifecycle `status` values (`draft`, `stable`, `deprecated`) separate from ADR decision state, using an extension such as `decisionStatus` for `proposed`, `accepted`, or `superseded`.
- Preserve optional provenance and verification metadata; do not interpret a document's default `stable` status as human approval of a decision.
- Map nested metadata deliberately, including source identifiers, rather than globally aliasing every `id` field to JSON-LD `@id`.

Maintain both the document's OKF path identity and its RDF resource identity.
Use stable explicit absolute IRIs where rename-stable graph identity is required, with an explicit top-level context mapping.
Do not equate a mutable path with an immutable resource identifier.

Existing untyped Tara notes remain readable legacy documents, but must not be advertised as conforming OKF concepts or silently given authoritative graph semantics.

###### 4. Start with a small, explicit ontology and bounded retrieval

Begin with requirements, ADRs, design documents, components, data models, and curated lessons.
Add task and test-specification nodes where they provide useful traceability; do not turn every transient prompt into permanent shared knowledge.

Use relationships such as:

- Component `implements` Requirement.
- ADR `addresses` Requirement and `constrains` Component.
- ADR `supersedes` ADR.
- ADR `rejects` DesignAlternative, with rationale and applicability recorded in the linked documents.
- DesignDocument `documents` Component or DataModel.
- Component `dependsOn` Component or DataModel.

Use one consistent ADR class identifier.
Do not model alternative allowed types with multiple RDFS domains or ranges: those express intersection, not union.
Use appropriate shared classes or unions for semantics, and SHACL for validation.

Retrieve from explicit task links, changed code paths, or search seeds, then traverse relevant edge types in the appropriate directions.
Bound both nodes and context size, include source citations and inclusion paths, and distinguish empty results, stale evidence, and truncated results.
Context selection is not an authorization boundary.

###### 5. Treat freshness, provenance, and privacy as core behavior

Validate identities, link resolution, relation types, lifecycle state, and supersession cycles.
Broken links may remain readable in the OKF baseline; the stricter semantic profile reports them and can block promotion of incomplete knowledge to an approved state.

Track source paths, revisions or hashes, provenance, and whether assertions are authored or derived.
Code changes mark affected assertions as needing review; they do not prove that an architectural decision is wrong.
Agents propose knowledge changes, while human review determines acceptance.

Preserve existing local-only choices across discovery, indexing, exports, and generated navigation.
Do not allow a tracked graph export to publish notes excluded from the shared store.
Local indexing does not imply that retrieved content remains local once consumed by a remote model.

###### Consequences

- Good, because small projects retain a useful Markdown workflow without mandatory semantic infrastructure.
- Good, because the same documents can acquire shared semantics incrementally through a context.
- Good, because architectural intent remains reviewable in Git and independent of generated code maps.
- Good, because standard RDF provides a path to a different query engine without a content migration.
- Bad, because Tara must define and maintain compatibility, identity, and retrieval contracts.
- Bad, because ordinary navigation links and typed edges require consistency checks.
- Bad, because graph validation detects structural problems but cannot establish that architectural prose is true.
- Bad, because supporting multiple capability levels requires explicit degraded-mode behavior and cross-mode fixtures.

##### Architecture

```text
Authored Markdown: OKF-compatible envelope, prose, standard links
  |                                     |
  | no semantic layer                   | local context + explicit edges
  v                                     v
File/text/navigation retrieval       Vault-LD RDF projection
                                        |
                              Validation + derived local index
                                        |
                              Bounded context / impact queries
                                        |
                              Coding agent via CLI or MCP

Later: code -> Graft adapter -> provenance-labelled derived evidence
Later: RDF projection -> maplib query backend, if benchmarks justify it
```

Keep the initial implementation small: RDFLib for RDF handling and basic querying, with pySHACL for validation where needed.
Neither a database server nor an LLM extraction pipeline is required.
Obsidian is an optional authoring surface, not a runtime dependency; verify its handling of Tara's hidden `.agents/` folders before choosing any integration layout.

###### Deferred Graft adapter

Use Graft to supply observed code structure and source-linked evidence, not to regenerate accepted intent.
Keep derived assertions distinguishable from authored ones and link them through explicit component-to-source mappings.
Tara remains responsible for its harness configuration; avoid two tools independently rewriting the same instruction files.
Surface Graft freshness failures rather than assuming every returned result reflects the current code.

###### Conditional maplib query backend

If increasing graph size makes the initial backend miss an agreed query-latency or memory budget, benchmark [maplib](https://github.com/DataTreehouse/maplib) against the same RDF dataset and query fixtures.
Adopt it only if it preserves query semantics and materially improves the measured bottleneck.
Measure cold loading, warm-query p50/p95 latency, rebuild cost, and peak memory on representative repositories before setting a migration threshold.

maplib is a Rust-based RDF engine with Python bindings, SPARQL queries, and Polars DataFrame results.
Its current documentation describes an in-memory engine, so it is not automatically a solution to out-of-memory workloads.
Its mapping, querying, and serialization core is open source; its SHACL and Datalog functionality is not.
Limit the proposed integration to the open-source query functionality and retain independent validation.
Do not make maplib a default dependency or pre-build a general backend framework before evidence warrants it.

##### Rollout

1. Reconcile the implementation branch with the current `.agents/` store, pin the specifications, and define the OKF-compatible profile and minimal ontology.
2. Introduce opt-in templates and read-only discovery/indexing over existing document locations, with approved metadata migrations only.
3. Add bounded retrieval, graph validation, and explicit freshness/privacy handling; integrate them with Tara's existing skills, check gate, and optional local MCP wiring.
4. Verify that the same authored bundle remains usable with the semantic layer disabled and that enabling the context does not rewrite it.
5. Add the Graft adapter after authored-knowledge retrieval is useful and stable.
6. Evaluate maplib only when representative measurements demonstrate a size-related query bottleneck.

###### Acceptance criteria

- [ ] A minimal OKF-compatible bundle works without an RDF engine, ontology, or model call.
- [ ] Adding the pinned Appendix B context yields coarse RDF types and predicates without modifying concept files.
- [ ] Removing or disabling the semantic layer preserves readable rationale, discovery, and standard-link navigation.
- [ ] Invalid configured contexts and stale indexes are reported, not hidden by fallback.
- [ ] Typed retrieval includes applicable decisions, scoped rejection rationale, and supersession history within a bounded context.
- [ ] Rename, duplicate-name, incoming-edge, broken-link, and branch-switch cases have deterministic behavior.
- [ ] Source documents, existing indexes, and local-only knowledge are preserved during indexing and migration.
- [ ] Future Graft assertions cannot silently become accepted architectural decisions.
- [ ] A future maplib backend passes the same query-result fixtures before being enabled.

##### References

- [Tara agent document store at the research baseline](https://github.com/plugin-healthcare/tara/blob/3ba1466/src/tara/agent_docs.py).
- [Tara's ADR-writing guidance](https://github.com/plugin-healthcare/tara/blob/main/src/tara/data/catalog/skills/writing-adrs/SKILL.md).
- [Vault-LD specification and Appendix B](https://github.com/The-Knowledge-Graph-Guys/vault-ld/blob/main/SPEC.md#appendix-b-lifting-an-okf-bundle-compatibility-profile).
- [Canonical Open Knowledge Format specification](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md).
- [Graft](https://github.com/trailhq/Graft) and its [refresh behavior](https://github.com/trailhq/Graft/blob/main/src/graph/refresh.ts).
- [maplib capabilities and licensing](https://github.com/DataTreehouse/maplib).
- [Basic Memory](https://github.com/basicmachines-co/basic-memory), [Graphiti](https://github.com/getzep/graphiti), [Cognee](https://github.com/topoteretes/cognee), and the [MCP reference memory server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory).
- [RDFLib](https://github.com/RDFLib/rdflib), [pySHACL](https://github.com/RDFLib/pySHACL), and [RDFS domain semantics](https://www.w3.org/TR/rdf-schema/#ch_domain).



<a id="issue-29"></a>

### #29: Integrate oxivault as structured, queryable store for the `.agents/` doc store

Source: https://github.com/plugin-healthcare/tara/issues/29.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: proposed replacement, not posted.

##### Context

`src/tara/agent_docs.py` notes that "optimizing knowledge retention (a structured, queryable store) is deliberately deferred; this flat, greppable layout is the interim."
[oxivault](https://github.com/dkapitan/oxivault) (design:
`.agents/design/202609281044_oxivault-design.md`) is a Vault-LD knowledge graph store (Markdown + YAML-LD frontmatter → RDF, maplib/Polars, git or S3 backends)
that can fill this gap for agent memory, data collection and retrieval.

##### Proposal

1. **Skill via `tara sync`:** oxivault ships `.agents/skills/oxivault/SKILL.md` in its package; no tara changes needed beyond documenting it (and optionally an index/theme entry).
2. **Frontmatter in doc-store templates:** add light YAML-LD frontmatter to the plan/design/review/memory templates and `tara new adr`:
   `type`, `status`, `created`, `relatesTo: [[...]]`.
3. **`context.jsonld`:** `tara init` optionally writes a `.agents/context.jsonld` mapping those keys to IRIs, making `.agents/` a valid Vault-LD vault.
4. **Config:** optional `[agents] backend = "oxivault"` in `.tara/config.toml`;
   when set, prompts direct agents to query oxivault (CLI `--json` / API)
   instead of scanning `index.md`.
5. **Index generation:** optionally generate per-folder `index.md` from the graph.
6. **Audit:** `tara audit` checks frontmatter validity of doc-store notes.

##### Non-goals

- No change to `.mcp.json`: external MCP servers remain as-is; oxivault exposes no MCP server.
- Agents do not silently write shared knowledge; enrichment is suggestion-only.

##### Acceptance criteria

- [ ] Templates emit valid YAML-LD frontmatter; existing plain docs keep working.
- [ ] `tara init` can write `context.jsonld` (opt-in).
- [ ] `[agents] backend` config option documented and parsed by `TaraConfig`.
- [ ] `tara sync` picks up the oxivault skill (documented in `docs/skills.md`).
- [ ] `tara audit` flags invalid doc-store frontmatter.

##### Proposed review follow-up (2026-10-12)

The backend remains optional and unscheduled.
Agree on shared continuation state with #14 and #55 before adding backend-specific configuration.
Preserve plain Markdown and indexes as a working baseline.
Do not make an ignored local memory note the only record needed by a remote agent.
Do not bulk-publish existing ignored notes.
Verify the package's skill-discovery route before claiming it requires no Tara changes.

- [ ] The proposal distinguishes local scratch from reviewed shared records.
- [ ] Repositories without oxivault can still follow the complete workflow.
- [ ] The ADR records the measured benefit, ownership, migration, and fallback behavior.



<a id="issue-31"></a>

### #31: Add obra/superpowers as skill set

Source: https://github.com/plugin-healthcare/tara/issues/31.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

##### Scope needed

The published issue has no body.
Define the problem, owner, scope, dependencies, and acceptance criteria before scheduling implementation.
Do not infer requirements from the title alone.



<a id="issue-36"></a>

### #36: Add a scheduled health check for the skill index

Source: https://github.com/plugin-healthcare/tara/issues/36.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

##### Problem

Every theme in `src/tara/data/skills/index.toml` tracks a moving branch (`main` or `master`).
When an upstream repository renames or removes a skill folder, or changes the `name:` in a `SKILL.md`, `tara skill add <theme>` breaks, and nobody notices until a user runs it.

##### Required changes

- Add a scheduled CI job (weekly, and on changes to `index.toml`) that resolves every theme against its upstream `ref`.
- Fail when a member path is missing or a `SKILL.md` `name:` does not match the member name.
- Report each skill's size, so token-heavy changes upstream are visible.

##### Definition of done

- [ ] The job runs on a schedule and on pull requests that touch `index.toml`.
- [ ] A broken member fails the job with a message that names the theme and the skill.

Part of #33.



<a id="issue-41"></a>

### #41: Show the token cost of skills in the picker and audit

Source: https://github.com/plugin-healthcare/tara/issues/41.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

##### Problem

Some skill sets are large and expensive in context tokens.
For example, superpowers `systematic-debugging` has 283 lines plus 10 support files, and `test-driven-development` has 330 lines.
Users cannot see this cost when they pick a theme, so they install more context than they need.

##### Required changes

- Estimate each skill's token footprint (for example, characters divided by 4) for the `SKILL.md` and for its total files.
- Show the estimate per theme in the `tara init` and `tara add` pickers and in `tara skill list`.
- Report it in `tara audit` next to the existing line-count warning.
- Point users in the picker hint to `tara skill add <skill>`, which already installs one member of a theme.

##### Definition of done

- [ ] The pickers and `tara skill list` show an approximate token cost.
- [ ] `tara audit` reports the estimate per skill.

Part of #33.



<a id="issue-42"></a>

### #42: Spike and ADR: move the catalog to a fetched registry outside src/

Source: https://github.com/plugin-healthcare/tara/issues/42.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: proposed replacement, not posted.

##### Question

Should Tara's catalog (templates, instructions, agents, prompts, internal skills, hooks, and MCP entries) move from `src/tara/data/` to a `registry/` folder in this repository that Tara fetches from GitHub, instead of shipping it inside the package?

##### Motivation

- The catalog can grow and get updates without a package release, and the package stays small.
- Tara's own content uses the same import route as third-party skills: reference it, pin it in the lock, and restore it on demand.
- A registry with its own CI can enforce size and token budgets on every skill.

##### Problems to solve

| Topic | Direction |
| ----- | --------- |
| Offline use | Keep the bundled baseline available; use cached remote content only at the requested pinned revision and report when it is unavailable. |
| Compatibility | Pin the registry to a tag or commit per Tara version or per repository, and check a format version in `registry.toml`. |
| Ownership checks | `_matches_catalog_source` (`src/tara/cli.py:1108`) compares against the bundled copy. Replace it with content hashes in the lock. |
| Supply chain | Hooks run code and MCP entries start processes, so fetch only pinned commits and never a branch head. |
| Access | Use `gh` or a token when available, and allow a registry URL override in `.tara/config.toml`. |
| Testing | Use a local registry fixture in tests, and validate the registry in its own CI job (#36). |

##### Timing

This spike is unscheduled and does not block 2.0.0 or 2.1.0.
Do not reserve registry schema fields in 2.0.0.
Approve an ADR and migration contract before assigning registry implementation to a release.
The bundled setup remains the baseline unless the spike demonstrates a concrete benefit.

##### Spike (timebox 2 days)

- [ ] Prototype fetching `registry/` at a pinned commit with a cache and an offline fallback.
- [ ] Replace the ownership comparison with lock content hashes for one artifact kind.
- [ ] Measure `tara init` with a cold and a warm cache.
- [ ] Write the ADR with the decision and the migration path for existing configs.

##### Open questions

1. Registry in this repository or a separate `tara-registry` repository?
2. Which content stays bundled as the offline core?
3. Is the registry size and token budget a hard limit or a warning?

Part of #33.

##### Proposed review follow-up (2026-10-12)

- [ ] Compare the prototype with the current bundled approach for offline first use, cold and warm setup, release frequency, and maintenance effort.
- [ ] Choose one authoritative lock representation and distinguish restore from an explicit update.
- [ ] Never substitute another cached revision or a moving source ref when the requested locked revision is unavailable.
- [ ] Define compatibility and ownership-hash migration before remote fetching.
- [ ] Keep hooks and MCP additions explicitly approved even when their sources are pinned.
- [ ] Record a go/no-go recommendation without making the basic setup depend on a registry service.



<a id="issue-43"></a>

### #43: Let contributors add stacks through the registry

Source: https://github.com/plugin-healthcare/tara/issues/43.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

###### Goal

Let anyone add a language stack, such as Rust or TypeScript, without code changes in Tara.
Python stays the only stack with full setup help from Tara's maintainers.

###### Stack contract

A stack is a folder `stacks/<name>/` in the registry.

- `stack.toml` (required): name, description, and owner.
- `<name>.instructions.md` (required): scoped instructions with their own `applyTo`.
- `checks.toml` (optional): commands for `tara check`.
- `pre-commit.yaml` (optional): hooks that `tara init` offers to add.
- `mcp.json` (optional): extra MCP servers.

Tara does not compare manifests, install toolchains, or read dependencies for contributed stacks.

###### Request for @dkapitan

- Do you want to own the Rust and TypeScript stacks?
- Have you found good human-written Rust or TypeScript skills? Users can add those directly from their repositories (#53).

@dkapitan let me know if this works for you.

Sub-issues: #44, #46, #47, #48. Language-neutral testing rules: #54.

Part of #33.



<a id="issue-44"></a>

### #44: Support a list of stacks in config and tara init

Source: https://github.com/plugin-healthcare/tara/issues/44.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: proposed replacement, not posted.

##### Problem

`.tara/config.toml` holds one `stack` string (`src/tara/config.py:123`), so a repository that mixes Python with Rust or TypeScript cannot select both.

##### Required changes

- Add `stacks: list[str]` and read a legacy `stack = "python"` as `stacks = ["python"]` without a warning.
- Preserve the current positional `tara init python` interface; define `--stack` as a compatible extension if it is added for comma-separated selection, and persist explicit names.
- Instructions, MCP servers, checks, and standards are merged across all configured stacks.

##### Definition of done

- [ ] Old configs with `stack` load and are written back as `stacks`.
- [ ] Two stacks produce merged checks and MCP servers without duplicates.
- [ ] Tests cover migration and merging.

##### Proposed review follow-up (2026-10-12)

- [ ] Define check ordering, command identity, duplicate handling, and conflict reporting with #46.
- [ ] Define precedence for developer-owned `.tara/checks.toml`, MCP settings, and pre-commit configuration.
- [ ] Do not discard different commands merely because both have the display name `test`.
- [ ] Cover the positional CLI form, any new option, and legacy `stack` migration in compatibility tests.

Do not widen contributed stacks into toolchain installation or manifest comparison.
This work remains unscheduled until the contract is approved.



<a id="issue-46"></a>

### #46: Install a contributed stack from its folder

Source: https://github.com/plugin-healthcare/tara/issues/46.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: proposed replacement, not posted.

###### Required changes

- `tara init` and `tara rebuild` install the files of every configured stack that follows the contract.
- Show the stack's owner in `tara init`.
- Keep the Python-only steps as they are.

###### Definition of done

- [ ] A sample stack folder with only `stack.toml` and an instructions file installs without code changes.
- [ ] Optional `checks.toml` and `pre-commit.yaml` are picked up when present.
- [ ] Python behaviour is unchanged.

Part of #43.

##### Proposed review follow-up (2026-10-12)

- [ ] Implement the approved merge and override contract from #44, including conflicting MCP names and pre-commit entries.
- [ ] Require explicit approval of contributed executable checks and preserve developer-owned configuration.
- [ ] Report missing toolchains clearly without installing them implicitly.
- [ ] Start with a minimal instructions-and-checks fixture that proves generic installation and checking.

Keep Python-only setup behavior unchanged.
The registry and stack contracts must be approved before assigning implementation to a release.



<a id="issue-47"></a>

### #47: Add the Rust stack

Source: https://github.com/plugin-healthcare/tara/issues/47.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

##### Scope update (2026-10-04)

This stack becomes a data-only folder in the registry that follows the stack contract in #43, maintained by its contributor.
Tara does not compare manifests or read dependencies for it, so the standards comparison and dependency triggers below are dropped.

---

##### Goal

Add Rust as a stack.
Prefer referencing existing human-curated skills over writing new ones, because agent-written skills only contain what the agent already knows.

##### Required changes

- A short scoped `rust.instructions.md` with `applyTo: "**/*.rs"`.
- `data/checks/rust.toml` with the tooling baseline agreed in the parent issue.
- `data/standards/rust/` with the pre-commit hooks and the config baseline.
- Index entries for good existing Rust skills, referenced and not copied.

##### Definition of done

- [ ] `tara init --stack rust` sets up instructions, checks, and standards.
- [ ] `tara check` runs the Rust gate in a sample project.
- [ ] The README lists the stack.



<a id="issue-48"></a>

### #48: Add the TypeScript stack

Source: https://github.com/plugin-healthcare/tara/issues/48.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

##### Scope update (2026-10-04)

This stack becomes a data-only folder in the registry that follows the stack contract in #43, maintained by its contributor.
Tara does not compare manifests or read dependencies for it, so the standards comparison and dependency triggers below are dropped.

---

##### Goal

Add TypeScript as a stack.
Prefer referencing existing human-curated skills over writing new ones, because agent-written skills only contain what the agent already knows.

##### Required changes

- A short scoped `typescript.instructions.md` with `applyTo: "**/*.ts,**/*.tsx"`.
- `data/checks/typescript.toml` with the tooling baseline agreed in the parent issue.
- `data/standards/typescript/` with the pre-commit hooks and the config baseline.
- Index entries for good existing TypeScript skills, referenced and not copied.

##### Definition of done

- [ ] `tara init --stack typescript` sets up instructions, checks, and standards.
- [ ] `tara check` runs the TypeScript gate in a sample project.
- [ ] The README lists the stack.



<a id="issue-53"></a>

### #53: Browse and add skills from one index of Tara and external sources

Source: https://github.com/plugin-healthcare/tara/issues/53.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: proposed replacement, not posted.

###### Problem

Tara's own skills and external skills are handled in different ways.
Bundled skills come from the catalog, external collections need a curated theme in `index.toml`, and anything else needs a git URL plus the exact `--path` of one skill.
`tara skill list` only shows external skills that are already installed, so users cannot see what is available.

###### Proposal

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

###### Required changes

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

###### Definition of done

- [ ] `tara skill list mattpocock` shows the skills grouped by `engineering`, `productivity`, and `misc`.
- [ ] `tara skill add superpowers/test-driven-development` installs one skill and pins it in the lock.
- [ ] `tara skill add obra/superpowers` works without an index entry.
- [ ] External skills are labelled as external with their repository and license in the list, the picker, and the add output.
- [ ] A note on a skill is shown in the list, the picker, and before install, and the skill can still be installed.
- [ ] Existing theme names from 1.x still install the same skills.
- [ ] The index format matches the registry decision in #42.

Part of #33.

##### Proposed review follow-up (2026-10-12)

- [ ] Define precedence when `<source>/<skill>` and `owner/repo` have the same textual shape.
- [ ] Reject ambiguous input with an actionable disambiguation route instead of guessing.
- [ ] Preserve existing non-interactive theme commands and their explicit membership until an approved migration changes them.
- [ ] Cover interactive source browsing separately from legacy theme installation.
- [ ] Reuse URL and `--path` disambiguation before adding more command surface.

Conflict notes and pinned source information are disclosure, not a security guarantee.
Keep this work unscheduled pending the registry and CLI contract decisions.



<a id="issue-59"></a>

### #59: Split cli.py and group modules into packages

Source: https://github.com/plugin-healthcare/tara/issues/59.
Milestone captured on 2026-10-12: 2.x.
Proposed milestone: none.
Body status: current published body, retained for editing.

###### Problem

`src/tara/` has 18 modules in one folder.
`cli.py` has 1,328 lines and holds every command group, so changes to unrelated commands touch the same file.

###### Required changes

- Turn `cli.py` into a `cli/` package with one module per command group, and keep the `tara` entry point unchanged.
- Group the generators for other agent tools, `claude`, `opencode`, `hooks`, and `generate`, into an `integrations/` package.
- Move code only, with no behaviour changes, in a separate pull request from any feature work.

###### Definition of done

- [ ] `tara --help` and `docs/cli.md` are unchanged.
- [ ] No module in `src/tara/` is longer than about 500 lines.
- [ ] `tara check` passes.



<a id="issue-64"></a>

### #64: Spike optional Pi integration and its protection boundary

Source: https://github.com/plugin-healthcare/tara/issues/64.
Milestone captured on 2026-10-12: none.
Proposed milestone: none.
Body status: current published body, retained for editing.

##### Question

Can Tara support Pi through a small optional configuration adapter while stating its protection limits accurately?
This is a spike, not approval to implement the adapter or a security package.
It has no release milestone until an owner and release are agreed.

##### Inputs

The original assumptions A1 to A7 are in `.agents/plan/202610121400_pi-integration.md`.
They came from a mirror and package listings and still need verification against versioned upstream sources.
The independent plans review identifies instruction-loading and policy-activation gaps.

##### Spike

Timebox: one day.

1. Confirm or correct A1 to A7 using upstream Pi documentation and examples at a recorded version.
2. Verify actual instruction loading, including root and subfolder execution, pointers to other files, and an existing developer-owned `AGENTS.md`.
3. Verify skills and prompt discovery without assuming Claude import behavior.
4. Record supported Pi versions and platforms, candidate policy-package versions, maintenance, licenses, and activation requirements.
5. Test the proposed protection layer only in an isolated disposable fixture with developer-approved experiments.
6. Cover permitted operations, denied operations, missing packages, disabled policy, incompatible versions, and documentation-only setup.
7. Write an ADR that states whether to build an adapter, document manual setup, or stop.

##### Boundaries

- Do not describe generated files as a safe default or as proof of runtime isolation.
- Do not install Pi or policy packages for consuming repositories.
- Do not build a Tara-owned sandbox or permission engine.
- Preserve developer-owned files and keep Pi explicitly opt-in.
- Prefer deterministic local diagnostics through `tara audit`; do not add implicit network checks to every project's build gate.
- The spike can proceed without #19, but implementation must agree on a temporary projection contract or the canonical-format decision.
- Implementation requires #18 and #20; declare #39 as a fixture dependency or provide a self-contained equivalent.

##### Definition of done

- [ ] A1 to A7 have versioned sources and observed results.
- [ ] Actual instruction delivery is demonstrated, not only generated-file existence.
- [ ] The ADR defines supported versions, activation checks, failure behavior, and protection limits.
- [ ] The developer approves the ADR before any implementation issue is scheduled.

Part of roadmap #33.
