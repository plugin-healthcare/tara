# Runbook: release a new version

## Trigger

Use this runbook to publish a release candidate or a stable version of the `tara-dev` package.
It is the manual procedure until the release pipeline (#22) automates the build and publish steps.

## Prerequisites

- Access required: maintainer rights on `plugin-healthcare/tara` and on the `tara-dev` project on PyPI.
- Tools required: `uv`, `gh`, `git`, and Python 3.12, 3.13, and 3.14 (installed through `uv python install`).
- Every issue in the release milestone is closed or moved to a later milestone.

Steps marked (developer) push, publish, or change shared infrastructure.
An agent prepares them and stops, and the developer runs them.

## Steps

### Prepare

1. Update `main` and create the branch `release/<version>`.
2. Set `version` in `pyproject.toml`. Use `<version>rc1` for a release candidate.
3. Move the `[Unreleased]` entries in `CHANGELOG.md` under the new version with today's date, and list each breaking change with its migration step.
4. Regenerate the CLI docs and check that the README install commands use `uvx --from tara-dev tara`.

### Verify locally

1. Run `tara check` and stop if it fails.
2. Run `uv run --python 3.12 pytest`, then the same command with 3.13 and 3.14.
3. Build once with `uv build`. The files in `dist/` are the release artifacts from here on.
4. Smoke-test the wheel with `uvx --from dist/tara_dev-<version>-py3-none-any.whl tara --version`.
5. Smoke-test the sdist with `uvx --from dist/tara_dev-<version>.tar.gz tara --version`.

### Exercise a scratch repository

Run these with the built wheel in a new temporary git repository.

1. Run `tara init` with every integration, run it again, and confirm `git status` shows no changes after the second run.
2. Run `tara skill add query`, delete `.github/skills/`, and confirm `tara rebuild` restores the skill from the lock.
3. Edit a generated file by hand and confirm `tara sync` asks before replacing it, and skips it when run non-interactively.
4. Add and remove an integration with `tara integrations` and confirm only Tara-owned files are removed.
5. Copy in a `.tara/config.toml` from 1.0 and confirm `tara rebuild --dry-run` loads it without errors.

### Publish

1. Open a pull request from `release/<version>` and merge it after review and green checks.
2. (developer) Tag the merge commit with `git tag v<version>` and push the tag.
3. (developer) Upload the `dist/` artifacts from the verify step to PyPI as `tara-dev`.
4. (developer) Create the GitHub release from the tag with the changelog section, attach the artifacts, and mark a release candidate as pre-release.

### Promote a release candidate to stable

1. Use the release candidate for at least a week and collect feedback.
2. Fix any findings and release `rc2` with this runbook if needed.
3. Set the final version and repeat the verify and publish steps on the same code that passed the candidate.

## Rollback

- PyPI does not allow replacing a version. (developer) Yank the broken version on PyPI and release a patch version with the fix.
- Do not delete or move a pushed tag. (developer) Mark the GitHub release as broken in its notes and link the patch release.

## Verification

1. On a clean machine, `uvx --from tara-dev tara --version` prints the new version.
2. In a new project, `uv add --dev tara-dev` installs it and `uv run tara --version` prints the new version.
3. The GitHub release shows the tag, the changelog section, and the attached artifacts.

## Contacts

| Role | Name / Channel |
|------|----------------|
| Release owner | @yannick-vinkesteijn |
| Maintainer | @dkapitan |
