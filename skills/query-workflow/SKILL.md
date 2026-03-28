---
name: query-workflow
description: How to query datasources correctly. Use before writing or executing queries, or when the user asks about data in their datasources.
---

# Query workflow

1. **Discover datasources** — always start here:
   ```
   list_datasources()
   ```

2. **Read the docs** — understand context and syntax before writing queries:
   ```
   execute_command("cat docs/RULES.md")
   execute_command("cat docs/{DS}/RULES.md")
   execute_command("cat docs/{DS}/SYNTAX.md")
   ```

3. **Explore the schema** — drill down from databases to columns:
   ```
   get_schema("DS")                              # databases/datasets
   get_schema("DS", database="db")              # tables
   get_schema("DS", database="db", table="t")   # columns
   ```

4. **Write the query to a file** — the `query` tool expects a file path, not
   inline SQL. Store queries in `queries/{DS}/`:
   ```
   execute_command("cat <<'EOF' > queries/DS/report.sql
   SELECT col FROM tbl WHERE condition
   EOF")
   ```

5. **Execute by file path** — results auto-load into a persistent DuckDB table:
   ```
   query("DS", "queries/DS/report.sql")
   ```
   Use `sample_rows` to control how many rows appear in the response (default
   10). The full result set is always available in DuckDB regardless.

6. **Follow-up in DuckDB** — use the `duckdb_table_name` from the response for
   further analysis without re-querying the original datasource:
   ```
   query("DUCKDB", "queries/DUCKDB/analysis.sql")
   ```
   You can join results from multiple datasources in DuckDB.

7. **Iterate in place** — when refining a query, edit the existing file rather
   than creating new files. This keeps the workspace clean.

## Parameterized queries

Use Jinja2 templating in SQL files with `params`:
```
query("DS", "queries/DS/filter.sql", params={"region": "US", "limit": 100})
```
SQL file: `SELECT * FROM orders WHERE region = '{{ region }}' LIMIT {{ limit }}`

To inject columns from a DuckDB table as template parameters:
```
query("DS", "queries/DS/filter.sql", params={"_params_table": "my_ids"})
```

## Write operations

Some datasources support writing data back. Provide `input_data` with a DuckDB
table name and a dict `op` describing the target:
```
query("google-sheets-ds", {"spreadsheet": "Dashboard", "sheet": "Results", "mode": "replace"}, input_data="analysis_results")
```
Check the datasource's syntax guide on the remote workspace —
`execute_command("cat docs/{DS}/SYNTAX.md")` — for write support and syntax.

## Check examples

The `examples/` directory contains read-only, verified working query patterns.
Review them for reference:
```
execute_command("ls examples/")
```
