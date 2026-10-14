# Release milestones and roadmap

Date: 2026-10-12.
Status: release milestone assignments applied on 2026-10-13; issue-body edits remain paused.
Source: `.agents/review/202610122253_independent-plans-review.md`.

The complete issue bodies and latest PR review triage are in `202610122358_release-issue-drafts.md`.
Milestone `2.1.0` and issues #63, #64, and #65 have been created.
The 2.1.0 work is assigned and the remaining open `2.x` work is unscheduled.
The empty `2.x` milestone is closed without deleting its history.
Existing issue bodies are unchanged, and #33 remains in 2.0.0 until its roadmap rewrite is approved.
Do not post the remaining issue-body changes until the developer has finished revising the full draft.

## Proposed structure

Reuse #33 as the cross-release roadmap rather than creating a competing tracker.
Remove its release milestone and keep it open across releases.
Use each numbered milestone as the authoritative issue list for that release.
Keep the roadmap short, with the goal, milestone link, dependencies, and release acceptance criteria.
Treat release candidates as stages of their stable release, not separate work milestones.
Do not add dates or change owners without agreement.

## Release assignments

| Release | Goal | Assigned work |
| --- | --- | --- |
| 2.0.0 | Establish safe setup and a verified first stable release. | Keep #18, #20, #21, #22, #24, #26, #30, #37, #38, #49, #50, #56, #60, and #61; add the independent-review work already required by the execution plan. |
| 2.1.0 | Improve repeatable setup and the daily workflow. | Assign #25, #39, #40, #51, #52, #54, and #55, plus a small issue to make generated CI use the project gate. |
| Unscheduled | Resolve designs before promising a release. | Leave other current 2.x work without a milestone, including registry, canonical formats, contributed stacks, storage backends, and new agent integrations. |

Create `2.1.0` rather than renaming the broad `2.x` milestone into a release commitment.
After moving its open issues, close `2.x` as a historical planning bucket without deleting it or changing closed issue history.
Do not close #49 merely because the current branch is green; its work still needs to land.

## Amend existing issues

| Issues | Required clarification |
| --- | --- |
| #18, #21 | Decide `all` and legacy alias behavior before the version freeze, with compatibility cases and migration guidance. |
| #22 | Bind the release to one verified commit and artifact set; update the runbook, exact-version RC checks, and installed-artifact smoke cases. |
| #37 | Require independent PR review, current approval, and the exact named checks; distinguish merge protection from publication eligibility. |
| #38, #50 | State the boundary between instructions, reduced tool access, runtime permissions, and isolation. |
| #60 | Reject empty, missing, misspelled, and otherwise unusable check definitions instead of passing an empty gate. |
| #39 | Keep the full fixture matrix separate from the small release smoke cases in #22. |
| #42 | Remove the pre-2.0.0 schema requirement; compare the bundled approach with an optional registry and define exact-revision offline behavior. |
| #44, #46 | Define stack merge precedence, collisions, existing overrides, and compatibility with the positional stack argument. |
| #53 | Define source-versus-repository resolution and preserve existing non-interactive theme behavior. |
| #55 | Define draft batch selection and document status transitions; keep posted issues authoritative and require shared continuation state. |
| #14, #29 | Define what information must be shared before selecting a storage backend; keep raw local scratch optional. |

Preserve existing issue requirements, assignees, and discussion.
Do not reopen closed issues or turn unresolved design choices into settled decisions.

## New issue drafts

### #63 Require independent review in the bundled workflow

Milestone: 2.0.0.
This tracks step 3 of the existing execution plan.
Add the clean-agent review step to the bundled workflow and Definition of Done.
Require the reviewed commit, findings, and developer acceptance in the review record.
Cover project invariants and permission-relevant parsing in the review instructions.
Ship the already-approved instruction lessons without adding a Tara-owned agent runtime.
The new writing-style guidance is already staged and does not need another issue.

### #65 Use the project gate in generated CI

Milestone: 2.1.0.
Make the bundled CI template run the same configured gate as local development.
Keep additional secret and workflow checks explicit.
Preserve existing workflows and explain the CI setup step after initialization.
Verify that a custom `.tara/checks.toml` is honored by the generated workflow.

### #64 Spike optional Pi integration and its protection boundary

Milestone: none until the spike has an owner and an agreed release.
Verify A1 to A7 against versioned upstream sources and actual instruction loading.
Cover existing `AGENTS.md`, subfolder execution, supported Pi versions and platforms, and missing or incompatible policy support.
Record whether the result supports a configuration adapter or documentation only.
Do not claim a safe default, install packages for the user, or implement an adapter before the ADR is approved.
The spike does not wait for #19, but implementation must agree on a temporary or canonical instruction contract.

## Local record updates

Replace the old roadmap's competing issue inventory with links to #33 and the numbered milestones.
Mark posted issue drafts as historical and keep future amendments separate.
Update the release execution plan and reusable runbook to follow the approved issue contracts.
Publish only the proposed GitHub changes after approval, then verify their bodies and milestone membership.
Keep Git commits and pushes with the developer.
