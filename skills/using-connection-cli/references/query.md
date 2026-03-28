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
- `--sample-rows <n>` — preview row count, default 10. Pass `-1` to
  include all rows in the JSON payload. The full result is materialized
  into DuckDB regardless.
- `--json` — always pass.

## Path semantics

Paths are workspace-relative. Prefer `connections/<name>/queries/<file>`
over `queries/<file>`. Absolute paths under `/workspace` also work but
the relative form is the convention everywhere else in the workspace.

## Response shape

```json
{
  "success": true,
  "operation": "query",
  "connection": "<name>",
  "run_id": "<uuid>",
  "relation_name": "<duckdb-relation-name>",
  "row_count": <int>,
  "preview": [{ ... }, ...]
}
```

The full result is materialized into DuckDB as `relation_name`. To do
follow-up analysis (joins, aggregations, transformations), query through
DUCKDB:

```
workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<followup>.sql --json")
```

The DuckDB SQL can reference the materialized `relation_name` directly —
no need to re-run the upstream query.

## When `query` fails

Common causes:

- query file doesn't exist or path is wrong → check with `ls`
- SQL syntax doesn't match the connection's dialect → read
  `connections/<name>/SYNTAX.md`
- references a table/column that no longer exists → re-run
  `connection describe <name>` and update the query
- credentials issue → run `connection test <name>` to confirm
