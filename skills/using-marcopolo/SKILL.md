---
name: using-marcopolo
description: What MarcoPolo is and how to use it. Use when the user asks about MarcoPolo, wants to work with data, or when marcopolo MCP tools are involved.
---

# Using MarcoPolo

MarcoPolo is a remotely hosted linux workspace for working with data. It is used
by data analysts and operations teams to query and analyze their company's data,
build dashboards, create automations, and grow a persistent collection of
queries, scripts, and artifacts — all organized around the datasources they work
with.

## Two filesystems

This session has two separate filesystems. Never confuse them.

**Local** (the user's machine) — use Claude's built-in tools (Read, Write, Edit,
Bash, Glob, Grep) for local code, repos, and files.

**Remote workspace** (/workspace) — use ONLY the marcopolo MCP tools:
- `list_datasources` to discover available datasources and capabilities
- `query` to execute queries against datasources (results auto-load into DuckDB)
- `get_schema` to explore datasource structure (databases → tables → columns)
- `browse`, `download`, `upload` for storage datasources (S3, Azure, GDrive)
- `execute_command` to run shell commands, create files, explore the filesystem
- `create_data_view` to build dashboards and visualizations
- `generate_connector_url` to add new datasources

Never use the local `Bash` tool to interact with the remote workspace.
Never use `execute_command` to interact with local files.

## Remote workspace layout

```
/workspace (home directory)
├── docs/           Read-only documentation and rules
│   ├── RULES.md        Global rules and business context
│   └── {datasource}/   Per-datasource docs
│       ├── RULES.md        Business rules and conventions
│       └── SYNTAX.md       Query syntax guide
├── examples/       Read-only working query examples (verified)
├── queries/        Your query files, organized by datasource
│   └── {datasource}/   e.g. queries/ATHENA/report.sql
└── downloads/      Files downloaded from storage datasources
```

Users can access workspace files in the web UI at
`https://mcp.marcopolo.dev/app/workspace/<path>?file=<filename>`.

## Start with list_datasources

Always call `list_datasources()` first. It returns the available datasources,
their capabilities, and instructions on what to do next. Follow its guidance.

## Understand the data first

Before querying any datasource, read the documentation from the remote workspace
using `execute_command`:
```
execute_command("cat docs/RULES.md")                  # global rules and business context
execute_command("cat docs/{datasource}/RULES.md")     # datasource-specific business rules
execute_command("cat docs/{datasource}/SYNTAX.md")    # query syntax and gotchas
```

Then explore the schema with `get_schema`. A query written without this
understanding risks wrong answers and wastes datasource resources. Start narrow,
check before you assume, and ask the user if a strategy isn't working.

## Scheduling

Use `execute_command("dv-schedule ...")` to create and manage recurring
automated tasks (e.g. daily data syncs, scheduled reports). Run
`execute_command("dv-schedule --help")` to see available commands.
