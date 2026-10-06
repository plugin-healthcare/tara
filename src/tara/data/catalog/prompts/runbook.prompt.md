---
description: "Execute a runbook from .agents/runbooks/ step by step. Use when running an operational procedure such as a release."
agent: agent
tools: [read, edit, execute, search]
---

Execute a runbook from `.agents/runbooks/`.
Follow the Executing rules in `runbooks.instructions.md`.

1. Ask which runbook to run if it is not given, and list the files in `.agents/runbooks/`.
2. Read the runbook and list its placeholders. Ask for any value you cannot derive from the repository.
3. Check every prerequisite and stop if one is missing.
4. Run the steps in order. After each step, report the command and its result in one line.
5. At a `(developer)` step, stop, show the exact command, and wait until the developer confirms it is done.
6. On a failed step or unexpected result, stop, report what happened, and point to the Rollback section.
7. Run every Verification step and report each as passed or failed.
8. Log the run in `.agents/memory/` and keep its `index.md` current.
9. If a step was wrong or outdated, propose the edit to the runbook.
