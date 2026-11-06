# Independent review of Tara and its plans

Reviewed on 2026-10-12 by Astra against `e567fe9` on `feat/claude-code-support`, including the uncommitted Pi draft.
This review follows `.agents/memory/202610121410_independent-plans-review-handover.md`.
It changes no implementation, plan, issue, or repository setting.

## Verdict

Tara has the right architectural boundary for a lightweight harness.
Keep it as a setup and verification CLI that installs readable project rules, preserves developer-owned files, restores explicitly selected content, and connects the project's checks to CI.
Keep model execution, runtime permissions, and isolation with the coding agent and its execution environment.

The current branch is not ready to support a stable safety claim.
Some essential protections are still planned rather than implemented, a malformed check configuration can produce a successful empty gate, and the release instructions do not yet bind publication to the exact tested commit and artifacts.
The largest planning problem is competing sources of truth, rather than a shortage of plans.
Adding integrations, a remote registry, or a queryable store before resolving these contracts would increase the number of states Tara must manage.

The intended flow can remain small.

```text
Approved issue -> short plan -> implementation -> project gate
                                                    |
                                                    v
Shared hand-off <- release and verification <- independent review

Tara supplies setup, files, checks, and integration adapters.
The agent runtime supplies tool permissions and execution isolation.
GitHub supplies merge and publication controls.
```

## Evidence and scope

All seven plans, both design documents, and the release runbook in the handover were read.
The review also traced the CLI, configuration loading, generated-file writers, skill restoration, check runner, installed instructions, CI workflow, and bundled CI template.
Live GitHub records were checked on 2026-10-12, including both milestones and the relevant issue bodies.

PR #17 is open and mergeable at the reviewed commit.
Its two reported CI jobs succeeded on 2026-10-07.
The branch-protection endpoint reports that `main` is not protected, and the effective branch-rules endpoint returns no rules.
Those observations do not establish package-release readiness.

`tara` was not on this shell's PATH, but `uv run --no-sync tara --help` worked.
A read-only in-process reproduction confirmed that empty and misspelled check configurations produce exit code 0.
No full gate, release, Pi installation, or destructive-operation experiment was run for this document review.
The Pi package claims remain spike inputs, not verified findings about those packages.

## Findings

### 1. The setup safety promise is ahead of the implementation

**Severity:** blocker for 2.0.0.
**Lens:** ease of use.
**Where:** `README.md:148-155`, `src/tara/core.py:152-174`, `src/tara/cli.py:263-281`, and `src/tara/generate.py:145-173`.

The README promises that Tara never silently overwrites an existing setup.
However, `init` still calls the unconditional core writer for instructions and MCP configuration, and rerunning it without an integration argument selects Copilot rather than preserving the saved selection.
The generated Markdown writer also treats a retained marker as ownership without detecting subsequent developer edits.
These are existing release blockers covered by #18, #24, and #30, not newly discovered issues.

**Suggested fix:** keep these repairs ahead of new integrations and make their acceptance cases part of the release gate.
Verify a fresh setup, an unchanged rerun, an edited generated file, and a hand-written collision through the actual CLI.
Until those cases pass, qualify the README's guarantee rather than presenting the planned behavior as delivered.

### 2. The check gate can succeed without running a check

**Severity:** blocker for 2.0.0.
**Lens:** pipeline.
**Where:** `src/tara/check.py:46-48`, `src/tara/check.py:99-111`, and `src/tara/cli.py:747-770`.

The parser defaults a missing `check` key to an empty list.
An empty file or a valid TOML file using `[[checks]]` instead of `[[check]]` therefore bypasses every check.
The CLI prints an empty summary and exits 0 because there are no failed results.
Both cases were reproduced through the parser and CLI with the loader isolated.
The #60 plan covers malformed files and clean errors, but does not explicitly cover syntactically valid configurations that define no usable gate.

**Suggested fix:** extend the check-configuration boundary and #60 acceptance cases to reject missing, empty, and misspelled check definitions with an actionable error.
Validate nonempty command strings and the intended schema before execution.
If disabling a gate is ever supported, make it explicit and visibly different from a passed gate.

### 3. Publication is not bound to one verified commit and artifact set

**Severity:** blocker for 2.0.0.
**Lens:** pipeline.
**Where:** `.agents/runbooks/release-a-new-version.md:30-48` and `.agents/plan/202610041800_release-2.0.0-execution-runbook.md:179-194`.

The reusable runbook builds locally before the release PR merges, then tags the merge commit and uploads the earlier local artifacts.
Changes made during review or merging can therefore make the tag and package disagree.
The execution plan instead proposes a tag-triggered publisher that “reuses the built artifacts”, without specifying which workflow run, commit, or artifact identity qualifies.
Neither route alone establishes #22's requirement that both destinations receive the exact CI-tested artifacts.
Required checks on `main` also do not by themselves prevent publication from an unrelated tag.

**Suggested fix:** define one release route in #22 and update the runbook in the same change.
Build once per release version from the exact protected release commit, smoke-test those artifacts, and publish those same bytes only after all required jobs succeed.
Bind artifact selection and attestations to that commit, restrict the publishing environment and eligible tag source, and require developer approval.
Do not leave the manual local-upload route as an alternative after trusted publishing is enabled.

### 4. The release procedure contains contradictory prerequisites and RC checks

**Severity:** blocker for 2.0.0.
**Lens:** plan quality.
**Where:** `.agents/runbooks/release-a-new-version.md:12`, `.agents/runbooks/release-a-new-version.md:22-32`, `.agents/runbooks/release-a-new-version.md:46-64`, `.agents/plan/202610041800_release-2.0.0-execution-runbook.md:210-224`, and `.agents/plan/202610021025_stable-release-roadmap.md:96`.

The reusable procedure requires every milestone issue to be closed before starting, while the execution plan explicitly leaves #33 open until publication.
It also asks for unpinned installation verification, which does not reliably select a release candidate when a stable release exists.
The roadmap says to promote the same RC artifacts to stable, although distribution version metadata must change.
The reusable procedure more accurately says to rebuild and verify the same code under the final version.
Finally, opening and merging the release PR is not marked as a developer step, despite the procedure's shared-infrastructure rule.

**Suggested fix:** allow the release-tracking issue to remain open until successful verification, and require all actual blockers to be resolved.
Use one explicit distribution version throughout filenames, metadata, tags, and post-publication installation, including an exact version pin for RC verification.
Describe stable promotion as a final-version build from the accepted source, with the full artifact checks repeated.
Mark PR creation and merge as developer-controlled steps.

### 5. The active roadmap and posted copies disagree with the board

**Severity:** blocker for 2.0.0.
**Lens:** plan quality.
**Where:** `.agents/plan/202610021025_stable-release-roadmap.md:64-90`, `.agents/plan/202610021040_stable-release-issue-drafts.md:4-6`, `.agents/plan/202610021040_stable-release-issue-drafts.md:192-213`, and `.agents/design/202610021040_remote-catalog-registry.md:44-48`.

The roadmap still lists #25, #36, #39, #40, and registry schema work as release requirements, while the current #33 and milestones defer them to 2.x.
It also lists #34 and #35 as blockers although both are closed.
The registry issue itself is in 2.x but still contains text requiring an ADR and schema changes before 2.0.0.
The execution plan mostly follows the reduced scope, so an agent receives different release instructions depending on which linked document it opens.
The drafts document explicitly invites editing its old issue bodies and syncing them back, risking reversal of later decisions.

**Suggested fix:** use approved issues and milestones as the authoritative scope.
Reduce the roadmap to the current release boundary, dependency order, and links.
Mark posted draft bodies as historical snapshots, and keep any new proposed issue amendments in a clearly separate pending section.
Resolve the registry timing contradiction explicitly instead of reserving speculative schema fields in 2.0.0.
Register the execution plan's untracked review-hardening step against an approved issue or an explicit acceptance item in #33.

### 6. The meaning of integration shorthand is still an unresolved release contract

**Severity:** blocker for 2.0.0.
**Lens:** ease of use.
**Where:** `src/tara/core.py:39-70`, `src/tara/config.py:156-163`, `.agents/plan/202610021040_stable-release-issue-drafts.md:868`, and `.agents/plan/202610121400_pi-integration.md:19`.

Current CLI normalization expands `all` to Copilot, OpenCode, and Claude.
Legacy scalar `tool = "all"` instead migrates to Copilot and OpenCode.
The plans acknowledge the compatibility decision but do not put its resolution into the version-freeze checklist.
Pi would introduce another distinction by being supported but excluded from `all`.
Persisting explicit names prevents future expansion of saved configurations, but does not settle what rerunning a legacy command should do.

**Suggested fix:** approve and document a compatibility table before step 14 of the execution plan.
Cover canonical flags, deprecated aliases, legacy scalar configuration, explicit lists, and opt-in integrations.
Either preserve the old CLI expansion where required or document the chosen 2.0.0 behavior change with a migration example.
Describe `all` as all standard integrations if Pi remains excluded, and name the exclusions in help and selection output.
Keep the canonical public terminology `integrations`; do not add another selection command.

### 7. Generated CI does not use the project's configured gate

**Severity:** should fix.
**Lens:** pipeline.
**Where:** `src/tara/data/templates/ci-github.yml:41-54`, `.github/workflows/ci.yml:31-35`, and `src/tara/cli.py:283-305`.

Tara's own CI invokes `tara check`, but the CI template handed to users duplicates the Python commands.
A project-specific `.tara/checks.toml` therefore affects local checks without affecting generated CI.
The execution plan fixes the generated agent starter commands but omits this equivalent template problem.
Also, `init` sets up tooling and optional artifacts without connecting the user to the separate `tara new ci` step, so a new user can finish setup without a remote gate.

**Suggested fix:** make the generated CI call the same project gate as local development, with Tara available through the documented dependency setup.
Add a template-level regression case showing that a custom gate is honored.
Offer CI setup or report its absence at the end of `init`, preserving any existing workflow.
Keep secret scanning and workflow linting explicit where they are additional to `tara check`.

### 8. Package smoke tests do not cover the behavior being released

**Severity:** should fix.
**Lens:** pipeline.
**Where:** `.agents/plan/202610041800_release-2.0.0-execution-runbook.md:181-184`, `.agents/runbooks/release-a-new-version.md:34-42`, and `.agents/plan/202610021040_stable-release-issue-drafts.md:871`.

The execution plan reduces the package smoke job to `tara --version`, despite an existing amendment also naming `tara init --dry-run` and `python -m tara.markdown_lint`.
The full installed-wheel lifecycle suite is deferred with #39, and the reusable runbook leaves its most important scenarios manual.
An importable CLI can still ship without usable package data or with broken setup and removal behavior.
The scratch-repository idempotency instruction also lacks a baseline snapshot, so ordinary untracked-file output is not a sufficient before-and-after comparison.

**Suggested fix:** keep #39's broad matrix in 2.x, but include a small installed-artifact smoke fixture in #22.
Exercise bundled-data access, one setup and rerun, a developer-owned collision, one integration add/remove cycle, and the public Markdown entry point.
Use isolated local fixtures and compare file contents before and after, rather than relying on the appearance of `git status`.
Specify the remaining manual acceptance checks and who records their result.

### 9. Independent review and runtime safety remain advisory in important places

**Severity:** should fix.
**Lens:** pipeline.
**Where:** `src/tara/data/instructions/base.md:29-38`, `src/tara/data/catalog/prompts/review.prompt.md:1-13`, and `.agents/plan/202610041800_release-2.0.0-execution-runbook.md:55-85`.

The planned clean-agent review stops are appropriate, but the currently shipped workflow does not require that step.
Adding the rule to a prompt will not by itself prove independent execution or prevent merging without review.
Similarly, removing the default Git MCP server reduces granted capability, but does not prevent an agent with shell access from invoking Git.
Neither change should be described as a complete runtime security boundary.

**Suggested fix:** ship the planned review instructions and require a PR review through #37.
Record the reviewed commit, reviewer, unresolved findings, and developer acceptance in the review hand-off.
Invalidate approval when the reviewed change changes.
Document which protections Tara checks mechanically, which depend on platform permissions, and which remain instructions.
Do not add a Tara-owned agent runtime merely to enforce this distinction.

### 10. The Pi plan promises safety before its permission layer is active

**Severity:** should fix.
**Lens:** ease of use.
**Where:** `.agents/plan/202610121400_pi-integration.md:11-18`, `.agents/plan/202610121400_pi-integration.md:43-49`, and `.agents/plan/202610121400_pi-integration.md:87-95`.

The goal calls Pi safe by default, but Tara never installs the required permission package and only warns if it is absent.
The fallback is documentation without configuration, which provides a different outcome again.
A generated policy file and a version string do not establish that a compatible policy engine loaded the file or that the execution environment confines the agent.
The test that requires `rm -rf` to ask also needs a defined relationship with the earlier fixture that expects an outside-repository attempt to be refused.

**Suggested fix:** describe the feature as optional Pi setup with an explicitly reported protection state.
Separate states for documentation-only setup, missing or incompatible policy support, and a verified supported baseline.
Put deterministic local configuration diagnostics in `tara audit`, rather than silently adding network-dependent package checks to every project's build gate.
Define when an expected protection failure is an error and when an advisory notice is sufficient.
Use wording such as “Pi runs with your account's access unless you configure isolation” until the spike establishes a narrower guarantee.

### 11. The Pi spike does not yet prove instruction delivery or define its dependency contract

**Severity:** should fix.
**Lens:** plan quality.
**Where:** `.agents/plan/202610121400_pi-integration.md:23-49`, `.agents/plan/202610121400_pi-integration.md:61-66`, and `.agents/plan/202610121400_pi-integration.md:98-121`.

A1 only concerns finding `AGENTS.md`; it does not establish that Pi follows a pointer to another instruction file.
The proposed Claude-style pointer therefore needs its own loading test.
Preserving an existing developer-owned `AGENTS.md` is correct, but the plan does not state how Tara's rules reach Pi when that file is retained.
The spike also lacks an explicit Pi version, supported platforms, policy-package activation test, and success criteria for the documentation-only fallback.
Step 5 depends on #39, but the header only declares #18 and #20.
The historical Claude plan demonstrates why file existence is insufficient evidence of instruction loading.

**Suggested fix:** post this as a bounded 2.x spike before approving the implementation.
Record upstream versioned sources for A1 to A7 and verify actual rule loading from the root and a subfolder, including the existing-file case.
Record supported Pi and policy-package versions, activation checks, platform limits, permitted operations, and denied operations in the ADR.
Test missing, disabled, and incompatible policy support as well as the successful setup.
Declare #39 as a prerequisite or provide a self-contained fixture instead.
The spike need not wait for #19, but implementation must explicitly choose a temporary projection contract or wait for the canonical-format decision.

### 12. Required hand-off information is available only on one machine

**Severity:** should fix.
**Lens:** storage.
**Where:** `.tara/config.toml:5-6`, `.gitignore:24-25`, `.agents/plan/202610041800_release-2.0.0-execution-runbook.md:20-27`, and `docs/agent-working-docs.md:3-4`.

This repository intentionally ignores `.agents/memory/`, while the process depends on it for phase results, decisions, and resumption.
The review handover itself is an example that a fresh clone or remote agent will not receive.
This configuration is supported by Tara, so the bug is not the presence of a gitignore option.
The gap is requiring local notes without requiring a shared equivalent of the information needed to continue.

**Suggested fix:** keep raw session scratch local if that remains useful, but put the minimal non-sensitive continuation state in the tracked active plan, review, or official issue.
Record the last completed step and commit, the next action, remaining blockers, and the developer decision required.
Alternatively, explicitly choose tracked memory and review its contents before changing the ignore rule.
Do not bulk-add existing ignored notes.
For #14 and #29, settle this information contract before choosing a storage engine.

### 13. Historical documents and indexes still contain executable stale guidance

**Severity:** should fix.
**Lens:** storage.
**Where:** `.agents/plan/202609072015_claude-import-port-and-catalog-followups.md:31-42`, `.agents/plan/202607020900_maturity-execution-plan.md:1-35`, `.agents/plan/202610021040_stable-release-issue-drafts.md:447-513`, `.agents/plan/index.md:9-13`, and `.agents/design/index.md:7-8`.

The rebuild plan states completion in its body, but its index still reads as an open task.
The completed Claude work retains imperative instructions to import agent bodies even though its recorded experiment rejected that approach.
The maturity plan still points to Wingman paths and an old review location without a top-level supersession statement.
The issue-draft file calls posted work “not yet posted”, and the design index still advertises ecosystem dependency triggers that the revised stack decision excludes.
The indexes enumerate the scoped tracked documents in order, but are not reliable status summaries.

**Suggested fix:** add an explicit status, superseding record, and next action at the top of each active or historical document.
Mark historical steps as non-executable, and link remaining work to current issues.
Update index summaries when status changes.
Keep useful decisions and experiment results, but replace posted issue-body copies with links and a short decision record after approval.
Do not delete history automatically.
The one-off release execution plan can remain in `plan/`; clarify its status and avoid presenting it as a second reusable release procedure.

### 14. Registry complexity is not yet justified by an agreed operating contract

**Severity:** suggestion.
**Lens:** plan quality.
**Where:** `.agents/design/202610021040_remote-catalog-registry.md:17-23`, `.agents/design/202610021040_remote-catalog-registry.md:35-54`, and `src/tara/skills.py:411-425`.

The registry design correctly acknowledges that its benefit is independent content releases rather than the size of the current catalog.
However, it proposes another cache, compatibility version, configurable source, lock decision, and fallback behavior before specifying a success threshold over the bundled approach.
“Fall back to the cache” is also incomplete when the requested pinned revision is absent or the cache holds another revision.
Current skill restoration already falls back to a source ref when a lock entry is absent, so reusing that behavior would not establish strict reproducibility.

**Suggested fix:** keep the registry optional and in 2.x.
Compare the existing bundled route against the prototype for offline first use, setup time, update frequency, and maintenance cost.
Choose one authoritative lock representation and require exact-revision cache matching for restoration.
Report an unavailable requested revision without substituting a different one.
Keep executable hooks and MCP additions explicitly approved even when their source is pinned.
Do not require a registry service or new metadata for the basic offline setup unless the spike demonstrates a concrete benefit.

### 15. Contributed stacks need merge rules before they are implementable

**Severity:** should fix.
**Lens:** plan quality.
**Where:** `.agents/design/202610021055_rust-typescript-stacks.md:36-57`, `.agents/plan/202610021040_stable-release-issue-drafts.md:359-369`, and `.agents/plan/202610021040_stable-release-issue-drafts.md:477-498`.

Keeping Python as the fully supported setup and other stacks contributor-owned is a useful scope boundary.
The contract nevertheless leaves “merged checks and MCP servers without duplicates” undefined.
Two stacks can define a `test` check with different commands, an MCP server with the same name, or incompatible pre-commit entries.
The relationship with a developer's existing `.tara/checks.toml` is unspecified.
The plan and #44 also use `tara init --stack`, although the current CLI takes a positional stack argument.

**Suggested fix:** define deterministic ordering, identity, conflict reporting, and developer-owned override precedence in #44 and #46 before implementing adapters.
Do not silently deduplicate different commands because their display names match.
State how contributed executable checks are approved and how missing toolchains are reported.
Preserve `tara init python`; if `--stack` is added, specify it as a compatible extension with examples and tests.
Start with the smallest stack fixture that proves installation and checking without adding toolchain management.

### 16. The unified skill interface still has an ambiguous compatibility boundary

**Severity:** should fix.
**Lens:** ease of use.
**Where:** `.agents/plan/202610021040_stable-release-issue-drafts.md:627-654`.

Draft E and #53 accept both `<source>/<skill>` and `owner/repo`, which have the same textual shape.
They also change `tara skill add <source>` into a picker while promising that existing theme names retain their behavior.
The plan does not define precedence when a registered source name overlaps an owner, or what happens to existing non-interactive theme-install commands.
Those are observable CLI contracts, not implementation details an agent should infer.

**Suggested fix:** define resolution precedence, ambiguity errors, and non-interactive behavior in #53.
Keep existing theme commands installing their existing explicit membership until an approved migration changes that contract.
Use the current URL and `--path` route to disambiguate external repositories where possible.
Add compatibility cases before introducing another flag or command.
Labeling external content and showing its pinned source are good requirements, but do not claim that conflict notes establish its trustworthiness.

## Coverage of the requested documents

| Document | Assessment |
| --- | --- |
| Pi integration plan | Keep as a 2.x spike; do not approve the current safety claim or assume pointer loading. |
| 2.0.0 execution plan | Closest to current scope; retain its issue-by-issue order and review stops, then repair the missing contracts above. |
| Stable-release issue drafts | Historical posted copies and current proposals are mixed; stop treating the whole file as editable board state. |
| Stable-release roadmap | Out of sync with the approved reduced scope and current PR state. |
| Rebuild plan | Completion is recorded; surface it in the index and distinguish delivered work from later defects. |
| Claude import and catalog follow-ups | Preserve the empirical hybrid result; retire the contradicted steps and link outstanding follow-ups. |
| Maturity execution plan | Retain the enforcement-versus-advice principle; mark old paths and superseded implementation directions as historical. |
| Remote registry design | A reasonable experiment for independent content releases, subject to explicit offline and lock behavior. |
| Contributed-stack design | A suitable lightweight boundary, but merging, CLI compatibility, and executable-content approval need definitions. |
| Reusable release runbook | Has useful rollback and scratch-repository checks; fix publication provenance, developer stops, and RC semantics before use. |

## Summary by lens

**Ease of use:** the basic CLI is understandable, and keeping compatibility aliases is appropriate.
Finish safe reruns, publish the correct `tara-dev` installation route, explain what setup has and has not enabled, and settle shorthand behavior.
Do not make a registry, storage backend, or permission-package choice a prerequisite for ordinary Python setup.

**Pipeline:** backlog, design, implementation, review, release, operation, and hand-off all have a place.
The missing links are a gate that cannot silently do nothing, shared local/CI execution, independently recorded review, and publication of the exact verified artifacts.
Retain rollback through yanking and a corrected release, without moving published tags.

**Storage:** plain Markdown under `.agents/` is sufficient for the current workflow.
Accurate status and shared continuation information will provide more immediate value than replacing the storage layer.
Keep the tracker authoritative after posting, finalized decisions in ADRs, reusable procedures in runbooks, and local scratch out of mandatory remote-agent dependencies.

**Plan quality:** the reduced 2.0.0 direction is sound, but stale copies obscure it.
Keep Pi, the registry, contributed stacks, and optional oxivault integration in 2.x.
Resolve behavior contracts before expanding schemas or adding adapters, and turn completed plans into clearly non-executable history.

## The three changes to make first

1. Make Tara's existing guarantees true.
   Complete the ownership and lifecycle blockers, reject empty check configurations, and cover the resulting behavior through the CLI.
2. Establish one verified release path.
   Tie the protected commit, independent approval, built artifacts, package smoke checks, trusted publication, and exact-version verification together.
3. Reconcile the working records before starting another feature.
   Update the roadmap from approved scope, retire posted duplicates, expose shared hand-off state, and approve only the bounded Pi spike.
