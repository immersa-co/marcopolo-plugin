---
name: query-and-analyze
description: Queries connections, joins results across sources through DuckDB, and analyzes user-uploaded data files inside the MarcoPolo remote workspace. Use this skill whenever the user wants to look at, count, summarize, filter, group, join, aggregate, compare, or analyze data — even when they describe the request informally ("how many users last week?", "pull the revenue numbers", "what's our churn?", "compare the two tables", "rank these by X") and even when they don't explicitly say "query" or "SQL". Also use when exploring a connection's schema, refreshing metadata snapshots, or doing follow-up analysis on a previous query.
---

# Query and analyze data

All work happens in the remote workspace through `workspace_shell`. The
in-workspace canonical reference is `/workspace/workflows/query-and-analyze-data.md`.

## Query one connection

1. Discover connections and confirm capabilities.

   ```
   workspace_shell("connection list --json")
   ```

   Pick a connection. Confirm the verb you need is listed in its
   `capabilities` — never call `browse`/`download`/`upload` unless that
   verb is advertised.

2. Read the connection's docs.

   ```
   workspace_shell("cat connections/<name>/README.md connections/<name>/SYNTAX.md connections/<name>/RULES.md")
   ```

3. If the connection is new or credentials changed, verify them.

   ```
   workspace_shell("connection test <name> --json")
   ```

4. Look at existing queries and metadata before authoring.

   ```
   workspace_shell("ls connections/<name>/queries/ connections/<name>/metadata/")
   ```

   Prefer adapting an existing query file to starting from scratch. Existing
   queries encode connection-specific syntax, naming, filters, and join
   patterns that already work in this workspace.

5. Refresh metadata if it's missing or stale and `describe` is in capabilities.

   ```
   workspace_shell("connection describe <name> --json")
   ```

   This writes snapshot files into `connections/<name>/metadata/`. Read them
   before writing the query.

   ```
   workspace_shell("ls connections/<name>/metadata/ && cat connections/<name>/metadata/<file>")
   ```

   Rerun `describe` only when the connection changed, the snapshot looks old,
   or a query fails because the structure no longer matches.

6. Write the query file under `connections/<name>/queries/`. Use a
   `workspace_shell` heredoc — the built-in Write/Edit tools can't reach
   the remote workspace and would land the file in the client's
   environment instead.

   ```
   workspace_shell("""cat > connections/<name>/queries/<file>.sql <<'SQL'
   SELECT col FROM tbl WHERE condition
   SQL""")
   ```

   If an existing query is close, copy it to a new file rather than mutating
   the original — unless you intentionally want to change the existing
   workflow.

7. Execute the query.

   ```
   workspace_shell("connection query <name> --file connections/<name>/queries/<file>.sql --json")
   ```

   Path semantics: query file paths are workspace-relative; prefer
   `connections/<name>/queries/<file>` over `queries/<file>`.

   The response includes `run_id`, `relation_name` (a materialized DuckDB
   relation), `row_count`, and a `preview` array (default 10 rows; pass
   `--sample-rows -1` to include all rows in the payload).

## Join across connections through DUCKDB

DUCKDB is the in-workspace analytical connection. Backed by
`.dv/duckdb/workspace.duckdb`, it appears as a normal connection at
`connections/DUCKDB/`.

1. Run each upstream `connection query` first. Each materializes a DuckDB
   relation; note the `relation_name` from each response.

2. Write a DuckDB SQL file that joins or transforms those relations.

   ```
   workspace_shell("""cat > connections/DUCKDB/queries/<file>.sql <<'SQL'
   SELECT a.id, b.amount
     FROM <relation_a> a
     JOIN <relation_b> b USING (id)
   SQL""")
   ```

3. Execute through DUCKDB.

   ```
   workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<file>.sql --json")
   ```

Save reusable joins in `connections/DUCKDB/queries/` and reusable Python or
shell pipelines in `scripts/`.

## Work with files in the remote workspace

- User-provided files belong in `data/uploads/`. The user uploads them
  into the remote workspace; read them with `workspace_shell` (the
  built-in tools can't reach them).
- Files fetched via `connection download` land in `data/downloads/` by
  default.
- Use `data/databases/` for database files (SQLite, etc.) when needed.

DuckDB can read CSV/Parquet/JSON files directly, so for ad-hoc analysis on
an uploaded file:

```
workspace_shell("""cat > connections/DUCKDB/queries/<file>.sql <<'SQL'
SELECT * FROM read_csv_auto('data/uploads/<file>.csv') LIMIT 100
SQL""")
workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<file>.sql --json")
```

## Common pitfalls

- **Wrong shell.** The `connection` CLI only exists inside the remote
  workspace pod, so the client's built-in shell can't run it — calling
  `connection ...` through Bash will fail with "command not found".
  Always use `workspace_shell`.
- **Capabilities, not assumptions.** Trust `connection list --json` —
  capabilities vary per connection type and can change as the platform
  evolves.
- **One file per query.** `connection query` expects `--file <existing-path>`.
  Write the file first; don't try to inline SQL.
- **Workspace-relative paths.** Query file paths in `--file` are
  workspace-relative; absolute paths under `/workspace` work too, but the
  relative form is the convention.

## Pointers

- adding a connection or installing a demo → `setup-connection`
- per-verb flag reference → `using-connection-cli`
- workspace layout → `using-marcopolo-workspace`
- visualizing results → `build-dashboard`
- scheduling a recurring run → `setup-automation`
