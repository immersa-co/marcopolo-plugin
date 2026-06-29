# `connection query`

```
workspace_shell("connection query <name> --file <query-file> [--params-json <json>] [--sample-rows <n>] --json")
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
- `--sample-rows <n>` — controls how many rows come back into the agent's
  context window. The full result is **always materialized into DuckDB
  regardless** of this value. Default 10.

  Size this to what the agent needs for reasoning and display — not to
  capture the full dataset, which is already in DuckDB.

  | Purpose | Recommended value |
  |---|---|
  | Schema / data shape check | 5–10 |
  | Verify query returned expected rows | 5–20 |
  | Display a bounded list to the user | 50–100 |
  | Aggregation or join (query DuckDB instead) | 5–20 |

  For large result sets, prefer a DuckDB aggregation or export to CSV in
  `/workspace/data/downloads/` for the user to retrieve from the web UI rather
  than pulling all rows into the context window. For small result sets (a few
  dozen rows), `-1` is appropriate and avoids truncation:

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
| `preview` | **string** | JSON-encoded array of the sampled rows. **Must be `json.loads`-ed before use.** Row count bounded by `--sample-rows`. |
| `relation_name` | string | DuckDB relation holding the full result set |
| `column_count` | int | Number of columns in the result |
| `run_id`, `query_file`, `execution_time`, `next_actions` | — | Run metadata |

### Reading rows from the envelope

`preview` is a **string**, not a native array. Parse it before use:

```python
import json
resp = json.loads(workspace_shell_output)       # parse the outer envelope
records = json.loads(resp["preview"])           # parse preview string → list[dict]
# len(records) is the sampled row count (bounded by --sample-rows)
```

Common mistakes:
- `len(resp["preview"])` counts **characters**, not rows.
- `resp["rows"]` is an **int**, not a record list — do not iterate it.
- Iterating `resp["preview"]` without parsing yields characters →
  `'str' object has no attribute 'get'`.

### Prefer DuckDB for anything beyond a quick look

For aggregations, joins, group-bys, or totals, do not parse a large
`preview` and aggregate in Python. The full result is already in DuckDB as
`relation_name`; run a follow-up DuckDB query instead:

```
workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<followup>.sql --json")
```

The DuckDB SQL can reference the materialized `relation_name` directly —
no need to re-run the upstream query. Reserve `preview` parsing for small
samples and display.

## Timeout

`connection query` runs via `workspace_shell`. The default 30s timeout is
sufficient for simple queries. Pass a larger value for:

- queries on large datasets or slow connections: 60–120s
- `connection describe` operations: 30–60s

```text
workspace_shell("connection query <name> --file ... --json", timeout=90)
```

## When `query` fails

Common causes:

- query file doesn't exist or path is wrong → check with `ls`
- SQL syntax doesn't match the connection's dialect → read
  `connections/<name>/SYNTAX.md`
- references a table/column that no longer exists → re-run
  `connection describe <name>` and update the query
- credentials issue → run `connection test <name>` to confirm
- timed out silently → re-run with a larger `timeout` value
