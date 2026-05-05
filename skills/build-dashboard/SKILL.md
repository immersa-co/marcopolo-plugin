---
name: build-dashboard
description: Authors dashboard artifacts in the MarcoPolo workspace — a `.dashboard` manifest plus a `view.tsx` React component, previewed via the `preview_dashboard` MCP tool. Use this skill whenever the user wants any durable visual output — charts, dashboards, plots, graphs, visualizations, reports — even if they say "just show me a chart" or "plot this" without using the word "dashboard". Also use when iterating on the look of an existing dashboard or wiring up a new dataset.
---

# Build a dashboard

A dashboard is the right surface when the user wants a durable visual
artifact they can refine during design and view again later. The
in-workspace canonical reference is `/workspace/workflows/build-dashboard.md`.

## Authoring contract

A dashboard is two files under `artifacts/dashboards/`:

- `<name>.dashboard` — a JSON manifest declaring metadata and named DuckDB
  datasets
- `view.tsx` (or `shared/view.tsx`) — a React component that renders the data

The split exists for a reason: the manifest is the trusted authoring surface
and the only thing `preview_dashboard` looks at. MarcoPolo resolves the
manifest's `datasets` against DuckDB and passes the results in as the `data`
prop on the React component. That separation keeps `view.tsx` pure
presentation, makes the data dependencies inspectable, and lets the same
view re-render against fresh data without code changes.

Practical implications:

- The manifest has the `.dashboard` extension. Other extensions are not
  picked up by `preview_dashboard`.
- The manifest points at a relative React view file (commonly `view.tsx`
  next to it).
- Datasets are declared in the manifest. Don't fetch or query inside
  `view.tsx` — there's no assistant or workspace context at render time.
- `view.tsx` exports a default React component that takes `{ data,
  metadata }`.
- Use only `react` and `recharts` imports unless the workspace's `RULES.md`
  explicitly allows others — other libraries may not be available in the
  preview environment.
- Preview and share through the manifest, not through `view.tsx` directly.

## Templates

Two starter files live alongside this skill:

- `assets/dashboard.template.json` — the `.dashboard` manifest shape
- `assets/view.template.tsx` — a minimal React view component using
  `recharts`

Read them when authoring and adapt rather than reinvent.

## Authoring workflow

1. **Make the data queryable through DUCKDB first.**
   Dashboards resolve datasets against DuckDB, so the manifest's `query`
   field has to run cleanly there. For results from upstream connections,
   run `connection query <name> --file ...` first — each materializes a
   DuckDB relation you can then reference in the manifest. See
   `query-and-analyze` for the full flow.

2. **Create `artifacts/dashboards/` and write the manifest.**

   ```
   workspace_shell("mkdir -p artifacts/dashboards")
   workspace_shell("""cat > artifacts/dashboards/<name>.dashboard <<'JSON'
   {
     "version": 1,
     "name": "<name>",
     "title": "<Title>",
     "view": "view.tsx",
     "datasets": {
       "<dataset_key>": {
         "source": "duckdb",
         "query": "<sql>"
       }
     }
   }
   JSON""")
   ```

3. **Write `view.tsx` next to the manifest.**

   ```
   workspace_shell("""cat > artifacts/dashboards/view.tsx <<'TSX'
   import React from "react";
   import { ... } from "recharts";

   export default function Dashboard({ data, metadata }) {
     return (...);
   }
   TSX""")
   ```

   Reference dataset keys you declared in the manifest (e.g.,
   `data.<dataset_key>`). Every key the view reads from `data` must appear
   in the manifest's `datasets`.

4. **Preview through the MCP tool.**

   ```
   preview_dashboard(path="artifacts/dashboards/<name>.dashboard")
   ```

   This opens the interactive preview UI, resolves manifest datasets
   through DuckDB, and renders `view.tsx` with the results.

5. **Iterate the same artifact.**
   Edit the existing `view.tsx` rather than creating variants — the user
   wants one durable dashboard, not many. Update the manifest when the
   dashboard's data needs change. If the user explicitly asks for
   alternatives (e.g., "show me a line chart version"), then create a
   second manifest.

## Design guidance

- **Move data shaping upstream.** SQL in the manifest, saved DUCKDB
  queries under `connections/DUCKDB/queries/`, or scripts under `scripts/`
  are all easier to reason about, test, and reuse than logic inside
  `view.tsx`. Reach for the view only for layout and presentation.
- **Recurring refresh logic doesn't belong here.** A dashboard renders
  whatever data exists when you preview it. To keep the data fresh on a
  schedule, see `setup-automation` — it runs the upstream queries in the
  background.
- **Read the workspace's top-level `RULES.md`** before authoring. It may
  define visual conventions, allowed libraries, or naming rules for
  artifacts that override the defaults here.

## Common pitfalls

- **Querying inside the component.** The view receives data via the
  `data` prop. There's no assistant, no `connection`, no DuckDB at render
  time — only what the manifest resolved.
- **Mismatched dataset keys.** If `view.tsx` reads `data.foo` but the
  manifest declares `bar`, the view sees `undefined`. Keys must match.
- **Wrong manifest extension.** `preview_dashboard` only matches files
  ending in `.dashboard`.
- **Importing beyond `react` and `recharts`.** The preview environment
  may not have your library. Stick to those two unless `RULES.md` says
  otherwise.

## Pointers

- producing the upstream DuckDB relations → `query-and-analyze`
- per-verb flag reference → `using-connection-cli`
- scheduling a recurring refresh of the underlying data → `setup-automation`
- workspace layout (where `artifacts/dashboards/` sits) → `using-marcopolo-workspace`
