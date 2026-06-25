---
name: build-dashboard
description: Build a dashboard from governed MarcoPolo data. Use when the user asks for a dashboard, visualization, live artifact, remote artifact, explorable report, or runnable dashboard app backed by MarcoPolo connections.
---

# Build Dashboard

Build a dashboard that gets data through MarcoPolo MCP tools. Support both:

- Cowork: prefer a Remote Artifact that calls the MarcoPolo MCP connection.
- Non-Cowork: generate runnable code that calls the same MCP tools through the
  host or server runtime using a MarcoPolo developer API token.

## Compatibility

Prefer product MCP data tools when the current session exposes them:

- `connections_list`
- `data_query`

Older agent sessions may expose only `workspace_shell`. In those sessions, use
the compatibility path for agent-side work:

- `workspace_shell("connection list --json")`
- `workspace_shell("connection query <name> --inline '<sql>' --sample-rows <n> --json")`
- `workspace_shell("connection query <name> --file <workspace-relative-query-file> --sample-rows <n> --json")`

Treat shell query results as CLI envelopes, not `data_query` payloads.
Normalize them before reasoning over rows:

- rows from `data`, otherwise `preview`
- `row_count` from `row_count`, otherwise `len(rows)`
- `run_id` if present
- `relation_name` if present

Do not teach generated dashboards, Remote Artifacts, or external app code to
call `workspace_shell`. When the product surface exposes `data_query`, runtime
dashboard data access should target `data_query`.

## Inputs

Get the minimum missing details:

- Goal and audience.
- Connection or data domain.
- Metrics, filters, time range, and row limits.
- Output target: Cowork Remote Artifact or runnable code.
- Freshness: live query, reusable query file, or materialized result.

Do not ask for raw datasource credentials in chat. If connection access is
missing, hand off to the connection setup or sharing flow. For non-Cowork
runnable code, use a MarcoPolo developer API token supplied by the user's host
or runtime environment, not an endpoint or token entered into the dashboard UI.

## Data Contract

Use:

- `connections_list` to discover visible connections.
- `data_query` to fetch bounded dashboard data.

`data_query` requires exactly one query source:

- `query`: inline query text. Prefer this for generated apps and short artifact
  bindings.
- `query_file`: workspace-relative query file path. Use this when a reusable
  query already exists or the LLM intentionally authored one.

Always include `connection_name`, `max_rows`, and optional `params`.

## Workflow

1. Discover visible connections with `connections_list` when available. If the
   tool is unavailable in the current session, use the compatibility fallback
   `workspace_shell("connection list --json")`.
2. Pick bounded datasets: prefer aggregates, explicit filters, and `LIMIT`.
3. Use inline `query` unless a reusable workspace query file is clearly useful.
4. Build the dashboard with loading, empty, permission-error, and query-error
   states.
5. Keep raw datasource credentials out of the artifact or code.
6. Verify each `data_query` call returns the expected columns and row counts.
7. If the session lacks `data_query`, use bounded `workspace_shell("connection query ... --json")`
   probes for agent-side validation only. Do not convert that shell path into
   the runtime contract for generated artifacts.

Use `workspace_shell` only for workspace authoring or debugging, such as
creating a query file, probing query behavior, using DuckDB, or inspecting
metadata when needed. Do not make the runtime dashboard fetch data through
`workspace_shell`.

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
      "query": "select week, sum(revenue) as revenue from revenue group by week order by week limit 12",
      "max_rows": 500
    }
  }
}
```

For non-Cowork, generate runnable code for the user's chosen host, framework,
or local environment. The generated app should behave like a remote artifact:

- Browser UI calls only the app's own routes or server functions.
- Server-side or host code calls the MarcoPolo MCP server using JSON-RPC
  `tools/call` with `name: "data_query"`.
- Read the MCP server URL and MarcoPolo developer API token from environment or
  host context, such as `MARCOPOLO_MCP_URL` and `MARCOPOLO_API_TOKEN`.
- Send the token as `Authorization: Bearer <token>` from server-side or host
  code only.
- Do not add endpoint fields, token fields, or alternate transport choices to
  the dashboard UI.
- Do not create a browser-only live dashboard unless the target host explicitly
  provides a safe server-side MCP calling bridge.

The developer token is the current non-Cowork auth model. Keep it out of client
bundles and logs, and fail with a clear configuration error when it is missing.

In the final response, include the output location, data sources, `data_query`
bindings, freshness model, and validation result.
