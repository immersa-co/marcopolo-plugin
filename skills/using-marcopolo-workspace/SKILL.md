---
name: using-marcopolo-workspace
description: Orientation for the MarcoPolo remote workspace, what it is, how `/workspace` is laid out, when to use the product MCP data tools versus `workspace_shell`, and how the `connection` CLI fits in. Use this skill whenever MarcoPolo, the marcopolo MCP server, `workspace_shell`, `/workspace`, connections, or `connection` CLI commands come up. Read this first when entering a MarcoPolo session, before reaching for a more specific skill.
---

# Using the MarcoPolo workspace

MarcoPolo is a persistent remote Linux workspace at `/workspace` for working
with company data, building dashboards, scheduling jobs, and keeping a durable
collection of queries, scripts, and artifacts.

For an application embedding its own Python agent, read
[the SDK toolkit guide](references/sdk-toolkit.md). Its tools execute through
the same server executor used by the MCP data tools below.

## MCP execution surfaces

Use `connections_list` and `data_query` for governed queries when the current
session exposes them. Current `data_query` accepts `connection` and exactly
one of `query_text` or `query_path`, plus `parameters`, `max_rows`, and `inline`.
Set `inline=false` for intermediate results; query their relations against
connection `DUCKDB` with `inline=true` to return the final bounded answer.
`max_rows` limits inline records, not the stored relation.

The result has `content`, structured `data`, and `failed`. MCP also preserves
legacy query fields (`run_id`, `relation_name`, `rows`) and input aliases
(`connection_name`, `query_file`, `params`) for generated applications. Read
`data.error` or `data.failure` when `failed` is true and follow the guidance.

Use `workspace_shell` for workspace files, durable query authoring, scripts,
git, cron, and other commands inside `/workspace`. Read the connection's
README, RULES, and SYNTAX files before authoring queries.

## Session capability detection

Inspect the installed tool schemas. Older sessions may expose only
`workspace_shell`, or a `data_query` accepting only the legacy aliases. Use the
available schema. With only the shell, discover through `connection list --json`
and run saved queries through `connection query <name> --file <path> --json`.
Use `--include-results` only when rows are needed; bound final SQL with `LIMIT`.

Generated apps can use `data_query` for fresh data when it is exposed. Keep
intermediate records out of model prompts on every surface.

When using `workspace_shell` for queries, treat results as CLI envelopes:

- rows from `data` (present only when `--include-results` was passed)
- `row_count` from `row_count`, otherwise `len(rows)`
- `run_id` if present
- `relation_name` if present

By default a query returns only the relation handle (`relation_name` +
`row_count` + `column_count`); pass `--include-results` for the rows in `data`.
For large results, query the relation in DuckDB rather than pulling every row
into `data`.

## Two shell environments

Two shell environments coexist in this session:

- Your built-in shell and filesystem tools act on the client's own environment.
- `workspace_shell` runs commands inside the MarcoPolo remote workspace at
  `/workspace`.

Your built-in tools cannot reach the MarcoPolo workspace. They cannot read or
create files there, run the `connection` CLI or `crontab` that only exist there,
or see git state inside it. Only `workspace_shell` can.

So for all MarcoPolo workspace work, such as reading files, writing queries,
running scripts, or inspecting git, use `workspace_shell`. Reach for your
built-in tools only for things outside MarcoPolo.

User-uploaded files land in `data/uploads/` inside the MarcoPolo workspace.
`workspace_shell` reads them, not the built-in tools.

## Common `workspace_shell` operations

Treat `/workspace` like a checked-out repo. Common shapes:

- read files: `workspace_shell("cat /workspace/RULES.md")`
- list and search: `workspace_shell("ls connections/")`,
  `workspace_shell("rg <pattern> connections/")`
- write and edit files: `workspace_shell` with heredocs, `sed`, or other shell
  tools
- run scripts: `workspace_shell("python scripts/<file>.py")`
- inspect git state: `workspace_shell("git status")`,
  `workspace_shell("git diff")`

Read `RULES.md` and the relevant `workflows/` guide before authoring; use git
as part of normal work.

## MCP tool families

Product data tools:

- `connections_list` for connection discovery when available
- `data_query` for bounded governed query execution when available

Workspace and ext-app tools:

- `workspace_shell(command, timeout=30)` for remote workspace commands
- `connection_setup(type, intent_text=None)` for credentialed connection setup
- `install_demo_connection(demo_connection, display_name=None, intent_text=None)`
  for hosted demo connections

Some sessions may also expose legacy or host-specific tools. Do not rely on
them as the primary dashboard or query path unless a more specific skill tells
you to.

## The `connection` CLI is the workspace verb surface

For full reference see the `using-connection-cli` skill. The shape:

```text
connection <verb> [args] --json
```

Common verbs: `list`, `add`, `test`, `describe`, `query`, `browse`, `download`,
`upload`. Always pass `--json` so output is structured.

`connection list --json` returns each connection's `capabilities` array. That
list is authoritative. Never call `browse`, `download`, or `upload` on a
connection unless that verb appears in its capabilities.

## Workspace layout

```text
/workspace/
  README.md                       workspace overview
  RULES.md                        workspace-wide rules and conventions
  workflows/                      curated guides for recurring tasks
    README.md
    setup-connection.md
    query-and-analyze-data.md
  connections/                    one subdirectory per visible connection
    <name>/
      README.md
      RULES.md
      SYNTAX.md
      queries/
      metadata/
      profile/
      scratch/
    DUCKDB/
  scripts/
  artifacts/
  data/
    uploads/
    downloads/
    databases/
  .dv/
```

Always read first before authoring:

- `workspace_shell("cat /workspace/RULES.md")`
- `workspace_shell("cat /workspace/workflows/README.md")`
- `workspace_shell("cat connections/<name>/README.md connections/<name>/RULES.md connections/<name>/SYNTAX.md")`
- Before authoring or running any query, also read the `query-and-analyze` and
  `using-connection-cli` skills — they are prerequisites, not optional
  further reading.

`RULES.md` files are long-term memory — the workspace-level one holds general
conventions, and each `connections/<name>/RULES.md` holds connection-specific
facts: field quirks, reliable query patterns, naming conventions accumulated
from prior sessions. Read them before authoring queries and update them when
you discover new facts.

## DUCKDB is a connection

DUCKDB is the in-workspace analytical connection, backed by
`.dv/duckdb/workspace.duckdb`. Query it through the `connection` CLI:

```text
workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<file>.sql --json")
```

Use it for joins across connections, intermediate tables, and in-workspace
derived datasets.

## Where to put things

- query files -> `connections/<name>/queries/`
- metadata snapshots -> `connections/<name>/metadata/`
- reusable programs -> `scripts/`
- user-facing outputs -> `artifacts/`
- scheduled jobs -> the user crontab (`crontab -l`), not a workspace file
- user-provided data -> `data/uploads/`
- fetched data -> `data/downloads/`
- database files -> `data/databases/`

Do not write to `.dv/`; it is runtime-managed.

## Pointers

- adding a connection, installing a demo, fixing credentials -> `setup-connection`
- querying data, exploring schemas, joining sources -> `query-and-analyze`
- before running any `connection` verb (even routine ones) -> `using-connection-cli`
