# Optional Pi coding agent integration

Date: 2026-10-12
Status: draft for review, not posted as an issue.
Milestone: 2.x. It does not widen the 2.0.0 scope.
Depends on: #18 (integration lifecycle and strict config) and #20 (path containment), both in 2.0.0.
Related: #3 (goose support), #19 (open canonical agent formats), #50 (no commit tool by default).

## Goal

Let a developer who uses the Pi coding agent (`badlogic/pi-mono`) run `tara integrations copilot pi` and get the same rules, prompts, and skills as Copilot, Claude, and OpenCode.
Pi has no built-in permission system and runs with the permissions of the user who starts it.
Tara adds the most value by also generating a security baseline that matches its own rules, such as never commit and never force-push, so a Pi setup is safe by default.

## Non-goals

- Tara does not install Pi or any Pi package, and never runs `pi install` or `npm`.
- Tara does not write its own Pi sandbox. It recommends a pinned, reviewed third-party package or a container.
- Pi is not included in `tara init --tool all`. It is opt-in by name only.
- No MCP translation, unless the spike shows Pi reads MCP config.

## Assumptions to verify in the spike

These come from one web search on 2026-10-12 and a fork of the Pi repository, not from the upstream docs.
Step 1 confirms or corrects each one before any code is written.

| # | Assumption | Source |
| - | ---------- | ------ |
| A1 | Pi reads `AGENTS.md` from the working directory and its parents. | gitsense/pi mirror |
| A2 | Pi loads Agent Skills (`SKILL.md` folders) from a project folder such as `.pi/skills/`. | pi.dev package listings |
| A3 | Pi loads prompt templates from a project folder such as `.pi/prompts/`. | Not confirmed |
| A4 | Pi extensions are TypeScript modules, and packages are listed in a project settings file. | pi.dev, pi-mono examples |
| A5 | Pi has no built-in permission system, and upstream recommends a container or sandbox. | gitsense/pi mirror |
| A6 | `pi-permission-modes` offers OS sandboxing and an allow, ask, or deny policy, and `@akshaykarle/pi-tools` blocks destructive commands and secret exfiltration. | pi.dev listings |
| A7 | Pi has no MCP support in core. | Not confirmed |

## Design choices to settle in the spike

1. **Instructions.** Pi reads `AGENTS.md`, while Tara's source of truth is `.github/copilot-instructions.md`.
   Option a: write a thin `AGENTS.md` that points to the Copilot file, like `CLAUDE.md` does.
   Option b: reuse a shared `AGENTS.md` if #19 adopts one as the canonical format.
   Choose b if #19 has landed, otherwise a, and never overwrite an `AGENTS.md` that Tara did not write.
2. **Security baseline.** Option a: generate a policy file for one recommended package, pinned to an exact version.
   Option b: generate only a `docs/` page or a README section that lists the recommended setup, and write no config.
   Option c: generate a small Tara-owned extension.
   Recommendation: a, with b as the fallback if no package has a stable, documented policy format.
   Reject c, because Tara would then own security code in a language the project does not test.
3. **Which package.** Compare the candidates in A6 on maintenance, licence, a stable policy format, and whether the deny rules cover Tara's invariants.
   Record the choice and the pinned version in an ADR in `docs/decisions/`.

## Files

- `src/tara/core.py`: add `PI = "pi"` to the supported integrations, and keep it out of the `all` shorthand with an explicit opt-in set.
- `src/tara/pi.py`: new adapter, modelled on `claude.py`. It projects `.github/` into Pi's files and writes only through the helpers in `generate.py`.
- `src/tara/data/templates/pi/`: the policy template that maps Tara's rules to deny and ask entries.
- `tests/test_pi.py`: adapter tests.
- `README.md`, `docs/`, and `CHANGELOG.md`: the new integration, the security note, and how to remove it.

## Steps

### 1. Spike: verify the assumptions (1 day, timeboxed)

1. Read the upstream pi-mono docs and examples, and install Pi in a throwaway container.
2. Confirm or correct A1 to A7 in this plan, with links to the upstream files.
3. Try the two candidate security packages against a fixture repository: an attempted `git commit`, `git push --force`, `rm -rf` outside the repository, and a read of `.env`.
4. Settle the three design choices above and write the ADR.

**Review stop.** The developer approves the ADR before step 2.

### 2. Register Pi as an opt-in integration

1. Test: `normalize_integrations(["pi"])` returns Copilot and Pi, and `normalize_integrations(["all"])` does not include Pi.
2. Test: `tara integrations copilot pi` records `pi` in `.tara/config.toml` as an explicit name.
3. Implement in `core.py` and the CLI.
4. Changelog: Added entry.

**Review stop.**

### 3. Generate instructions, prompts, and skills

1. Tests first: each generated file, a rerun that changes nothing, a user-written `AGENTS.md` that is left alone, and a symlinked `.pi/` parent that is refused.
2. Implement `pi.py` for the files confirmed in the spike.
3. Hook the adapter into `tara integrations`, `tara sync`, and `tara rebuild`.

**Review stop.**

### 4. Generate the security baseline

1. Tests first: the policy denies commit, push, force-push, and reads of `.env` and credential files, and asks before `sudo` and `rm -rf`.
2. Generate the policy for the package chosen in the ADR, pinned to an exact version.
3. Print one line after Pi is added that names the package to install and tells the developer to review its source first.
   Tara never installs it.
4. If the developer did not install the package, `tara check` warns that Pi runs without a permission layer.

**Review stop.**

### 5. Removal and lifecycle

1. Test: dropping Pi from `tara integrations` (or the remove command from #18, if it adds one) deletes only the files Tara wrote, using the manifest from #18.
2. Add Pi to the end-to-end fixture tests from #39.

**Review stop.**

### 6. Documentation

1. README: a short section on Pi, the security baseline, and the container alternative.
2. One sentence per line, no em dashes, no jargon.

**Review stop.** The developer commits.

## Edge cases

- A repository already has an `AGENTS.md` from another tool, which Tara must not overwrite.
- A developer runs Pi from a subfolder, so `AGENTS.md` lookup from parent folders matters.
- The pinned security package is unpublished or renamed. `tara check` reports this as a warning and does not fail the build.
- Upstream changes Pi's folder layout. Keep the paths in one place in `pi.py`.

## Verification

- `uv run tara check` passes.
- In a fixture repository with the security package installed, Pi refuses the attempts from step 1.3.
- Dropping Pi leaves the repository as it was before Pi was added, apart from files the developer wrote.

## Sources

- https://github.com/gitsense/pi (mirror, Pi's stated security stance)
- https://cdn.jsdelivr.net/gh/akshaykarle/pi-tools@main/README.md
- https://pi.dev/packages/pi-permission-modes
