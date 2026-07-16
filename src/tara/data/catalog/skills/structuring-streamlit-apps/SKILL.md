---
name: structuring-streamlit-apps
description: "Use when creating or structuring a Streamlit application: the entrypoint, the multipage pages/ folder, .streamlit/config.toml, dependencies via uv, and keeping business logic testable and separate from the UI. Applies Tara's Python conventions on top of uv init."
---

# Structuring Streamlit apps

The canonical layout for a Streamlit application: one entrypoint, a `pages/` folder
for extra pages, config under `.streamlit/`, and business logic pulled out of the UI
so it can be tested without a running app.

## Create it with uv

Start the project and add Streamlit as a dependency:

```
uv init --app <name>
cd <name>
uv add streamlit
```

Then arrange the layout below and run it with `uv run streamlit run app.py`.

## Canonical layout

```
<name>/
  pyproject.toml
  app.py                  # entrypoint: `streamlit run app.py`
  pages/
    views/                # page views: GLUE ONLY. compose components + backend.
      1_overview.py
      2_details.py
  components/             # reusable front-end pieces and plot builders
    __init__.py
    charts.py             # plots: take data, return a figure/chart
    widgets.py            # reusable UI components
  backend/                # data retrieval + calculations: pure, no st.* calls
    __init__.py
    data.py               # loading, querying, transforms
    compute.py            # calculations, business logic
  .streamlit/
    config.toml           # theme + server settings
  tests/
    test_backend.py       # tests target backend/, not the views
  data/                   # sample data so the app runs out of the box
```

## The three layers: views glue, components render, backend computes

**Never build logic or components inside `pages/views`.** A view exists only to glue
things together: read the user's inputs, call `backend` for the data and numbers,
pass them to a `components` function to render, and lay it out with `st.*`. That is
all a view does.

- **`backend/`**: data retrieval and calculations. Pure, typed functions with no
  `st.*` calls and no plotting. This is the logic layer, and it is where the real
  work lives.
- **`components/`**: reusable front-end pieces and plots. A plot function takes data
  (from `backend`) and returns a figure or chart; a component renders a reusable bit
  of UI. Keep data fetching and business rules out of here, that is `backend`'s job.
- **`pages/views/`**: glue only. No transforms, no computations, no inline
  components. If you are writing one in a view file, it belongs in `backend` (logic)
  or `components` (UI/plot).

Why: a view with logic or components baked in cannot be tested and cannot be reused.
When calculations sit in `backend/` you unit test them with `pytest` and no running
app; when plots and widgets sit in `components/` any view (or another app) can reuse
them.

- Cache expensive calls with `@st.cache_data` / `@st.cache_resource` at the view
  boundary, not inside the pure `backend/` functions.
- Multipage: files under `pages/views/` become sidebar entries automatically; prefix
  with a number to order them.
- `.streamlit/config.toml` holds theme and server config; do not hardcode it.

## Conventions

- Follow `.github/instructions/python.instructions.md` (type hints, `pathlib`,
  `logging` not `print`, ruff).
- Ship sample data in `data/` so `uv run streamlit run app.py` works immediately.
- Test `backend/` with `uv run pytest`; run the app to verify the views.

Never commit; the developer reviews and commits. You scaffold and arrange the files.
