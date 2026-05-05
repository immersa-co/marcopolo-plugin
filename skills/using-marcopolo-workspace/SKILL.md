---
name: using-marcopolo-workspace
description: Orientation for the MarcoPolo remote workspace — what it is, how `/workspace` is laid out, why `workspace_shell` is the only tool that can reach it (built-in tools cannot), and how the `connection`/`cron` CLIs fit in. Use this skill whenever MarcoPolo, the marcopolo MCP server, the `workspace_shell` tool, the `/workspace` directory, connections, or `connection`/`cron` CLI commands come up — including when the user says "use Marcopolo" without specifying what to do, or when any marcopolo MCP tool is invoked even incidentally. Read this first when entering a MarcoPolo session, before reaching for a more specific skill.
---

# Using the MarcoPolo workspace

MarcoPolo is a persistent remote Linux workspace at `/workspace` for working
with company data — querying connections, building dashboards, scheduling
jobs, and keeping a durable collection of queries, scripts, and artifacts.

The workspace is the surface. Almost everything happens there.

## Two shell environments

Two shell environments coexist in this session:

- **Your built-in tools** — the shell and filesystem tools your client
  provides (Bash, Read, Write, Edit, Glob, Grep, etc., depending on the
  client). These act on the client's own environment.
- **`workspace_shell`** — the MCP tool that runs commands inside the
  MarcoPolo remote workspace at `/workspace`.

Your built-in tools cannot reach the MarcoPolo workspace. They can't
read or create files there, run the `connection` or `cron` CLIs that
only exist there, or see git state inside it. Only `workspace_shell`
can.

So for all MarcoPolo work — reading files, writing queries, running
scripts, inspecting git — use `workspace_shell`. Reach for your built-in
tools only for things outside MarcoPolo (the client's own configuration,
a repo on the user's machine, files they explicitly point at there).

User-uploaded files land in `data/uploads/` *inside the MarcoPolo
workspace* — `workspace_shell` reads them, not the built-in tools.

## Common `workspace_shell` operations

Treat `/workspace` like a checked-out repo. Common shapes:

- read files: `workspace_shell("cat /workspace/RULES.md")`
- list and search: `workspace_shell("ls connections/")`, `workspace_shell("rg <pattern> connections/")`
- write and edit files: `workspace_shell` with heredocs, `sed`, or other shell tools
- run scripts: `workspace_shell("python scripts/<file>.py")`
- inspect git state: `workspace_shell("git status")`, `workspace_shell("git diff")`

Read `RULES.md` and the relevant `workflows/` guide before authoring; use
git as part of normal work.

## The four MCP tools

- `workspace_shell(command, timeout=30)` — run any command in the remote
  workspace. This is how you read files, write queries, run scripts, drive the
  `connection` and `cron` CLIs, and inspect git state.
- `connection_setup(type, intent_text=None)` — generate a browser URL the user
  opens to configure a credentialed connection. Returns canonical type
  resolution and a setup workflow.
- `install_demo_connection(demo_connection, display_name=None, intent_text=None)`
  — install a hosted demo connection directly. No browser flow.
- `preview_dashboard(path)` — open the interactive preview UI for a workspace
  `.dashboard` manifest.

Everything else — listing connections, testing credentials, describing
metadata, querying, browsing storage, scheduling jobs — runs inside the
workspace through `workspace_shell` and the in-pod `connection` and `cron`
CLIs.

## The `connection` CLI is the verb surface

For full reference see the `using-connection-cli` skill. The shape:

```
connection <verb> [args] --json
```

Common verbs: `list`, `add`, `test`, `describe`, `query`, `browse`, `download`,
`upload`. Always pass `--json` so output is structured.

`connection list --json` returns each connection's `capabilities` array. That
list is **authoritative** — never call `browse`, `download`, or `upload` on a
connection unless that verb appears in its capabilities.

## Workspace layout

```
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
      README.md                   connection summary + authoritative capabilities
      RULES.md                    runtime-managed working guidance
      SYNTAX.md                   query syntax reference
      queries/                    saved query files (workspace-relative paths)
      metadata/                   snapshots written by `connection describe`
      profile/                    profiling snapshots
      scratch/                    temporary work
    DUCKDB/                       in-workspace analytical connection
  scripts/                        reusable programs (Python, shell, Node)
  artifacts/                      user-facing outputs
    dashboards/                   .dashboard manifests + view.tsx files
  data/
    uploads/                      user-provided files
    downloads/                    files fetched via `connection download`
    databases/                    database files (SQLite, etc.)
  schedules/                      cron job definitions
  .dv/                            runtime-managed state (DuckDB, etc.)
```

Always read first before authoring:

- `workspace_shell("cat /workspace/RULES.md")`
- `workspace_shell("cat /workspace/workflows/README.md")`
- `workspace_shell("cat connections/<name>/README.md connections/<name>/RULES.md connections/<name>/SYNTAX.md")`

## DUCKDB is a connection

DUCKDB is the in-workspace analytical connection, backed by
`.dv/duckdb/workspace.duckdb`. It is not a separate tool — query it the same
way as any other connection:

```
workspace_shell("connection query DUCKDB --file connections/DUCKDB/queries/<file>.sql --json")
```

Use it for joins across connections, intermediate tables, and in-workspace
derived datasets.

## Where to put things

- query files → `connections/<name>/queries/`
- metadata snapshots → `connections/<name>/metadata/` (written by `connection describe`)
- reusable programs → `scripts/`
- user-facing outputs → `artifacts/`
- dashboards → `artifacts/dashboards/<name>.dashboard` + `view.tsx`
- schedule definitions → `schedules/`
- user-provided data → `data/uploads/`
- fetched data → `data/downloads/` (from `connection download`)
- database files (SQLite, etc.) → `data/databases/`

Don't write to `.dv/` — it is runtime-managed.

## Pointers

- adding a connection, installing a demo, fixing credentials → `setup-connection`
- querying data, exploring schemas, joining sources → `query-and-analyze`
- building a chart or dashboard → `build-dashboard`
- scheduling recurring jobs or refreshes → `setup-automation`
- looking up a `connection` CLI verb or flag → `using-connection-cli`
