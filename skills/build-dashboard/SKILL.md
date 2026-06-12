---
name: build-dashboard
description: Build a dashboard from governed Marcopolo data. Use when the user asks for a dashboard, visualization, insight, live artifact, remote artifact, explorable report, or runnable dashboard app backed by Marcopolo connections.
---

# Build Dashboard

Build a visualization backed by Marcopolo data. First determine whether the
user needs:

- a transient inline visualization for the current conversation
- a persistent dashboard or app that can be revisited, refreshed, or shared

Do not assume the current assistant or runtime supports a native live-artifact
surface, browser-executable tool bridge, local app execution, or code hosting.
Infer capabilities from observable behavior and available tools. If the
environment is ambiguous, ask the user which deliverable they want instead of
guessing.

## Output Modes

### `inline_snapshot`

Use this mode when the user wants a quick chart, comparison, summary, or visual
explanation in the current conversation.

Properties:

- one-off
- embedded snapshot data
- no live refresh
- no persistent asset required

### `host_native_live_artifact`

Use this mode only when the current environment already provides a persistent
interactive artifact surface with built-in authenticated tool access to
Marcopolo.

Properties:

- live data on refresh
- revisitable in the host
- possibly shareable through the host

Rules:

- use the host's existing artifact or tool-binding contract only
- rely on the host's existing auth or session flow
- do not invent custom API bridges, browser-only Marcopolo access, or
  undocumented runtime globals

### `local_runnable_app`

Use this mode when the environment can generate and run a full-stack app on the
user's machine, or when the user explicitly wants a local live app.

Properties:

- browser UI plus server-side backend
- Marcopolo API token stays server-side
- live data fetched on demand
- local execution, not inherently shareable

### `code_only_app`

Use this mode when the environment can generate code but cannot reliably run or
host it for the user.

Properties:

- generated full-stack app source
- user must configure env vars and run it
- best suited to technical users

## Capability Check

Before building a persistent dashboard, determine which capabilities are
actually available:

- Can the environment render a persistent interactive artifact with native tool bindings?
- Can the environment run local files or processes and preview a web app?
- Can the environment only generate code but not execute it?
- Can the environment only display inline chat visuals?

If these capabilities are not clear from visible tools or host behavior, do not guess. Ask the user to choose one of:

- quick inline chart
- persistent live dashboard in the current environment
- local runnable app
- code only

## Defaults

- If the user asks for a chart or visualization without asking for persistence, use `inline_snapshot`.
- If the user asks for something reusable, refreshable, or shareable and the
  host-native live-artifact capability is clearly available, use  `host_native_live_artifact`.
- If the user asks for a live app and local code execution is available, use
  `local_runnable_app`.
- If the user asks for a live app but only code generation is available, use
  `code_only_app`.
- If no supported live runtime exists, do not fake one. Fall back to
  `inline_snapshot` or a static artifact, or explain the limitation clearly.

## Inputs

Get the minimum missing details:

- Goal and audience.
- Connection or data domain.
- Metrics, filters, time range, and row limits.
- Desired output mode, if the user's request does not make it clear.
- Freshness: live query, reusable query file, or materialized result.

Do not ask for raw datasource credentials in chat. If connection access is
missing, hand off to the connection setup or sharing flow. For generated live
apps, use a Marcopolo developer API token supplied by the runtime environment,
not an endpoint or token entered into the dashboard UI.

## Data Contract

Use:

- `connections_list` to discover visible connections.
- `data_query` to fetch bounded dashboard data.

Treat `data_query` results as an envelope object, not a bare row array. The
canonical shape is `{ rows: [...] }`, typically alongside fields such as
`success`. Host runtimes that call Marcopolo through MCP may wrap that result
one level deeper before generated code sees it. Normalize the tool result into
a plain `rows[]` array before iterating, charting, or rendering.

`data_query` requires exactly one query source:

- `query`: inline query text. Prefer this for generated apps and short artifact
  bindings.
- `query_file`: workspace-relative query file path. Use this when a reusable
  query already exists or the LLM intentionally authored one.

Always include `connection_name`, `max_rows`, and optional `params`.

## Workflow

1. Classify the request into one of the output modes before building.
2. Discover visible connections with `connections_list`.
3. Pick bounded datasets: prefer aggregates, explicit filters, and `LIMIT`.
4. Use inline `query` unless a reusable workspace query file is clearly useful.
5. Normalize each `data_query` result into a plain `rows[]` array before
   passing data into tables, chart components, or row iteration.
6. Build loading, empty, permission-error, and query-error states.
7. Keep raw datasource credentials out of the artifact or generated code.
8. Verify the raw tool-result shape first, then verify the normalized rows
   return the expected columns and row counts.
9. Match the output packaging to the environment's actual capabilities instead
   of assuming a live-artifact surface, MarcoPolo API bridge, or browser-only
   live fetch path.

Use `workspace_shell(...)` only for workspace authoring or debugging, such as
creating a query file, probing query behavior, using DuckDB, or inspecting
metadata when needed. Do not make runtime dashboards fetch data through
`workspace_shell(...)`.

## Mode Guidance

### `inline_snapshot`

- query bounded data
- embed only the data needed for the visualization
- clearly present the result as a snapshot, not a live dashboard
- prefer this mode for casual exploratory analysis

### `host_native_live_artifact`

If the current environment exposes a native artifact or tool-binding surface,
produce the shape that environment expects, with dataset bindings that call:

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

Rules:

- use only the runtime or tool-binding mechanism the current host already
  exposes
- rely on host-provided auth or session flow
- do not embed datasource credentials or Marcopolo API tokens in client code
- do not generate arbitrary HTML that assumes an undocumented browser bridge
  exists

### `local_runnable_app`

Use this mode when the environment can run local code and the user wants a live app they can open in a browser.

Rules:

- browser UI must call only the app's own server routes or server functions
- server-side code calls the Marcopolo MCP server using JSON-RPC `tools/call`
  with `name: "data_query"`
- read `MARCOPOLO_MCP_URL` and `MARCOPOLO_API_TOKEN` from environment
- send `Authorization: Bearer <token>` from server-side code only
- keep the token out of client bundles and logs
- do not invent new Marcopolo API routes, bridge endpoints, or alternate
  transport contracts

### `code_only_app`

Use the same architecture as `local_runnable_app`, but deliver code plus clear
run instructions instead of assuming the environment can execute it.

Rules:

- state exactly which environment variables the user must configure
- state how to start the server
- make it clear that the result is live only after the user runs the app

If the environment supports neither native tool binding nor an existing
server-backed live path, fall back to a static artifact backed by a
materialized query result and state that freshness is snapshot-based.

## Generated App Guidance

Generated code should include a small normalization layer between the MCP tool
result and the visualization:

- if the parsed result is already an array, use it
- else if it has `rows` and `rows` is an array, use `result.rows`
- else if it has `data.rows` and that is an array, use `result.data.rows`
- else fail with a clear error that includes the unexpected response shape

Do not assume the parsed MCP response is directly iterable.

## Final Response

Always include:

- which output mode was chosen
- whether the result is live or snapshot-based
- what runtime assumptions were used
- whether the output is shareable
- output location or code location
- data sources and `data_query` bindings
- freshness model
- validation result
