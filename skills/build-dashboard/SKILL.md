---
name: build-dashboard
description: Build a dashboard from governed MarcoPolo data. Use when the user asks for a dashboard, visualization, live artifact, remote artifact, explorable report, or runnable dashboard app backed by MarcoPolo connections.
---

# Build Dashboard

Build a dashboard that gets data through MarcoPolo MCP tools. Support both:

- Cowork: prefer a Remote Artifact that calls the MarcoPolo MCP connection.
- Non-Cowork: generate runnable code that calls the same MCP tools through the
  host/server runtime using a MarcoPolo developer API token.

## Inputs

Get the minimum missing details:

- Goal and audience.
- Connection or data domain.
- Metrics, filters, time range, and row limits.
- Output target: Cowork Remote Artifact or runnable code.
- **Freshness: will this re-query live data at view/load time, or is a snapshot sufficient?**
  - Live query at view time (Remote Artifact, external app, scheduled script) → use `data_query`
  - One-off snapshot or report → embed the already-queried data inline; `data_query` not needed

Do not ask for raw datasource credentials in chat. If connection access is
missing, hand off to the connection setup/sharing flow. For non-Cowork runnable
code, use a MarcoPolo developer API token supplied by the user's host/runtime
environment, not an endpoint or token entered into the dashboard UI.

## Session capability detection

Only applies when building a **live-querying artifact** (one that re-queries at view or load time).
For one-off snapshots, embed the data inline — no MCP tool needed at runtime.

When building a live-querying artifact, check which tools the session exposes:

- Sessions with `connections_list` and `data_query` (Claude, Cursor, etc.):
  Use `data_query` for all live runtime queries in generated artifacts and apps.
- Sessions with only `workspace_shell` (ChatGPT, older sessions):
  Use bounded `workspace_shell("connection query <name> --file <file> --sample-rows <n> --json")`
  for discovery and probing. Generated code for these sessions should use the
  same `workspace_shell` query path with small `--sample-rows`, noting it can be
  upgraded to `data_query` when the session gains that tool.

## Data Contract

For live-querying artifacts, use:

- `connections_list` to discover visible connections.
- `data_query` to perform bounded live queries at view or load time.

`data_query` requires a workspace-relative query file:

- `query_file`: workspace-relative query file path under
  `connections/<connection>/queries/`.

Before calling `data_query`, author a named query file with `workspace_shell` or
reuse an existing query file. Pick a business-readable filename such as
`weekly_revenue.sql`, `latest_errors.json`, or `metric_rollup.yaml`, using the
extension appropriate for the connection's query language.

Always include `connection_name`, `max_rows`, and optional `params`.

## Workflow

1. Discover visible connections with `connections_list`.
2. Pick bounded datasets: prefer aggregates, explicit filters, and `LIMIT`.
3. Create or reuse query files under `connections/<connection>/queries/`.
4. Build the dashboard with loading, empty, permission-error, and query-error
   states.
5. Keep raw datasource credentials out of the artifact/code.
6. Verify each `data_query` call returns the expected columns and row counts.

Use `workspace_shell` only for workspace authoring/debugging, such as creating a
query file, probing query behavior, using DuckDB, or inspecting metadata when
needed. Do not make the dashboard fetch data through `workspace_shell`.

## Output Guidance

For Cowork, produce the Remote Artifact shape or instructions the host expects,
with dataset bindings that call:

```json
{
  "method": "tools/call",
  "params": {
    "name": "data_query",
    "arguments": {
      "connection_name": "SALES",
      "query_file": "connections/SALES/queries/weekly_revenue.sql",
      "max_rows": 500
    }
  }
}
```

For non-Cowork, generate runnable code for the user's chosen host, framework, or
local environment. The generated app should behave like a remote artifact:

- Browser UI calls only the app's own routes or server functions.
- Server-side/host code calls the MarcoPolo MCP server using JSON-RPC
  `tools/call` with `name: "data_query"`.
- Read the MCP server URL and MarcoPolo developer API token from environment or
  host context, such as `MARCOPOLO_MCP_URL` and `MARCOPOLO_API_TOKEN`.
- Send the token as `Authorization: Bearer <token>` from server-side/host code
  only.
- Do not add endpoint fields, token fields, or alternate transport choices to
  the dashboard UI.
- Do not create a browser-only live dashboard unless the target host explicitly
  provides a safe server-side MCP calling bridge.

The developer token is the current non-Cowork auth model. Keep it out of client
bundles and logs, and fail with a clear configuration error when it is missing.

In the final response, include the output location, data sources, `data_query`
bindings, freshness model, and validation result.
