# Wingman maturity: execution plan

Execution plan derived from `docs/maturity-review.md` (review date 2026-07-02).
The review's theme: **close the gap between what the harness claims and what it
enforces**. Push rules from the prompt layer into the tool layer.

Guiding test for every item below: *does the harness enforce this, or merely
ask for it?*

## Phases at a glance

| Phase | Goal | Items |
|---|---|---|
| Phase 0 (P0) | Make the README's safety claims true | P0-1 … P0-4 |
| Phase 1 (P1) | Maturity within current scope + v2 down payment | P1-1 … P1-4 |
| Phase 2 (P2) | Expand scope | P2-1, P2-2 |
| Housekeeping | Small correctness/doc fixes | H-1 … H-3 |

Each item lists: **outcome**, **touch points** (real modules), **acceptance**
(how we know it's done and enforced), and **effort** (S/M/L).

---

## Phase 0 — Enforcement (turns claims true)

### P0-1 · Make the safety layer mechanical, not advisory
- **Outcome:** destructive ops (`git commit`, `git push`, `rm -rf`-class) are
  blocked or explicitly gated by config wingman emits, not just prose in
  `base.md`. The `git` MCP server no longer contradicts the "never commit" rule.
- **Touch points:**
  - `src/wingman/data/instructions/base.md` (source of the advisory rules).
  - `src/wingman/data/mcp/catalog.toml` + `data/mcp/base.json` (un-default or
    ship a restricted `git` server variant).
  - New emission of Copilot `--allow-tool`/`--deny-tool` config or documented
    launch flags in the generated `copilot-instructions.md`
    (`review.py` already uses `--allow-tool read` — reuse that knowledge).
  - New contradiction check (extend `audit.py`, or a new `wingman doctor`) that
    flags when granted tools in `.mcp.json` violate instruction rules.
- **Acceptance:** a repo with the default MCP set + the emitted deny config
  cannot `git commit` via the agent; `wingman audit`/`doctor` fails when
  `.mcp.json` grants a tool the instructions forbid. Test in `tests/`.
- **Borrow:** Claude Code `settings.json` allow/deny + PreToolUse hooks; Codex
  approval modes; Gemini policy engine.
- **Effort:** M–L.

### P0-2 · Make the skills lockfile binding
- **Outcome:** `.wingman/skills.lock` is authoritative. Install checks out the
  locked commit; update is an explicit, reviewable event; disk content is
  verifiable against the lock.
- **Touch points:** `src/wingman/skills.py` (`add()`, `update()` currently fetch
  HEAD and silently rewrite the lock), `src/wingman/sync.py`.
- **Work:**
  - `wingman skill install` / `sync --frozen`: check out exactly the locked SHA.
  - `wingman skill verify`: hash installed skill tree, store hash in lock, fail
    on divergence.
  - `update` shows commit range / diff before rewriting the lock.
  - Optional: run `audit` on freshly fetched skills before they land in
    `.github/skills/`.
- **Acceptance:** fresh clone + `install --frozen` reproduces exact skill tree;
  `verify` fails on tampering; `update` prints what changed before writing.
  Tests cover frozen install, verify-mismatch, update-diff.
- **Borrow:** pre-commit `rev:` pins + explicit `autoupdate`; `uv.lock`/npm lock
  semantics; Renovate/Dependabot PR model (`skill update --pr` later).
- **Effort:** M.

### P0-3 · Pin the MCP catalog  ✅ done
- **Outcome:** no unversioned `uvx`/`npx` MCP launches; unpinned entries are
  flagged like unpinned deps already are.
- **Touch points:** `src/wingman/data/mcp/catalog.toml`
  (`uvx mcp-server-git`, `npx -y @likec4/mcp` → pinned versions), lock the
  versions the way skills are locked, add a check in `src/wingman/standards.py`
  (mirrors existing unpinned-dependency detection) or `audit.py` for
  `.mcp.json` / `mcp.local.json`.
- **Acceptance:** catalog entries carry versions; check fails on an unpinned
  `.mcp.json` entry. Test added.
- **Effort:** S–M.
- **Delivered:** catalog pinned (`mcp-server-git@2026.6.16`, `@likec4/mcp@1.58.0`);
  `audit.py` now audits `.mcp.json` / `.wingman/mcp.local.json`, warning on any
  package-runner server without a version pin (surfaced by `wingman audit`, fails
  under `--strict`). Tests in `tests/test_audit.py`.
- **Lock decision:** no separate MCP lock. Unlike skills (mutable git HEAD →
  `skills.lock` pins the SHA), MCP versions are exact strings in `catalog.toml`
  written verbatim into the committed `.mcp.json`, which is itself the lock. A
  hash-based lock was considered for parity with Action SHA pins but skipped as
  redundant indirection for a lean setup.

### P0-4 · Wire the gate into CI by default
- **Outcome:** the check gate binds without someone remembering to run it.
- **Touch points:** `src/wingman/core.py` / init flow (offer, pre-checked, to
  write `data/templates/ci-github.yml` and install the pre-commit hook),
  `src/wingman/check.py` (add `check --changed` fast variant).
- **Acceptance:** `wingman init` writes CI + pre-commit by default (opt-out);
  `check --changed` runs only on changed files. Tests for both.
- **Effort:** M.

**Phase 0 exit criteria:** the five safety claims in the README are each backed
by a mechanism that fails on violation.

---

## Phase 1 — Maturity + v2 down payment

### P1-1 · Scan fetched artifacts for prompt-injection patterns
- **Outcome:** `audit` inspects *content*, not just form. Deterministic pattern
  pass flags exfiltration, runtime remote fetches, safety-rule disabling,
  out-of-repo edits. Subjective layer stays under `--deep`.
- **Touch points:** `src/wingman/audit.py` (currently checks frontmatter,
  length, `_has_trigger`); add `--format sarif` for code-scanning upload.
- **Acceptance:** a SKILL.md containing an exfiltration instruction fails audit;
  SARIF output validates. Test fixtures with injection patterns.
- **Borrow:** Invariant Labs mcp-scan; zizmor's severity-ranked/SARIF shape.
- **Effort:** M.

### P1-2 · Adopt open formats to de-risk v2 agnostic core
- **Outcome:** `.wingman/` (+ bundled `data/`) is the single source of truth;
  `.github/` becomes the output of a Copilot renderer. `AGENTS.md` is canonical
  instructions; `copilot-instructions.md` is generated from it.
- **Touch points:** introduce a `Renderer` seam (`render_copilot(artifacts)`) so
  `init`/`add`/`sync` stop hardcoding `.github/` paths (`core.py`, `sync.py`,
  `skills.py`, `docs.py`). Keep skill handling as-is (SKILL.md already
  convergent). For prompts/agents/permissions with no open standard: minimal
  frontmatter + markdown body, tool-specific keys namespaced (`copilot:`,
  `claude:`, `goose:`).
- **Acceptance:** one generator emits `AGENTS.md` + `copilot-instructions.md`;
  all Copilot artifacts flow through `render_copilot`; no `.github/` path
  literals outside the renderer. Tests assert renderer output paths.
- **Borrow:** Ruler (single source → per-agent fan-out); AGENTS.md spec.
- **Effort:** L.

### P1-3 · Strengthen audit heuristics with measurement
- **Outcome:** routing quality is measurable, not just substring-satisfied.
- **Touch points:** `src/wingman/audit.py` (`_has_trigger`).
  - Cheap: flag descriptions lacking concrete file types/commands/keywords;
    flag near-duplicate descriptions across installed skills (mis-routing).
  - Valuable: `wingman audit --eval` runs a fixed prompt set against skill
    descriptions and reports which skill routes — a routing regression test.
- **Acceptance:** near-duplicate descriptions are flagged; `--eval` reports
  selected skill per fixture prompt. Test for both.
- **Borrow:** promptfoo eval-as-CI; anthropics/skills `skill-creator` rubric.
- **Effort:** M.

### P1-4 · Telemetry for the token-efficiency claim
- **Outcome:** "token-efficient" becomes a number.
- **Touch points:** `wingman list --tokens` (`cli.py` + `docs.py`/`catalog.py`):
  tokenizer pass over always-on instructions vs. on-demand skills, budget
  warning (e.g. always-on > 2k tokens).
- **Acceptance:** `list --tokens` prints always-on vs on-demand token counts and
  warns over budget. Test with a known fixture size.
- **Effort:** S–M.

**Phase 1 exit criteria:** fetched content is scanned, routing is measurable,
token cost is visible, and the renderer seam exists (v2-ready).

---

## Phase 2 — Scope expansion

### P2-1 · Second stack (TypeScript)
- **Outcome:** proves the stack abstraction; ~doubles addressable surface.
- **Touch points:** `data/checks/<stack>.toml`, `data/standards/<stack>/`,
  `data/instructions/<stack>.md` already parameterize stack. Add TypeScript:
  pnpm/bun + biome/eslint + vitest + `npm audit`/osv-scanner.
- **Acceptance:** `wingman init` supports a TS stack end to end; checks run.
  Tests for the TS check/standards path.
- **Effort:** L.

### P2-2 · Org-level distribution
- **Outcome:** platform teams curate once; repos inherit. Depends on P0-2
  lockfile verification.
- **Touch points:** shared skill/instruction index (git repo of `index.toml` +
  curated artifacts) consumed by `wingman init --org <url>`; `wingman audit
  --score` as an org guardrail-health metric.
- **Acceptance:** `init --org` pulls and locks from a remote index; `audit
  --score` emits a health score. Tests for org fetch + score.
- **Borrow:** pre-commit remote-repo hooks; OpenSSF Scorecard.
- **Effort:** L.

---

## Housekeeping (small, do opportunistically)

- **H-1 · Persona agents opt-in.** Keep gilfoyle/marvin/yoda out of any
  recommended set (per-reply token cost); `skill-reviewer` is the load-bearing
  one. Touch: `data/skills/index.toml` / recommended-set logic.
- **H-2 · Generate the theme list.** `README.md` and `docs/skills.md` duplicate
  the theme list; generate one from `index.toml` like `docs/cli.md` is
  generated (`scripts/`, `docs.py`). Keeps docs in sync (note: `docs/cli.md` is
  already auto-generated — follow that pattern).
- **H-3 · Document check trust.** One sentence in docs: cloning an untrusted
  repo and running `wingman check` executes its `checks.toml`
  (`check.py` runs repo-local commands).

---

## Suggested sequence (from the review)

1. **Now (P0):** P0-1 permissions/deny + un-default git MCP → P0-2 binding
   lockfile → P0-3 pin MCP catalog → P0-4 CI wiring in `init`.
2. **Next (P1):** P1-2 AGENTS.md + renderer seam → P1-1 injection scan →
   P1-3 audit heuristics/eval → P1-4 token budget report.
3. **v2:** `render_claude()` / `render_goose()` on the seam (skills + `.mcp.json`
   need little work — already open standards).
4. **Later (P2):** TS stack → org index + `audit --score`.

## Cross-cutting requirements

- Every new rule ships with a test in `tests/` and, where applicable, a check
  that fails on violation.
- Keep the no-model-calls-at-runtime architecture (except opt-in
  `audit --deep`) — do not trade it away.
- Preserve the setup-time CLI / runtime agent split: wingman sets up and
  verifies; Copilot is the runtime.
