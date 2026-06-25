---
name: using-marcopolo-workspace
description: Orientation for the MarcoPolo remote workspace, what it is, how `/workspace` is laid out, when to use the product MCP data tools versus `workspace_shell`, and how the `connection` and `cron` CLIs fit in. Use this skill whenever MarcoPolo, the marcopolo MCP server, `workspace_shell`, `/workspace`, connections, or `connection` and `cron` CLI commands come up. Read this first when entering a MarcoPolo session, before reaching for a more specific skill.
---

# Using the MarcoPolo workspace

MarcoPolo is a persistent remote Linux workspace at `/workspace` for working
with company data, building dashboards, scheduling jobs, and keeping a durable
collection of queries, scripts, and artifacts.

## Two execution surfaces

Two execution surfaces coexist in a MarcoPolo session:

- Product MCP data tools for governed data reads:
  - `connections_list`
  - `data_query`
- `workspace_shell` for workspace files, scripts, git, DuckDB, query authoring,
  and cron operations inside `/workspace`

Use the product data tools for simple governed data reads when the current
session exposes them. Use `workspace_shell` for normal file and process work in
the workspace.

## Compatibility

Older agent sessions may expose only `workspace_shell`. In those sessions, use
the compatibility path for agent-side work:

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
`data_query` when the product surface exposes it. Do not teach generated code
to call `workspace_shell`.

## Two shell environments

Two shell environments coexist in this session:

- Your built-in shell and filesystem tools act on the client's own environment.
- `workspace_shell` runs commands inside the MarcoPolo remote workspace at
  `/workspace`.

Your built-in tools cannot reach the MarcoPolo workspace. They cannot read or
create files there, run the `connection` or `cron` CLIs that only exist there,
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
    build-dashboard.md
    setup-automation.md
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
  schedules/
  .dv/
```

Always read first before authoring:

- `workspace_shell("cat /workspace/RULES.md")`
- `workspace_shell("cat /workspace/workflows/README.md")`
- `workspace_shell("cat connections/<name>/README.md connections/<name>/RULES.md connections/<name>/SYNTAX.md")`

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
- schedule definitions -> `schedules/`
- user-provided data -> `data/uploads/`
- fetched data -> `data/downloads/`
- database files -> `data/databases/`

Do not write to `.dv/`; it is runtime-managed.

## Pointers

- adding a connection, installing a demo, fixing credentials -> `setup-connection`
- querying data, exploring schemas, joining sources -> `query-and-analyze`
- building a chart or dashboard -> `build-dashboard`
- building a scheduled data or AI workflow -> `build-scheduled-pipeline`
- managing an existing recurring job -> `setup-automation`
- looking up a `connection` CLI verb or flag -> `using-connection-cli`
