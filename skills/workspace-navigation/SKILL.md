---
name: workspace-navigation
description: How to use marcopolo MCP tools correctly. Use when working with marcopolo tools, the remote workspace, datasources, or data analysis.
---

# MarcoPolo tools and the remote workspace

The marcopolo MCP tools (`list_datasources`, `query`, `get_schema`, `browse`,
`download`, `upload`, `execute_command`, `create_data_view`,
`generate_connector_url`) operate on a remote Linux workspace at /workspace —
not the local filesystem.

Use `execute_command` (not the local `Bash` tool) for all workspace file
operations: reading files, creating query files, running scripts, searching
content. Use `Bash` only for local machine operations.

## Workspace layout

```
/workspace
├── docs/           Rules and syntax guides (read-only)
│   ├── RULES.md        Global business context
│   └── {datasource}/
│       ├── RULES.md    Datasource-specific rules
│       └── SYNTAX.md   Query syntax reference
├── examples/       Working query examples (read-only)
├── queries/        Your query files by datasource
│   ├── {datasource}/   e.g. queries/ATHENA/report.sql
│   └── DUCKDB/         DuckDB follow-up queries
└── downloads/      Files from storage datasources
```

## Getting started

Always start by calling `list_datasources()`. It returns the available
datasources, their capabilities, and what to do next.

Before querying, read the relevant docs:
```
execute_command("cat docs/RULES.md")
execute_command("cat docs/{DATASOURCE}/RULES.md")
execute_command("cat docs/{DATASOURCE}/SYNTAX.md")
```

## Web UI access

Users can browse workspace files in the web UI. File links follow the directory
structure: `https://mcp.marcopolo.dev/app/workspace/<path>?file=<filename>`

For example, `queries/ATHENA/users.sql` is at
`https://mcp.marcopolo.dev/app/workspace/queries/ATHENA?file=users.sql`

## Scheduling

`execute_command` also handles `dv-schedule` commands for creating recurring
automated tasks (daily syncs, scheduled reports, etc.):
```
execute_command("dv-schedule create daily-sync --script sync_data.py --cron '@daily'")
execute_command("dv-schedule list")
```
