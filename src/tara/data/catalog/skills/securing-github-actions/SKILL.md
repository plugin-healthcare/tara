---
name: securing-github-actions
description: "Use when writing, reviewing, or hardening GitHub Actions workflows and CI/CD: setting least-privilege permissions, pinning actions, avoiding script injection and pull_request_target pitfalls, handling secrets and GITHUB_TOKEN safely, and wiring the tara check gate into CI."
---

# Securing GitHub Actions

CI runs with access to your code, tokens, and often deployment credentials, so a
sloppy workflow is a supply-chain hole. Write workflows that are least-privilege,
pinned, and injection-proof by default.

## Start from the standard CI template

Scaffold a secure gate workflow that mirrors `tara check`:

```
tara new ci
```

It writes `.github/workflows/ci.yml` with the conventions below already applied.

## Rules

- **Least-privilege permissions.** Set `permissions: contents: read` at the top of
  every workflow and widen per job only when needed (e.g. `pull-requests: write`).
  Never leave the default read/write token in place.
- **Pin third-party actions to a full commit SHA**, with the version in a comment:
  `uses: actions/checkout@<40-char-sha> # v7.0.0`. Tags and branches are mutable and
  can be repointed at malicious code; a SHA cannot.
- **Never interpolate untrusted input into a shell.** `${{ github.event.pull_request.title }}`,
  issue bodies, and branch names are attacker-controlled. Pass them through `env:`
  and reference `"$TITLE"` in `run:`; never inline `${{ ... }}` inside a `run` script.
- **Treat `pull_request_target` as dangerous.** It runs with a privileged token in
  the base repo's context. Do not check out and execute PR head code under it. Prefer
  plain `pull_request` for untrusted contributions.
- **Protect the checkout token.** Set `persist-credentials: false` on
  `actions/checkout` unless a later step needs to push.
- **Prefer OIDC over long-lived secrets** for cloud auth (`permissions: id-token: write`
  + a cloud login action). Never `echo` a secret or write it to logs or artifacts.
- **Bound every job.** Add `timeout-minutes` and a `concurrency` group with
  `cancel-in-progress: true` so stuck or superseded runs don't pile up.

## Check it

`actionlint` (correctness) and `zizmor` (security) run automatically via the
tara pre-commit standard whenever a workflow or action file changes. Run zizmor
directly for a one-off audit:

```
uvx zizmor .github/workflows/
```

Fix what it flags before merging. Never commit; the developer reviews and commits.
