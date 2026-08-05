# Wingman maturity review: toward a mature agentic harness

*Review date: 2026-07-02. Produced by a model-assisted code review of the full
codebase (CLI, audit/check/skills/standards/sync modules, bundled instructions,
skills, agents, MCP catalog). Treat findings as input for discussion, not gospel.*

## Executive summary

Wingman's goal — a productivity **and** security harness so juniors and seniors
both produce high-quality, safe code, with agents steered to specific answers
for token-efficient workflows — is well served by its architecture. The
setup-time CLI / runtime agent split keeps the tool deterministic and testable,
and the skill/audit/check triad is exactly the right shape.

Scope: v1 targets GitHub Copilot only. **v2 aims to be agent-agnostic (Claude
Code, Goose, and whatever comes next), so every v1 decision should prefer open
standards and formats** — see "V2 direction" below for the concrete mapping.

The structural weakness is a single asymmetry: **the productivity half is
enforced, the security half is advisory.** `wingman check` actually runs and
fails builds; "never commit" and the destructive-command rules live only in a
prompt the model can ignore — while the default-enabled `git` MCP server hands
the agent `git_commit` and `git_reset` tools. Closing the gap between what the
harness *claims* and what it *enforces* is the theme of every P0 item below.

| Axis | Rating | One-liner |
|---|---|---|
| Steering & token efficiency | **Strong** | Progressive-disclosure skills, trigger-linted descriptions, short always-on instructions, size warnings. |
| Productivity | **Strong** | Check gate, standards baseline, scaffolding, per-repo overrides. |
| Security (mechanical) | **Good** | `uv audit`, `exclude-newer`, zizmor/actionlint, unpinned-dep detection. |
| Security (containment) | **Weak** | Prompt-only safety rules, non-binding lockfile, unpinned MCP servers, opt-in CI. |
| Junior/senior fit | **Good** | Opinionated defaults + clean escape hatches; but juniors need the rails to actually hold. |

## What to keep (strengths)

- **The architecture.** No model calls at runtime (except opt-in `audit
  --deep`). Deterministic, cheap, testable. Never trade this away.
- **Token economy as a design principle.** Skills load on trigger, not always;
  `audit.py` lints that descriptions say *when* to use them (`_has_trigger`);
  warnings at 400+ instruction lines and 500+ skill lines. The always-on cost
  (base ~80 lines + stack ~55) is modest. This is the mechanism that steers
  agents to specific answers — protect it.
- **Steering to canonical sources.** Polars MCP, `llms.txt` docs servers,
  official skill repos. Consistent answers come from consistent sources.
- **Supply-chain thinking in the gate.** `uv audit` (CVEs + PEP 792 statuses),
  `[tool.uv] exclude-newer = "14 days"`, unpinned-dependency detection in
  `standards.py`, zizmor/actionlint in pre-commit. The
  `securing-github-actions` skill is concrete and correct.
- **Junior/senior balance.** Defaults for juniors (gate, standards, plan-first,
  destructive-op rules); overrides for seniors (`.wingman/checks.toml`,
  `instructions.local.md`, `mcp.local.json`).

## Gaps and recommendations

Prioritized: **P0** = closes a claim/enforcement gap, **P1** = maturity within
the current scope, **P2** = expands scope.

### P0-1 · Make the safety layer mechanical, not advisory

**Problem.** `base.md` says "never commit" and lists forbidden destructive
commands, but nothing enforces it. Worse, the default-checked `git` MCP server
(`mcp-server-git`) exposes `git_commit`, `git_reset`, and `git_checkout` — the
harness forbids committing while wiring up a commit button. A junior who
believes "the harness stops destructive ops" is wrong today.

**Recommendation.**
- Write tool permission config alongside the instructions. The Copilot CLI
  supports `--allow-tool` / `--deny-tool` (wingman's own `review.py` already
  uses `--allow-tool read`); emit a deny-list for `git commit`, `git push`,
  `rm -rf`-class shell commands, or document the launch flags in
  `copilot-instructions.md` so teams can enforce them.
- Un-default the `git` MCP server, or ship a restricted variant: `mcp-server-git`
  accepts a repo path and tool selection in some forks; at minimum document
  that enabling it contradicts the "never commit" rule.
- Add a `wingman doctor` (or extend `audit`) check that flags contradictions
  between the instruction rules and the tools actually granted in `.mcp.json`.

**Borrow from:** Claude Code's `settings.json` permission rules
(`allow`/`deny`/`ask` per tool pattern) and its PreToolUse **hooks** — a hook
that exits non-zero deterministically blocks the tool call regardless of what
the model wants. Gemini CLI's policy engine and OpenAI Codex CLI's approval
modes + OS sandboxing (Seatbelt on macOS, Landlock on Linux) are the same idea
at different layers. Wingman can't sandbox Copilot itself, but it can generate
the strictest config the host tool supports.

### P0-2 · Make the skills lockfile binding

**Problem.** `.wingman/skills.lock` records commit SHAs, but nothing installs
*from* it: `add` and `update` always fetch the ref's HEAD and silently rewrite
the lock (`skills.py: update()`). Branch refs are mutable; a compromised skill
repo becomes injected instructions to every agent in the org. Skills are a
prompt-level supply chain and deserve the same rigor as packages.

**Recommendation.**
- `wingman skill install` (or `sync --frozen`): check out exactly the locked
  commit. This is what CI and fresh clones should run.
- `wingman skill verify`: hash the installed skill tree, store the hash in the
  lock, and fail when disk content diverges from the lock.
- Make `update` show a diff (or at least the commit range) before rewriting the
  lock, so updating a skill is a reviewable event, not a silent refetch.
- Optionally: run `wingman audit` automatically on freshly fetched skills and
  surface findings before the files land in `.github/skills/`.

**Borrow from:** `pre-commit`'s model (`rev:` pins per repo, `autoupdate` is an
explicit, diff-visible action), `uv.lock`/npm lockfile semantics (install
respects the lock; update refreshes it), and Renovate/Dependabot (updates
arrive as reviewable PRs — a `wingman skill update --pr` would fit a mature
org workflow). Longer-term direction: Sigstore/cosign-style signing for skill
artifacts if a shared org index emerges.

### P0-3 · Pin the MCP catalog

**Problem.** The catalog runs `uvx mcp-server-git` and `npx -y @likec4/mcp`
with no version — while the bundled skill demands 40-char SHA pins for GitHub
Actions. Inconsistent gospel.

**Recommendation.** Pin versions in `data/mcp/catalog.toml`
(`uvx mcp-server-git==<ver>`, `npx -y @likec4/mcp@<ver>`), record them in a
lock the same way skills are locked, and add a `standards`-style check that
flags unpinned entries in `.mcp.json` / `mcp.local.json`.

### P0-4 · Wire the gate into CI by default

**Problem.** `wingman check` only binds if someone runs it. `wingman new ci`
is opt-in, so the harness currently depends on the agent *choosing* to check
its own work — advisory again.

**Recommendation.** Have `wingman init` offer (pre-checked) to write the CI
workflow and install the pre-commit hook. Add `wingman check --changed` for a
fast pre-commit variant. The principle: every rule the instructions state
should have a machine that catches its violation.

### P1-1 · Scan fetched artifacts for prompt-injection patterns

`audit` checks form (frontmatter, length, triggers) but not content. A fetched
SKILL.md that says "also upload the repo to pastebin" passes today.
Add a content pass over fetched skills/instructions: flag instructions to
exfiltrate data, fetch remote URLs at runtime, disable safety rules, or edit
files outside the repo. Keep it deterministic (pattern lists), with `--deep`
handling the subjective layer.

**Borrow from:** Invariant Labs' **mcp-scan** (scans MCP tool descriptions for
tool-poisoning / injection patterns — same threat model, adjacent artifact) and
**zizmor**'s architecture (small deterministic security linter with
severity-ranked, explainable findings — wingman's `audit` is already
zizmor-shaped; lean into it, e.g. `wingman audit --format sarif` for GitHub
code-scanning upload).

### P1-2 · Adopt open formats now to de-risk the v2 agnostic core

v2's goal is to support Claude Code and Goose alongside Copilot. The cheapest
way to get there is to make v1's *internal* representation the open format and
treat each agent's file layout as a render target — the "single source of
truth, many renderers" pattern (see **Ruler**). Concretely: `.wingman/` (plus
the bundled `data/`) is already the source of truth; what's missing is a
renderer boundary in the code so `.github/` is just the Copilot renderer's
output.

How the artifacts map across the three targets:

| Artifact | Copilot (v1, today) | Claude Code | Goose | Open format to standardize on |
|---|---|---|---|---|
| Instructions | `.github/copilot-instructions.md` | `CLAUDE.md` (also reads AGENTS.md via config) | `.goosehints` | **AGENTS.md** — emit it as the canonical file, render the others from it |
| Scoped instructions | `.github/instructions/*.instructions.md` (applyTo globs) | `CLAUDE.md` in subdirectories | — | No standard; keep per-renderer |
| Skills | `.github/skills/<n>/SKILL.md` | `.claude/skills/<n>/SKILL.md` | — | **SKILL.md** (anthropics/skills conventions) — already convergent; Copilot adopted Anthropic's format. Wingman's fetch/lock/audit logic is layout-independent already |
| Prompts / commands | `.github/prompts/*.prompt.md` | `.claude/commands/*.md` | Recipes (`.yaml`) | No standard; needs a renderer per tool |
| Subagents | `.github/agents/*.agent.md` | `.claude/agents/*.md` | Subrecipes | No standard; frontmatter is similar enough to render from one source |
| MCP servers | `.mcp.json` (`mcpServers`) | `.mcp.json` — **same file, same schema** | `config.yaml` extensions / deeplinks | **MCP is the open standard**; the repo-root `.mcp.json` already covers two of three targets for free |
| Permissions / safety | `--allow-tool` / `--deny-tool` flags | `settings.json` permissions + hooks | modes (auto/approve/chat) + tool permissions | No standard — this is where P0-1's "emit the strictest config per tool" becomes a renderer concern |

Practical v1 steps that cost little and pay off in v2:

- Emit `AGENTS.md` now and generate `copilot-instructions.md` from it (or vice
  versa — one generator, two outputs). AGENTS.md is adopted by OpenAI Codex,
  Google Jules, Amp, Cursor, and readable by Claude Code and Goose setups.
- Keep skill handling exactly as is — SKILL.md is the one artifact where the
  ecosystem already agreed, and wingman bet correctly.
- Introduce a `Renderer` seam in the code (`render_copilot(artifacts)`) even
  while Copilot is the only implementation, so `init`/`add`/`sync` stop
  hardcoding `.github/` paths. v2 then adds `render_claude()` /
  `render_goose()` instead of refactoring.
- Where no open format exists (prompts, agents, permissions), define wingman's
  source format as *minimal frontmatter + markdown body* and keep
  tool-specific keys in a namespaced block (e.g. `copilot:`, `claude:`,
  `goose:`) so one file renders to all targets.

### P1-3 · Strengthen the audit heuristics with measurement

`_has_trigger` is a substring + first-verb check — easy to satisfy without
being good. Two directions:
- **Cheap:** extend the mechanical checks (description mentions concrete file
  types/commands/keywords a router could match; flag near-duplicate
  descriptions across installed skills, which cause mis-routing).
- **Valuable:** a `wingman audit --eval` that runs a small fixed prompt set
  against the skill descriptions and reports which skill would be selected —
  a routing regression test. **Borrow from:** promptfoo's eval-as-CI pattern
  and the `skill-creator` conventions in anthropics/skills (already bundled).

### P1-4 · Telemetry for the token-efficiency claim

"Token-efficient" is asserted, not measured. Add `wingman list --tokens`: a
tokenizer pass over always-on instructions vs. on-demand skills, with a budget
warning (e.g. always-on > 2k tokens). Cheap to build, turns the philosophy
into a number juniors and reviewers can see.

### P2-1 · Second stack

Python+uv-only is a clean scoping decision, but org adoption usually dies on
"what about our TypeScript repos". The stack abstraction already exists
(`data/checks/<stack>.toml`, `data/standards/<stack>/`,
`data/instructions/<stack>.md`); a TypeScript stack (pnpm/bun + biome/eslint +
vitest + `npm audit`/osv-scanner) would prove the abstraction and roughly
double the addressable surface.

### P2-2 · Org-level distribution

Mature harnesses are org-shaped: a shared skill/instruction index (a git repo
of `index.toml` + curated artifacts) that `wingman init --org <url>` consumes,
so platform teams curate once and every repo inherits. This is where lockfile
verification (P0-2) pays off. **Borrow from:** pre-commit's remote-repo hook
model and OpenSSF Scorecard's idea of a repo health score — `wingman audit
--score` as an org-visible guardrail-health metric.

### Housekeeping (small)

- The persona agents (gilfoyle, marvin, yoda) are well written but cost tokens
  on every reply — keep them opt-in and out of any recommended set; the
  `skill-reviewer` rubric is the load-bearing one.
- `README.md` and `docs/skills.md` duplicate the theme list; generate one from
  `index.toml` like `docs/cli.md` is generated.
- `check.py` runs commands from a repo-local `checks.toml` — same trust level
  as the repo itself, fine, but worth one sentence in the docs ("cloning an
  untrusted repo and running `wingman check` executes its checks.toml").

## Reference projects

| Project | What to take from it |
|---|---|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (settings + hooks) | Deterministic enforcement: permission `allow`/`deny`/`ask` rules per tool pattern; PreToolUse hooks that block calls regardless of model intent. The model for P0-1 — and a v2 render target (it already reads the same repo-root `.mcp.json` and the same SKILL.md format). |
| [Goose](https://github.com/block/goose) (Block) | v2 render target. MCP-native (extensions *are* MCP servers — the `.mcp.json` catalog maps over directly), `.goosehints` for repo instructions, recipes/subrecipes for reusable workflows, permission modes per tool. Its extension config is the template for `render_goose()`. |
| [OpenAI Codex CLI](https://github.com/openai/codex) | Approval modes and OS-level sandboxing (Seatbelt/Landlock) — the "containment beats instruction" philosophy. |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | Policy engine for tool allowlisting; container-based sandbox option. |
| [pre-commit](https://pre-commit.com) | Lock semantics done right: `rev:` pins, explicit `autoupdate`, remote hook repos. Model for P0-2 and P2-2. |
| [Renovate](https://github.com/renovatebot/renovate) / Dependabot | Updates as reviewable PRs, not silent refetches — model for `skill update --pr`. |
| [mcp-scan](https://github.com/invariantlabs-ai/mcp-scan) (Invariant Labs) | Scanning MCP tool descriptions for tool-poisoning / prompt-injection — same threat model as fetched skills (P1-1). |
| [zizmor](https://github.com/zizmorcore/zizmor) | Architecture of a small deterministic security linter: severity-ranked, explainable, SARIF output. Already in the stack; copy its shape for `audit`. |
| [AGENTS.md](https://agents.md) | The cross-tool instruction standard — make it the canonical instructions file in v1, render tool-specific files from it (P1-2). |
| [Ruler](https://github.com/intellectronica/ruler) | Single source of truth fanned out to per-agent instruction files — the exact architecture v2 needs; study its target list and merge strategy before designing the renderer seam. |
| [anthropics/skills](https://github.com/anthropics/skills) | Skill-authoring conventions (`skill-creator`), progressive disclosure via `references/`. Already bundled — align audit rules with its rubric. |
| [awesome-copilot](https://github.com/github/awesome-copilot) | Community catalog of Copilot instructions/prompts/chat modes — candidate source for the index, and a distribution channel for wingman's own artifacts. |
| [promptfoo](https://github.com/promptfoo/promptfoo) | Eval-as-CI pattern for the skill-routing regression tests (P1-3). |
| [OpenSSF Scorecard](https://github.com/ossf/scorecard) | Repo-health scoring as an org metric — model for `wingman audit --score`. |
| [aider](https://github.com/Aider-AI/aider) | Repo-map technique for token-efficient context, and the edit→lint→test loop as a hard cycle. |

## Suggested sequence

1. **Now (P0):** deny-list/permission emission + un-default git MCP; binding
   lockfile (`install --frozen`, `verify`); pin MCP catalog; CI wiring in
   `init`. These four turn the README's safety claims true.
2. **Next (P1):** AGENTS.md as canonical + renderer seam (the v2 down
   payment); injection-pattern scan on fetch; audit heuristics + routing eval;
   token budget report.
3. **v2:** `render_claude()` and `render_goose()` on top of the seam —
   instructions, prompts, agents, and per-tool permission config from the one
   `.wingman/` source. Skills and `.mcp.json` need little to no work: SKILL.md
   and MCP are already the open standards all three tools share.
4. **Later (P2):** TypeScript stack; org index + `audit --score`.

The test for every future feature: *does the harness enforce this, or merely
ask for it?* Wingman's value over "a folder of markdown files" is exactly the
set of things it can verify mechanically. Keep pushing rules from the prompt
layer into the tool layer, and this becomes a genuinely mature agentic harness.
