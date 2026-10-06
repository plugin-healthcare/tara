# Agent working docs

`tara init` creates `.agents/`, a folder where coding agents keep the documents they produce while they work.
It is committed by default, so the next session, another agent, or a colleague can pick up where the last one stopped.
The instructions Tara installs tell agents when to write to each folder.

## Folders and the flow of a change

Every change follows the workflow in the base instructions, and each folder belongs to a step in it.

| Folder | When it is written | What it holds |
| ------ | ------------------ | ------------- |
| `design/` | Before the plan, when there are options to weigh. | The options, the trade-offs, and the choice. |
| `plan/` | When the change is planned. | The files, edge cases, and steps for one change. |
| `review/` | After the checks pass. | Findings from a code or maturity review. |
| `memory/` | At the end of every phase and at every hand-off. | What was done, what is left, and the open decisions. |
| `runbooks/` | When a procedure is repeated, such as a release. | Steps, rollback, and verification that an agent executes with the `/runbook` prompt. |

A design and a plan are written once for one change and are done when the change lands.
A runbook is reused and stays current, and an agent proposes an edit to it when a step turns out to be wrong.

## Naming and indexes

Each folder has an `index.md` with one row per doc, newest first, so an agent can scan it instead of opening every file.
Docs are named `YYYYMMDDHHMM_<short-descriptive-title>.md`, so they sort by time and rarely collide across parallel sessions.
Runbooks keep a stable `<slug>.md` name instead, because other docs and issues link to them.
Scaffold a runbook with `tara new runbook "<title>"`.

## Working docs and official records

A working doc supports the agent while it works, and an official record is what other people rely on afterwards.
Each stage of the DevOps cycle has one of each.

| Stage | Official record | Working doc |
| ----- | --------------- | ----------- |
| Plan the backlog | Epics, stories, bugs, and spikes on the board | Drafts in `plan/`, reviewed before they are posted |
| Design | An ADR in `docs/decisions/` | Options and trade-offs in `design/` |
| Build and test | Code, tests, and the pull request | The plan for one change in `plan/` |
| Review | The pull request review | Findings in `review/` |
| Release | The changelog, the tag, and the GitHub release | The release procedure in `runbooks/` |
| Operate | Issues for the follow-up actions | Operational procedures in `runbooks/` and post-mortems in `review/` |
| Hand off | Issues for work that is left | Session notes in `memory/` |

A post-mortem is a short write-up after an incident, such as an outage or a broken release, with the timeline, the cause, and what to change.

## What does not belong here

Finalized architecture decisions belong in `docs/decisions/`, and stories and epics belong in the issue tracker.
Never put secrets or credentials in `.agents/`, because the folder is committed and shared.
To keep a subfolder local, such as `memory`, list it under `[agents] gitignore` in `.tara/config.toml`.
