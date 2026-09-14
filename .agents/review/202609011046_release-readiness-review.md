# Tara 1.1 release-readiness review

Review date: 2026-09-01.

## Verdict

Tara is a promising beta, but PR #17 is not ready for a stable release.
The implementation has a strong automated baseline, yet release engineering and
integration lifecycle safety still have blocking gaps.

The proposed 1.1.0 also documents breaking behavior. Under the project's stated
Semantic Versioning policy, either preserve 1.x compatibility or release this
work as 2.0.0.

## Evidence

| Area | Assessment | Evidence |
| ---- | ---------- | -------- |
| Automated quality | Strong | `tara check` passes with 259 tests, lint, format, types, and dependency audit. |
| Python compatibility | Good locally | The full suite passes on Python 3.12, 3.13, and 3.14. CI currently tests only the version in `.python-version`. |
| Packaging | Buildable | The 1.1.0 sdist and wheel build, and the wheel's `tara --version` smoke test passes. |
| Change safety | Not stable | #18 tracks configuration, stale-output, atomic-write, and cleanup defects. |
| Filesystem safety | Blocking | Generated child paths can traverse a symlinked parent and write or recursively delete outside the repository. |
| Distribution | Blocking | The `tara` name on PyPI belongs to an unrelated project. `uvx tara` does not install this repository's package. |
| Release automation | Weak | There is no package publication workflow, artifact attestation, release build job, or automated install smoke test. |
| Repository governance | Weak | `main` has no branch protection and there is no documented support, security, or deprecation policy. |
| Product integration | Partial | File transformations are well unit-tested, but there are no end-to-end compatibility tests against supported Copilot, Claude Code, and OpenCode versions. |

## PR #17

The two Copilot review comments about nested `check.md` commands are fixed at
the branch head. Both Claude and OpenCode now key collisions by relative path,
with regression tests for nested prompts.

The failed GitHub gate was caused by an ANSI-sensitive help assertion. The test
now verifies the stable semantic tokens independently, including under forced
color output.

Do not merge for a stable release until these blockers are resolved:

1. Complete #18, including stale generated agent and command pruning,
   ownership-safe OpenCode config updates, strict config validation, atomic
   writes, and failure-safe integration removal.
2. Reject generated and cleanup paths with symlinked ancestors. Verify resolved
   paths remain below the repository root before writes, copies, unlinks, or
   recursive deletion.
3. Decide the public distribution name. Either obtain the `tara` PyPI project
   or publish under an available distribution name while retaining the `tara`
   console command.
4. Resolve the SemVer mismatch. Preserve 1.x behavior for 1.1.0, or call the
   documented breaking release 2.0.0.

## Stable release path

1. Finish the lifecycle and filesystem safety fixes with regression tests for
   idempotency, source deletion, rollback after config-write failure, symlinked
   parents, and preservation of hand-written files.
2. Add CI jobs for Python 3.12, 3.13, and 3.14, then build the sdist and wheel
   and install each artifact in a clean environment.
3. Add a release workflow using PyPI trusted publishing and attestations. Build
   once, publish the same artifacts, and attach them to the GitHub release.
4. Protect `main` and require the gate, pre-commit, compatibility matrix, and
   package smoke jobs before merge.
5. Publish a release candidate. Exercise init, sync, integration add/remove,
   legacy-config migration, and clean uninstall in fixture repositories with
   the supported agent tools.
6. Promote the exact tested artifacts to stable, tag from the protected main
   commit, and verify the documented `uvx` and `uv add --dev` installation
   commands from a clean machine.

## Maturity target

A stable release is justified when the package is reproducibly installable,
all supported Python versions are required checks, generated-file ownership is
safe under failure and symlinks, breaking changes follow SemVer, and a release
candidate has completed end-to-end tool compatibility tests.
