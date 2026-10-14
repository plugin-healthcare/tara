# Copilot code review of PR #17: triage

Copilot Code Review left 15 comments on PR #17 at `65102c1` on 2026-10-07.
Each finding is mapped to an existing 2.0.0 issue, so no new issues are needed.
Findings marked "checked" were confirmed against the code.

| # | Location | Finding | Checked | Goes to |
| - | -------- | ------- | ------- | ------- |
| 1 | `pyproject.toml:3` | The distribution is still named `tara`. | Yes | #21, already runbook step 14 |
| 2 | `generate.py:345` | `remove_owned_skills` joins names from `.tara/generated.json` to the directory without a per-path check, so a `../` name lets `rmtree` delete outside the repository. | Yes | #20 |
| 3 | `sync.py:228` | `_remove_skill` returns silently on an unsafe path, and `sync` then drops the lock entry and reports the skill as removed. | Yes | #20 |
| 4 | `generate.py:224` | `.tara/generated.json` is written without the containment check. | Yes, same as bug review finding 7 | #20 |
| 5 | `agent_docs.py:53`, `config.py:319` | `.agents/` indexes and `.tara/config.toml` are written without the containment check. | Yes, known gap | #20 |
| 6 | `catalog.py:338` | Collision checks read the destination and may prompt before the containment check runs. | No | #20 |
| 7 | `cli.py:273` | `tara init` overwrites a hand-written `copilot-instructions.md` and `.mcp.json` through `core._write`. | Yes, known gap | #30 |
| 8 | `hooks.py:170` | Installing a hook bundle rewrites `.claude/settings.json` without a confirmation path. | No | #30 |
| 9 | `generate.py:77` | A marker counts as ownership even after the developer edits the generated file, so a non-interactive sync overwrites those edits. | No | #24 |
| 10 | `claude.py:251`, `claude.py:274`, `opencode.py:199` | Generated agents and commands are never pruned when their Copilot source is deleted. | No | #18 |
| 11 | `cli.py:264` | Rerunning `tara init` without `--integrations` resets the integrations to Copilot only. | Yes | #18 |
| 12 | `prose-style.hooks.json:7` | The description says the hook blocks the write, but `PostToolUse` runs after the write and only returns the reason to Claude. | Partly: the hook works as feedback, the description is wrong | #61 |

## Proposed issue comments

- #20: keep it open after PR #17 merges, and add findings 2 to 6 as the remaining containment work.
- #30: add findings 7 and 8, plus bug review finding 5 (OpenCode port replaces user keys in `opencode.json`).
- #24: add finding 9.
- #18: add findings 10 and 11.
- #61: add finding 12.
