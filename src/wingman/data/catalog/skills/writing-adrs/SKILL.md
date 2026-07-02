---
name: writing-adrs
description: "Use when making or recording an architectural or design decision, when running research or a spike to unblock one, or when asked to write an ADR (architecture decision record). Also use when a decision needs a C4 or LikeC4 diagram to explain structure."
---

# Writing ADRs

An architecture decision record captures a significant, hard-to-reverse decision:
the context, the options, the choice, and its consequences. Record decisions that
shape the system, not routine implementation details. The format follows MADR
(Markdown Any Decision Records, adr.github.io).

## Write an ADR

Scaffold it: `wingman new adr "<title>"` (writes a numbered file under
`docs/decisions/`, e.g. `0007-use-postgres-over-mongodb.md`). Then fill:

- **Metadata**: status, date, and authors.
- **Context and Problem Statement**: the situation and the problem in two or three
  sentences, ideally as a question. Link the issue or spike that raised it.
- **Considered Options**: the realistic candidates, not just the winner.
- **Decision Outcome**: the chosen option stated plainly, and *why* it won (the
  criterion or force it satisfies).
- **Consequences**: the good and the bad. Be honest about the costs.

Optional house additions, used only when they add clarity:

- **Architecture**: a diagram (ASCII, Mermaid, or LikeC4) or a comparison table
  weighing the options against the concerns that matter.
- **Rollout**: the phases if the decision lands in steps.

## Status lifecycle

`Proposed -> Accepted -> Deprecated | Superseded by ADR-<n>`. An accepted ADR is
immutable: do not rewrite it. If the decision changes, write a new ADR and mark the
old one superseded. This keeps the decision history intact.

## Spikes feed decisions

When a decision needs research first, run a timeboxed spike:
`wingman new spike "<title>"`. State the question, the timebox, and the
expected output. The spike's recommendation becomes the input to an ADR; do not
skip straight to a decision without recording what was learned.

## Diagrams

When structure is easier shown than told, add a C4 or LikeC4 diagram (context,
container, or component level) under Architecture. Keep diagrams in the repo as
text so they diff and review like code.
