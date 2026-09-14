---
applyTo: "deploy/**/*,infra/**/*,services/**/*,config/**/*,**/justfile,**/Justfile"
description: "Deployment conventions: task runner, secret handling, Helm values layering, and image builds."
---

# Deployment and infrastructure

Deploy manifests hold no business logic. If a step needs branching or computation, it
belongs in the library package with a test, not in a template or a shell one-liner.

## Task runner

Every deploy action has a named task. Run the task runner with no arguments (`just`) to
list them. A command that only exists in someone's shell history is not a deploy step.

## Secrets

- Never commit a secret. Keep `.env`, `secrets.sh`, `values-prod.yaml`, `kubeconfig.yaml`
  and any `certs/` directory in `.gitignore`.
- Commit an example counterpart for each (`x.example` next to `x`) so a new machine can
  be set up without asking anyone what the file should contain.
- Mark every value to be filled in with a single searchable prefix, for example
  `CHANGE_ME_`, so a half-configured environment fails a grep rather than at runtime.
- A password shared by several components (database, auth server, job runner) is one
  value in one place. List the places it has to reach, and change them together.

## Helm and values layering

- Layer values base to specific: `values.yaml`, then `values-local.yaml`, then the
  gitignored `values-prod.yaml`. Nothing environment-specific in the base file.
- Guard every optional template with `{{- if .Values.<component>.enabled }}`.
- Keep one source of truth for the domain (`global.domain`) and derive hostnames from
  it. Domain mismatches between ingress, OIDC redirect URIs, and proxy issuer URLs are
  the most common cause of login loops.
- Name the release once and derive component names from it (`<release>-<component>`).

## Container images

- Record for each image what its source directory is, what its build context is, and how
  it is tagged. An image whose build context is the repo root (because the Dockerfile
  copies `pyproject.toml`, the lockfile, and `src/`) fails confusingly when built from
  its own directory.
- Build and push through a task, never by hand.
- Pin a tag. `latest` in a cluster means nobody can say what is running.

## Gotchas

Keep a short list of the failures this repo has actually hit, with the fix, for example a
stale volume claim after redeploying a database, an image that is not in the local
container runtime's cache, or a load balancer that has to be released before the
infrastructure can be destroyed. Each entry should be one line of symptom and one line of
cause, and it earns its place only after someone has lost an afternoon to it.
