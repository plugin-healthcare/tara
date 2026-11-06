# Matt Pocock skills: conflicts with Tara and ideas worth adopting

Date: 2026-10-04
Source: [`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT), read at the default branch on 2026-10-04.

## Approach

Tara does not exclude skills from an external source.
Users browse and pick skills themselves (draft E), and Tara shows a warning on a skill that conflicts with Tara's way of working.
The ideas below are for Tara's own instructions and skills, written in Tara's own words and never copied.

## Conflict warnings

These are the notes Tara would show in `tara skill list` and before `tara skill add`.

| Skill | Warning | Severity |
| ----- | ------- | -------- |
| `implement-spec` | Creates branches, merges work, and opens pull requests marked as closing issues. This conflicts with Tara's rule that only the developer commits, and with linking issues through development links. | Strong |
| `to-spec`, `to-tickets`, `triage`, `wayfinder`, `code-review` | Need `/setup-matt-pocock-skills` first. They publish to the issue tracker with their own labels and use `docs/agents/`, while Tara drafts plans in `.agents/` for review first. | Strong |
| `setup-matt-pocock-skills` | Writes issue tracker and label conventions into the repository. | Strong |
| `handoff` | Writes the hand-off to the OS temp directory, while Tara keeps hand-offs in `.agents/memory/`. | Medium |
| `ask-matt` | Routes to the full set and points to skills that may not be installed. | Medium |
| `pr` | Uses its own pull request template. Check it against the repository's own template. | Low |
| `tdd` | Fits Tara's test-first step. Install only one TDD skill, because superpowers `test-driven-development` describes a different loop. | Low |
| `retro` | Refers to `CLAUDE.md`, `AGENTS.md`, and `CODING_STANDARDS.md` instead of the files Tara generates. | Low |

## Ideas worth adopting in Tara

| Idea | Source skill | Where it fits in Tara |
| ---- | ------------ | --------------------- |
| Name the anti-patterns: tests coupled to the implementation, tautological tests whose expected value repeats the code, and writing all tests before any code. | `tdd` | Base workflow, step 3, so it applies to every stack. |
| Mock only at system boundaries such as external APIs, time, and randomness, and never your own modules. | `tdd` (`mocking.md`) | Base workflow, step 3. The Python instructions now only say "mock I/O". |
| Agree the test boundaries with the developer before writing tests. | `tdd`, `to-spec` | Base workflow, step 2 (plan). |
| Review along two separate axes: does it follow the standards, and does it do what the issue asked. | `code-review` | `reviewing-changes` skill. |
| Turn a repeated mechanical review finding into an automated check instead of a written rule. | `retro` | `tara check` guidance and a possible retrospective prompt. |
| A hand-off references existing plans, issues, and commits by path instead of repeating them, and suggests which skills the next session needs. | `handoff` | Hand-off rules for `.agents/memory/`. |
| A pull request states whether the change is easy to undo and how much it can affect. | `pr` | A pull request template, if Tara adds one. |

## Language-neutral testing rules

Test-first, the anti-patterns, and mocking at boundaries apply to every stack, so they belong in `base.md`.
Each stack's instructions keep only the runner and its idioms: `pytest` and `uv` for Python, `cargo test` for Rust, and `vitest` for TypeScript.
A Rust or TypeScript repository then gets the same testing rules without the `uv` and `pytest` setup.
The Python testing section mixes both today: GIVEN/WHEN/THEN and "mock I/O" are general, and `pytest`, `parametrize`, and the `tests/` layout are Python specific.

## Follow-up

- Add the warnings as per-skill notes on the `mattpocock` source in the index (draft E).
- Decide which ideas to adopt. Each one is a small change to an existing Tara instruction or skill and can be its own issue in 2.x.
