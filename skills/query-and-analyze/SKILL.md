---
name: query-and-analyze
description: Queries connections, joins data through DUCKDB, and analyzes uploaded files inside the MarcoPolo remote workspace. Use this skill whenever the user wants analysis, aggregation, filtering, comparison, or follow-up querying on workspace data.
---

# Query and analyze data

Use this skill when the work needs query authoring or debugging inside the
workspace, intermediate materialization, DUCKDB joins, or analysis over files
that live in the remote workspace.

For live dashboards or generated apps that only need bounded runtime data,
prefer the MCP `connections_list` and `data_query` tools instead of routing the fetch through `workspace_shell(...)`.

When using MCP `data_query`, treat the result as an envelope object rather than a bare row array. The usual contract is `{ rows: [...] }` plus metadata such as `success`, so callers should unwrap `rows` before iterating or handing results to chart code.

## Preferred surfaces

- run shell commands through `workspace_shell(...)`
- use the `connection ...` CLI for connection operations
- use `connection query DUCKDB ...` for joins and in-workspace derived datasets
- use `using-connection-cli` for detailed `connection` verb or flag reference

## Query one connection

1. Start with `workspace_shell("connection list --json")`
2. Choose a connection and confirm the needed verb is listed in its `capabilities`
3. Read `connections/<name>/README.md`, `connections/<name>/RULES.md`, and `connections/<name>/SYNTAX.md`
4. If credential behavior is unclear or credentials changed, run `workspace_shell("connection test <name> --json")`
5. Inspect existing files in `connections/<name>/queries/` and prefer adapting an existing query over starting from scratch
6. Inspect existing files in `connections/<name>/metadata/` if present
7. If `describe` is available and metadata snapshots are missing or stale, run `workspace_shell("connection describe <name> --json")`
8. Read the metadata snapshot files in `connections/<name>/metadata/`
9. Write or revise a query file in `connections/<name>/queries/` using shell commands in the remote workspace
10. Run `workspace_shell("connection query <name> --file connections/<name>/queries/<file> --json")`

## Query authoring notes

- treat `capabilities` as authoritative before using gated verbs
- prefer `connections/<name>/queries/report.sql` over ad hoc relative paths
- if an existing query is close, reuse its pattern and copy it to a new file
  unless you intentionally want to change the existing workflow
- preserve connection-specific syntax, naming, filters, and join patterns that
  already work in this workspace
- rerun `connection describe ...` only when the connection changed, the
  snapshot looks stale, or a query fails because the structure no longer
  matches
- do not run `connection browse`, `download`, or `upload` unless that verb
  appears in the selected connection's `capabilities`

## Join across connections with DUCKDB

1. Query each upstream connection first; each result is materialized into
   DUCKDB as a relation
2. Use `workspace_shell("connection query DUCKDB --file <query-file> --json")`
   to join and transform those relations
3. Use returned `relation_name` values directly in follow-up DUCKDB SQL
4. Save reusable SQL in `connections/DUCKDB/queries/` or reusable code in
   `scripts/`

## Work with files in the workspace

- user-provided files belong in `data/uploads/`
- fetched files usually land in `data/downloads/`
- database files such as SQLite belong in `data/databases/`

DuckDB can read files directly from those paths, so file-based analysis usually becomes a DUCKDB query rather than bespoke parsing code.

## Failure routing

- if metadata is missing or stale and `describe` is available, rerun
  `workspace_shell("connection describe <name> --json")`
- if a query fails because the structure changed, refresh metadata before
  rewriting the query
- if you need `connection` flags or response details, consult
  `using-connection-cli` instead of guessing
