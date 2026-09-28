# `connection query`

```
workspace_shell("connection query <name> --file <query-file> [--params-json <json>] [--include-results] --json")
```

Execute a saved query file against a connection.

## Why file-based, not inline

`--file` requires an existing workspace file, not inline SQL. This is
deliberate: query files in `connections/<name>/queries/` become a durable
record of what was run, get committed alongside the rest of the workspace,
can be reused by scheduled jobs, and let the user see and edit the SQL
without round-tripping through the assistant. Inline SQL would be invisible after
the call returned.

For provider-specific operations that aren't expressible as a SQL file
(some storage browsers, custom RPC calls), use `--op-json <json>` instead
of `--file`.

## Flags

- `--file <query-file>` — workspace-relative or absolute path to an
  existing query file. Convention is
  `connections/<name>/queries/<file>`.
- `--op-json <json>` — provider-specific operation payload (alternative
  to `--file`).
- `--params-json <json>` — JSON object of parameter values for parameterized
  queries.
- `--input-data <data>` — input bytes for queries that need them.
- `--include-results` — also return the result rows in `data`. By default
  (without this flag) a query returns only the DuckDB relation handle
  (`relation_name` + `row_count` + `column_count`), not the rows, so a large
  result never floods the context window. Pass this when you need the rows
  inline, and add a SQL `LIMIT` for large results. Inline rows are capped at
  1 MiB: past that the response returns the first rows that fit and sets
  `data_truncated` (see below).

  For aggregations or large result sets, prefer a DuckDB follow-up over
  `--include-results`. To hand a large result to the user, export from DuckDB to
  CSV in `/workspace/data/downloads/` for retrieval from the web UI:

  ```sql
  COPY (SELECT * FROM <relation_name>) TO '/workspace/data/downloads/<file>.csv' (HEADER, DELIMITER ',');
  ```

  Run via `workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/export.sql --json")`.
- `--json` — always pass.

## Path semantics

`--file` paths are resolved from the workspace root (`/workspace`),
**regardless of the shell's current working directory**. `cd`-ing into a
connection directory does NOT change resolution.

- ✅ Always use the full workspace-relative form:
  `connections/<name>/queries/<file>`
- ✅ Absolute paths under `/workspace` also work.
- ❌ Do NOT use a bare `queries/<file>` path. It resolves to
  `/workspace/queries/<file>`, not the connection's queries directory, and
  fails with `No such file or directory` even if you just created the file
  via `cd <connection-dir> && cat > queries/<file>`.

```bash
# WRONG — resolves to /workspace/queries/foo.json
cd connections/<name> && connection query <name> --file queries/foo.json --json

# RIGHT
connection query <name> --file connections/<name>/queries/foo.json --json
```

## Response shape

`connection query --json` returns an envelope. Key fields:

| Field | Type | Meaning |
|---|---|---|
| `success` | bool | Whether the query ran |
| `row_count` | int | Total rows in the full result (materialized in DuckDB) |
| `rows` | int | Duplicate of `row_count` — **NOT a list of records**. Ignore it. |
| `data` | **string** | JSON-encoded array of the result rows. **Must be `json.loads`-ed before use.** Present only when `--include-results` was passed. |
| `data_truncated` | object | Present only when `data` was cut at the 1 MiB inline cap: `{rows_returned, row_count}`. The full result is still in `relation_name`; `next_actions` has a ready-to-run DuckDB command for the next page. |
| `relation_name` | string | DuckDB relation holding the full result set |
| `column_count` | int | Number of columns in the result |
| `run_id`, `query_file`, `execution_time`, `next_actions` | — | Run metadata |

### Reading rows from the envelope

`data` is a **string**, not a native array. Parse it before use:

```python
import json
resp = json.loads(result["stdout"])             # the CLI envelope is workspace_shell's stdout
records = json.loads(resp["data"])              # parse data string → list[dict]
# len(records) is the number of rows returned
```

Common mistakes:
- `len(resp["data"])` counts **characters**, not rows.
- `resp["rows"]` is an **int**, not a record list — do not iterate it.
- Iterating `resp["data"]` without parsing yields characters →
  `'str' object has no attribute 'get'`.

### Prefer DuckDB for anything beyond a quick look

For aggregations, joins, group-bys, or totals, do not parse a large
`data` payload and aggregate in Python. The full result is already in DuckDB as
`relation_name` (the default response), so run a follow-up DuckDB query against
it instead:

```
workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<followup>.sql --json")
```

The DuckDB SQL can reference the materialized `relation_name` directly —
no need to re-run the upstream query. Reserve `data` parsing for small
results and display.

## Timeout

`connection query` runs via `workspace_shell`. `timeout` is how long the call
waits (default 30s, max 300s). The default is enough for simple queries; pass a
larger value for queries on large datasets or slow connections (60–120s) and
for `connection describe` (30–60s).

```text
workspace_shell("connection query <name> --file ... --json", timeout=90)
```

A command still running when `timeout` ends comes back with
`status: "running"` and an `execution_id`, and keeps running for up to 300s in
total. Check it with:

```text
workspace_shell("execution status <execution_id>")
```

The record shows `status` (`running`, `succeeded`, `failed`), the
`failure.kind` (`timed_out`, `lost`, `command_failed`), and the tails of
stdout/stderr. A workspace runs one such background command at a time: while
one is running, another command that outlives its `timeout` is stopped and the
response names the execution holding the slot — wait for it, then retry.

## When `query` fails

Common causes:

- query file doesn't exist or path is wrong → check with `ls`
- SQL syntax doesn't match the connection's dialect → read
  `connections/<name>/SYNTAX.md`
- references a table/column that no longer exists → re-run
  `connection describe <name>` and update the query
- credentials issue → run `connection test <name>` to confirm
- `data_truncated` present → not a failure; the rows beyond the 1 MiB cap are
  in `relation_name`. Aggregate or filter there rather than paging through them
- `status: "running"` → check it with `execution status <execution_id>`
  instead of re-running it
- `failure.kind: "timed_out"` → it hit the 300s limit, or the background slot
  was taken; narrow the query or wait for the running execution
