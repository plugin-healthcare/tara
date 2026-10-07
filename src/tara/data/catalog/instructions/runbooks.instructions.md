---
applyTo: ".agents/runbooks/**/*.md"
description: "Runbook conventions: structure, executable steps, developer-only actions, rollback, and verification."
---

# Runbooks

Scaffold a new runbook with `tara new runbook "<title>"`.
Execute one with the `/runbook` prompt.

## Writing

- Keep the template sections: Trigger, Prerequisites, Steps, Rollback, Verification, and Contacts.
- Write each step as one action with the exact command, in the order it must run.
- State the expected result of a step when the next step depends on it.
- Mark every step that pushes, publishes, deletes, or changes shared infrastructure with `(developer)`.
- Give every `(developer)` step a rollback entry, or state that it cannot be undone.
- Use placeholders in angle brackets, such as `<version>`, and list them under Prerequisites.
- Keep secrets, hostnames of private systems, and credentials out of the runbook.

## Executing

- Read the whole runbook and resolve every placeholder before running the first step.
- Run the steps in order, and do not skip or reorder them.
- Stop at the first failed step or unexpected result, report it, and wait for the developer.
- Never run a `(developer)` step. Prepare the exact command and hand it to the developer.
- Run every Verification step at the end, and report each one as passed or failed.
- Log the run in `.agents/memory/` with the runbook, the inputs, each step's result, and any deviation.
- When a step is wrong or outdated, propose an edit to the runbook instead of working around it.
