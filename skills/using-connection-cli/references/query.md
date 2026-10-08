# `connection query`

MCP tool: `connection_query(connection_name, query_file=None, operation=None, params=None, input_data=None, include_results=False, timeout=None)`. It runs this CLI verb with `--json` and returns the result shape of `workspace_shell`; the CLI envelope is `stdout`. The CLI form below also works inside `workspace_shell`, for example in scripts and cron jobs. Tool arguments map to the flags: `query_file` is `--file`, `operation` is `--op-json`, `params` is `--params-json`, `input_data` is `--input-data`, and `include_results` is `--include-results`.

```
connection query <name> --file <query-file> [--params-json <json>] [--include-results] --json
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

  Run via `connection_query(connection_name="DUCKDB", query_file="connections/DUCKDB/queries/export.sql")`.
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
| `data_truncated` | object | Present only when `data` was cut at the 1 MiB inline cap: `{rows_returned, row_count}`. The full result is still in `relation_name`, and `next_actions` has a DuckDB command for the next page. If `rows_returned` is 0, one row alone exceeds the cap: select fewer or narrower columns. |
| `relation_name` | string | DuckDB relation holding the full result set |
| `column_count` | int | Number of columns in the result |
| `run_id`, `query_file`, `execution_time`, `next_actions` | — | Run metadata |

### Reading rows from the envelope

`data` is a **string**, not a native array. Parse it before use:

```python
import json
resp = json.loads(result["stdout"])             # the CLI envelope is the tool result's stdout
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
connection_query(connection_name="DUCKDB", query_file="connections/DUCKDB/queries/<followup>.sql")
```

The DuckDB SQL can reference the materialized `relation_name` directly —
no need to re-run the upstream query. Reserve `data` parsing for small
results and display.

## Timeout

`connection_query` (like `workspace_shell`) takes a `timeout`: the longest the
call waits (default 30s, max 300s); the call returns as soon as the command
finishes, so a generous value costs nothing on a fast query. The default suits
simple queries. For large datasets or slow connections pass 120–300 so the
result comes back in the same call; use 30–60 for `connection_describe`.

```text
connection_query(connection_name="<name>", query_file="connections/<name>/queries/<file>", timeout=180)
```

A command still running when `timeout` ends comes back with
`status: "running"` and an `execution_id`, and keeps running for up to 300s in
total. Do not re-run it. `execution_status(execution_id)` answers immediately
with the current record, so wait before you check rather than polling in a
tight loop:

```text
execution_status(execution_id="<execution_id>")
```

The record carries `status` (`running`, `succeeded`, `failed`),
`failure` (`{kind, message}` or null), and `outcome` with `exit_code`,
`stdout_tail`, and `stderr_tail`. The finished command's CLI envelope is the
`outcome.stdout_tail` string, one level deeper than a query that finished
within its call:

```python
resp = json.loads(record["outcome"]["stdout_tail"])   # the connection query envelope
```

A workspace has one background slot. Commands that finish within their
`timeout` still run while it is taken, but another command that outlives its
`timeout` is stopped with `failure.kind: "timed_out"`, and the message names
the execution holding the slot.

## When `query` fails

Common causes:

- query file doesn't exist or path is wrong → check with `ls`
- SQL syntax doesn't match the connection's dialect → read
  `connections/<name>/SYNTAX.md`
- references a table/column that no longer exists → re-run
  `connection describe <name>` and update the query
- credentials issue → run `connection test <name>` to confirm
- `failure.kind: "command_failed"` → the CLI exited non-zero. The reason is the
  envelope's `error` and `message` in `stdout`; `failure.message` only gives the
  exit code
- `data_truncated` present → not a failure; the rows beyond the 1 MiB cap are
  in `relation_name`. Aggregate or filter there rather than paging through them
- `status: "running"` → wait, then check it with
  `execution_status(execution_id)` rather than re-running it
- `failure.kind: "timed_out"` → `failure.message` says which limit was hit. For
  the 300s runtime limit, narrow the query: filter, aggregate at the source, or
  add a `LIMIT`. If the background slot was held, wait for the named execution
  to finish, then retry
- `failure.kind: "lost"` → the execution's supervisor stopped before it
  recorded an outcome, for example because the workspace restarted. A query is
  read-only, so re-run it
