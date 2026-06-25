---
name: query-and-analyze
description: Queries connections, joins results across sources through DuckDB, and analyzes workspace data. Use this skill whenever the user wants to look at, count, summarize, filter, group, join, aggregate, compare, or analyze data, or when exploring a connection's schema or doing follow-up analysis on a previous query.
---

# Query and analyze data

Use this skill for workspace-side query authoring, debugging, materialization,
DuckDB joins, and file analysis. The in-workspace canonical reference is
`/workspace/workflows/query-and-analyze-data.md`.

## Compatibility

Prefer product MCP data tools when the current session exposes them:

- `connections_list`
- `data_query`

Use those tools for simple governed reads that do not need workspace-local query
files, DuckDB shaping, or script authoring.

Older agent sessions may expose only `workspace_shell`. In those sessions, use
the compatibility path:

- `workspace_shell("connection list --json")`
- `workspace_shell("connection query <name> --inline '<sql>' --sample-rows <n> --json")`
- `workspace_shell("connection query <name> --file <workspace-relative-query-file> --sample-rows <n> --json")`

Treat shell query results as CLI envelopes rather than `data_query` payloads.
Normalize them before reasoning over rows:

- rows from `data`, otherwise `preview`
- `row_count` from `row_count`, otherwise `len(rows)`
- `run_id` if present
- `relation_name` if present

Generated dashboards, Remote Artifacts, and external app code should prefer
`data_query` when the product surface exposes it. The shell path is a
compatibility fallback for agent-side work.

## Query one connection

1. Discover connections and confirm capabilities. Prefer `connections_list`
   when available. Otherwise use:

   ```text
   workspace_shell("connection list --json")
   ```

   Pick a connection. Confirm the verb you need is listed in its
   `capabilities`.

2. Read the connection's docs.

   ```text
   workspace_shell("cat connections/<name>/README.md connections/<name>/SYNTAX.md connections/<name>/RULES.md")
   ```

3. If the connection is new or credentials changed, verify them.

   ```text
   workspace_shell("connection test <name> --json")
   ```

4. Look at existing queries and metadata before authoring.

   ```text
   workspace_shell("ls connections/<name>/queries/ connections/<name>/metadata/")
   ```

5. Refresh metadata if it is missing or stale and `describe` is in
   capabilities.

   ```text
   workspace_shell("connection describe <name> --json")
   ```

6. For simple governed reads, prefer `data_query` when available. For
   workspace-local authoring, write the query file under
   `connections/<name>/queries/`.

   ```text
   workspace_shell("""cat > connections/<name>/queries/<file>.sql <<'SQL'
   SELECT col FROM tbl WHERE condition
   SQL""")
   ```

7. Execute the query through the product tool when available and the workflow
   only needs bounded data. Otherwise use the workspace path:

   ```text
   workspace_shell("connection query <name> --file connections/<name>/queries/<file>.sql --sample-rows 500 --json")
   ```

   For inline compatibility probes:

   ```text
   workspace_shell("connection query <name> --inline '<sql>' --sample-rows 500 --json")
   ```

## Join across connections through DUCKDB

DUCKDB is the in-workspace analytical connection.

1. Run each upstream `connection query` first and note each `relation_name`.
2. Write a DuckDB SQL file that joins or transforms those relations.
3. Execute through DUCKDB.

   ```text
   workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<file>.sql --json")
   ```

Save reusable joins in `connections/DUCKDB/queries/` and reusable Python or
shell pipelines in `scripts/`.

## Work with files in the remote workspace

- User-provided files belong in `data/uploads/`.
- Files fetched via `connection download` land in `data/downloads/`.
- Use `data/databases/` for database files when needed.

DuckDB can read CSV, Parquet, and JSON files directly:

```text
workspace_shell("""cat > connections/DUCKDB/queries/<file>.sql <<'SQL'
SELECT * FROM read_csv_auto('data/uploads/<file>.csv') LIMIT 100
SQL""")
workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<file>.sql --json")
```

## Common pitfalls

- The `connection` CLI only exists inside the remote workspace, so the client's
  built-in shell cannot run it. Always use `workspace_shell` for workspace
  commands.
- Trust `connection list --json` or `connections_list` for capabilities.
- Keep compatibility queries bounded with `--sample-rows <n>`.
- Query file paths in `--file` are workspace-relative.

## Pointers

- adding a connection or installing a demo -> `setup-connection`
- per-verb flag reference -> `using-connection-cli`
- workspace layout -> `using-marcopolo-workspace`
- visualizing results -> `build-dashboard`
- building a scheduled workflow -> `build-scheduled-pipeline`
- managing an existing recurring run -> `setup-automation`
