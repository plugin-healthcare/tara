---
description: "Review code for correctness, clarity, and conventions. Use on a file, function, or diff after implementing, before integrating."
agent: agent
tools: [read, search, execute]
---

Review phase of the flow. Give structured feedback against the story's acceptance
criteria, Definition of Done, and any ADRs it references, plus the fixed flow in
`.github/copilot-instructions.md`.

**Correctness**: bugs, edge cases, error handling gaps
**Clarity**: naming, complexity, readability; clear over clever
**Conventions**: follows the project instructions, layout, and design principles
**Tests**: behaviour covered once, tests independent, the gate would pass
**Docs**: docs, runnable example, and changelog updated for the change
**Security**: secrets not committed, plus any obvious OWASP Top 10 concerns

Spend the review on judgement the gate cannot supply:

- Can a reader hold the design in their head? Prefer an obvious mechanism over a clever
  one when both satisfy the requirements.
- On a measured hot path, check repeated list scans, per-call derivation, and dataframe
  work pulled into Python. Account for construction cost and memory before recommending
  a different data structure.
- Distinguish intentional domain state from hidden temporal coupling. Flag argument
  mutation or call-order dependence when it changes results unexpectedly.
- Verify caches derive from immutable or versioned inputs and invalidate when their
  dependencies change.
- Check dependency direction when a change adds a `TYPE_CHECKING` block or function-body
  import. Those are signals to inspect, not findings by themselves.
- Flag duplicated business rules when independent copies can drift. Do not demand a
  shared abstraction for incidental expressions.

Do not report a finding you have not checked. Run the code, count the call sites, or
measure the thing. Say plainly when a suspected problem is not real.

Format as a prioritised list: `[blocker]`, `[suggestion]`, `[nit]`.
End with a one-line verdict: is the Definition of Done met, or what is missing.

Finally, file your review as `.agents/review/YYYYMMDDHHMM_<short-descriptive-title>.md`,
add a row to
`.agents/review/index.md`, and note the hand-off in `.agents/memory/`.
