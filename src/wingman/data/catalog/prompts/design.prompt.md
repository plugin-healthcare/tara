---
description: "Design a solution before building it. Use for architecture decisions, research or spikes, and modelling the system. Produces ADRs and LikeC4 diagrams."
agent: agent
tools: [read, search, edit]
---

Design phase of the flow. Decide *how* to build something before writing feature code.

1. Restate the problem and the constraints in one or two sentences.
2. Research first: read the existing code, then official docs. Note what already exists
   and must not be reinvented.
3. Lay out the realistic options with their trade-offs (cost, risk, fit with the
   composable-stack principles and current architecture).
4. Recommend one option and justify it.
5. Record the decision as an ADR (`wingman new adr "<title>"`), following the
   `writing-adrs` skill: MADR-minimal plus the house Status/Date/Authors block and
   optional Architecture and Rollout sections.
6. When structure needs a picture, model it with a LikeC4 diagram rather than prose.

Do not write feature code in this phase. Output the decision and diagrams, and stop.

Finally, record the hand-off in the `.agent/tracking/` ledger (schema and command
in `.github/copilot-instructions.md`).
