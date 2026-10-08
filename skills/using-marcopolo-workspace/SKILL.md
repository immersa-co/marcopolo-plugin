---
name: using-marcopolo-workspace
description: Orientation for the MarcoPolo remote workspace, what it is, how `/workspace` is laid out, when to use `workspace_shell`, the `connection_*` tools, and `data_query`, and how the `connection` CLI fits in. Use this skill whenever MarcoPolo, the marcopolo MCP server, `workspace_shell`, `/workspace`, connections, or `connection` CLI commands come up. Read this first when entering a MarcoPolo session, before reaching for a more specific skill.
---

# Using the MarcoPolo workspace

MarcoPolo is a persistent remote Linux workspace at `/workspace` for working
with company data, building dashboards, scheduling jobs, and keeping a durable
collection of queries, scripts, and artifacts.

## Execution surfaces

Three execution surfaces coexist in a MarcoPolo session:

- `workspace_shell` for authoring and shaping: query files, workspace files,
  DuckDB, scripts, git, and crontab inside `/workspace`.
- The `connection_*` tools for connection verbs (`connection_query`,
  `connection_describe`, `connection_test`, and so on). Each runs exactly that
  `connection` CLI verb in the workspace.
- `data_query` for generated code that re-queries live data at view or load
  time — Remote Artifacts, external web apps, scheduled scripts.

For all agent analytics, author query files with `workspace_shell` and run
them with `connection_query`. Reserve `data_query` for programmatic interfaces,
not for the agent's own data exploration.

## Session capability detection

Check which tools are available in the current session before choosing a path:

- Sessions with the `connection_*` tools: run connection verbs through them.
- Sessions with only `workspace_shell`: run the same verbs as CLI commands,
  e.g. `workspace_shell("connection query <name> --file <file> --json")`.
- Generated artifact code (web apps, dashboards) → use `data_query`.

`data_query` is for programmatic interfaces, not a replacement for agent work.

`connection_query` results are CLI envelopes in `stdout`:

- rows from `data` (present only when `include_results=true` / `--include-results` was passed)
- `row_count` from `row_count`, otherwise `len(rows)`
- `run_id` if present
- `relation_name` if present

By default a query returns only the relation handle (`relation_name` +
`row_count` + `column_count`); pass `include_results=true` for the rows in `data`.
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
  tools, except managed connection `RULES.md` projections
- update connection context: write the complete replacement to
  `connections/<name>/scratch/` with `workspace_shell`, then run
  `connection_edit_context(connection_name=<name>, source_file=<source-file>)`
- run scripts: `workspace_shell("python scripts/<file>.py")`
- inspect git state: `workspace_shell("git status")`,
  `workspace_shell("git diff")`

Read `RULES.md` and the relevant `workflows/` guide before authoring; use git
as part of normal work.

## MCP tool families

Workspace tools:

- `workspace_shell(command, timeout=30)` for Unix shell commands in
  `/workspace` (files, DuckDB, scripts, git, crontab scheduling, diagnostics). It
  returns `execution_id`, `status` (`running`, `succeeded`, `failed`),
  `exit_code`, `stdout`, `stderr`, `failure` (`{kind, message}` or null), and
  `next_actions`. A CLI's JSON envelope is the `stdout` string; when a CLI
  fails (`command_failed`), that envelope explains why. `stdout` and `stderr`
  keep the last 2 MiB, so trim large output with `head` or a query `LIMIT`.
  The call returns once the command finishes, up to `timeout` (max 300). A
  command outliving `timeout` returns `status: "running"` and keeps going.
  Don't re-run it; check it with `execution_status(execution_id)` (see
  `using-connection-cli/references/query.md`)
- `execution_status(execution_id)` for the current record of a running or
  finished execution

Connection tools (each runs exactly that `connection` CLI verb with `--json`
and returns the same result shape as `workspace_shell`):

- `connections_list()`
- `connection_add(type, intent?, timeout?)` for credentialed connection setup;
  returns the browser setup URL
- `connection_describe(connection_name, database?, table?, timeout?)`
- `connection_test(connection_name, timeout?)`
- `connection_browse(connection_name, remote_path="", detailed=false, timeout?)`
- `connection_download(connection_name, remote_path, local_path?, timeout?)`
- `connection_upload(connection_name, local_path, remote_path, timeout?)`
- `connection_edit_context(connection_name, source_file, timeout?)`
- `connection_query(connection_name, query_file? | operation?, params?, input_data?, include_results=false, timeout?)`

Data and demo tools:

- `data_query(connection_name, query_file, params?, max_rows?)` for generated
  code and artifacts
- `install_demo_connection(demo_connection, display_name=None, intent_text=None)`
  for hosted demo connections

Some sessions may also expose legacy or host-specific tools. Do not rely on
them as the primary dashboard or query path unless a more specific skill tells
you to.

## The `connection` CLI is the workspace verb surface

For full reference see the `using-connection-cli` skill. Each verb has a
dedicated `connection_*` tool; the CLI shape, which also works inside
`workspace_shell` (for example in cron scripts), is:

```text
connection <verb> [args] --json
```

Common verbs: `list`, `add`, `test`, `describe`, `query`, `browse`, `download`,
`upload`, `edit-context`. Pass `--json` for every verb except `edit-context`,
which takes a source file and intentionally has no `--json` flag.

`connections_list` returns each connection's `capabilities` array. That
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

`RULES.md` files are long-term memory. The workspace-level one holds general
conventions, while each `connections/<name>/RULES.md` is a managed projection
of shared tenant context for that connection. Read them before authoring
queries. After user confirmation, update connection context only through
the Marcopolo UI or `connection_edit_context`; direct edits
are not durable and may be overwritten. The CLI source is a complete
replacement, so start from the current rules unless the user wants to replace
all existing context.

## DUCKDB is a connection

DUCKDB is the in-workspace analytical connection, backed by
`.dv/duckdb/workspace.duckdb`. Query it with `connection_query`:

```text
connection_query(connection_name="DUCKDB", query_file="connections/DUCKDB/queries/<file>.sql")
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
