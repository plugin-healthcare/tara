---
applyTo: "**/assets/**/*.py,**/definitions.py,**/resources/**/*.py,**/io/**/*.py"
description: "Dagster conventions for assets, definitions, IO managers, and run configuration."
---

# Dagster conventions

For the Dagster API itself (asset selection, the `dg` CLI, component structure), use the
`dagster-expert` skill. This file covers the conventions a repo has to agree on, which
the API cannot enforce. Adjust the placeholder paths to your layout.

## Runtime shape

Dagster runs as several processes, not one script, so anything you write has to survive
being loaded in isolation:

- Webserver: UI and GraphQL API, stateless, horizontally scalable.
- Daemon: schedules, sensors, and the run queue. Single instance.
- User code server: the gRPC process that loads your definitions. One or more per
  project.

PostgreSQL holds run history, event logs, schedules, and asset metadata. Treat it as
critical state: back it up, and never drop its volume without knowing what you lose.

## Assets

- Annotate returns (`Output[pl.DataFrame]`, `Output[str]`); an unannotated asset gives
  the IO manager nothing to dispatch on.
- Register the default IO manager under the `"io_manager"` key so it applies to every
  asset. An asset that cannot produce the default type opts out visibly with its own
  `io_manager_key`, rather than every other asset opting in.
- `defs = Definitions(...)` is the only top-level export in `definitions.py`.
- Keep asset bodies thin: they wire inputs to a function in the library package, so the
  transformation stays testable without Dagster.

## Run configuration

- Import shared execution profiles (Kubernetes resources, image, env) from one module,
  for example `<package>.resources.k8s`. Never redefine them inline per asset, or the
  cluster's actual resource story lives in a dozen places.
- Give run priorities a documented scheme instead of ad-hoc numbers, for example a fast
  lane at 5, default at 0, background at -1, and backfill at -2. Queue behaviour is
  invisible in the code, so it has to be written down.

## Project structure

- Reusable platform code (IO managers, resources, base patterns) lives in the library
  package (`src/<package>/`), not in a project directory.
- Per-project assets live with their project (`projects/<name>/src/etl/assets/`), loaded
  by module (`-m etl.definitions`).
- Add a project by copying the example project and renaming, so every project keeps the
  same shape.
