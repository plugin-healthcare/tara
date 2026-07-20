---
name: release-semver-changelog
description: "Use when preparing a release, bumping a version, writing or updating a changelog, or branching for a feature or hotfix. Applies semantic versioning and GitHub flow, and checks the increment fits the project."
---

# Release: semver and changelog

Manage releases with semantic versioning, a Keep a Changelog file, and GitHub
flow. The goal is a clean, reviewable increment that fits the project direction.

## Semantic versioning (x.y.z)

- **major (x)**: breaking changes.
- **minor (y)**: new, backwards-compatible features.
- **patch (z)**: backwards-compatible bug fixes.

Docs, tests, CI, and other non-code changes do not bump the version. When in
doubt, pick the highest level of change in the release.

## Changelog

Keep a `CHANGELOG.md` in the Keep a Changelog format. Seed it once with
`tara new changelog` (writes `CHANGELOG.md` at the repo root):

- An `## [Unreleased]` section at the top collects changes as they land.
- Group entries under `Added`, `Changed`, `Fixed`, `Removed`, `Deprecated`,
  `Security`.
- On release, rename `Unreleased` to the new version with the date and open a fresh
  `Unreleased` section.
- Write entries for humans: what changed and why it matters, not the commit subject.

## GitHub flow

```
main  <-  feature/<name>   (optional smaller branches off the feature branch)
  ^-  hotfix/<name>
```

- Branch off `main`, open a pull request, merge back after review.
- Hotfixes branch from `main` and merge straight back.
- Use the `github` and `git` MCP to inspect branches, diffs, and PR state.

## Tags and release notes

- Tag releases as `v<x.y.z>` (annotated tag) on the merge commit, matching the
  version in `pyproject.toml` and the changelog heading.
- Release notes are the changelog section for that version. Do not write them twice:
  promote `Unreleased`, then reuse it as the notes.
- The tag and the version bump land together, so a tag always points at the commit
  that carries the matching `pyproject.toml` and `CHANGELOG.md`.

## CI and hooks

- CI should run the same gate as local: `tara check` (lint, format check, tests).
  A release is only cut from a green pipeline on `main`.
- Recommend a pre-commit hook that runs `uv run ruff check` and `uv run ruff format
  --check` so lint failures never reach CI. Keep the hook fast; leave the full test
  suite to CI.
- Never rely on a manual "remember to run the tests". If it is not in the gate, it
  does not gate.

## Release steps

1. Confirm the gate passes on `main`: `tara check` (and CI is green).
2. Update `CHANGELOG.md`: promote `Unreleased` to the new version with today's date.
3. Bump the version in `pyproject.toml` to match, following semver above.
4. Check the increment fits the overall project: no half-finished features, docs
   updated, the change still matches the project's direction.
5. Prepare the annotated `v<x.y.z>` tag and the release notes for the developer.

Never commit, push, or tag; the developer reviews and does that. You prepare the
changelog, the version bump, the tag command, and the release notes.
