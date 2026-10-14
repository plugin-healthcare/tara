# Remote catalog registry: draft for review

Date: 2026-10-02
Status: posted as #42.

## Question

Should Tara's catalog (instructions, agents, prompts, skills, hooks, MCP entries, and templates) move from `src/tara/data/` to a registry folder in the repository that Tara fetches from GitHub, instead of shipping it inside the package?

## Motivation

- The catalog can grow and update without a package release.
- The package stays small.
- Tara's own content uses the same import route as third-party skills: reference it, pin it in the lock, and restore it on demand.
- A registry with its own CI can enforce size and token budgets on every skill, which addresses the bloat in many published skills.

The catalog is 196 KB in 45 files today, so the gain is mainly the release cadence and not the package size.

## Proposed shape

- A top-level `registry/` folder in this repository with the current `src/tara/data/catalog/`, `skills/index.toml`, and `mcp/catalog.toml` content, plus a `registry.toml` with a format version.
- Tara resolves the registry at a pinned ref (a `registry-v<N>` tag or a commit), records the commit in `.tara/skills.lock` or a new `.tara/registry.lock`, and caches fetched content under the user cache directory.
- A small core stays bundled in the package: base instructions, config templates, and standards scaffolding, so `tara init` works offline.

## One index for Tara and external content

The registry lists sources, and Tara's own content is one source among the external ones.
An external entry holds only a repository, a folder, and a ref, and its content is never copied into the registry.
Every source other than Tara's own is labelled as external, with its repository and license, wherever users see it.
Users browse every source in the same way with `tara skill list` and pick skills with `tara skill add`, as described in draft E.
The skills in a source come from its own folder structure at a pinned commit, so the registry does not curate members of external repositories.

## Problems to solve

| Topic | Risk | Direction |
| ----- | ---- | --------- |
| Offline use | Healthcare environments often have restricted network access, so `tara init` must not fail without GitHub. | Bundle the core, cache fetched content, and fall back to the cache with a clear warning. |
| Compatibility | An older Tara version reading a newer registry from `main` can break. | Pin a ref per Tara version or per repository, and check `registry.toml`'s format version. |
| Ownership checks | `_matches_catalog_source` (`src/tara/cli.py:1108`) proves ownership by comparing against the bundled copy, which would no longer exist. | Store a content hash per installed artifact in the lock and compare against that. |
| Supply chain | Hooks run code on the user's machine, and MCP entries start processes. | Fetch only pinned commits and never a branch head. Consider signed tags for registry releases. |
| Access | GitHub rate limits, enterprise proxies, and forks. | Use `gh` or a token when one is available, and allow an override of the registry URL in `.tara/config.toml`. |
| Testing | Package tests currently read the bundled catalog. | Use a local registry fixture in tests, and validate the registry itself in its own CI job (with #36). |

## Timing

The lock format and config schema are the public surface that 2.0.0 should keep stable.
Proposal: decide the ADR before 2.0.0 and add only the schema parts (registry ref, content hashes in the lock).
Implement remote fetching in 2.x, with the bundled catalog kept as the fallback so the change is not breaking.

## Spike scope (timebox 2 days)

1. Prototype fetching `registry/` at a pinned commit with a cache and an offline fallback.
2. Replace the ownership comparison with lock content hashes for one artifact kind.
3. Measure the time `tara init` takes with a cold and a warm cache.
4. Write the ADR with the decision and the migration path for existing `.tara/config.toml` files.

## Open questions

1. Registry in this repository (atomic pull requests with CLI changes) or a separate `tara-registry` repository (independent release cadence)?
2. Which content stays bundled as the offline core?
3. Should the size and token budget in the registry CI be a hard limit or a warning?
