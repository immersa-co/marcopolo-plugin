---
name: using-marcopolo-workspace
description: Orientation for the MarcoPolo remote workspace. Use this skill when entering a MarcoPolo session, when the user says to use MarcoPolo without specifying a workflow, or when clarifying how `workspace_shell(...)`, `/workspace`, and the workspace CLIs fit together.
---

# Using the MarcoPolo workspace

Use this skill as the entry-point orientation layer for MarcoPolo work.

## Canonical workspace docs

- `/workspace/README.md` for bootstrap, command surfaces, and layout
- `/workspace/RULES.md` for workspace-wide rules and conventions

The plugin skills are the task-specific guidance layer:

- `setup-connection`
- `query-and-analyze`
- `build-dashboard`
- `build-scheduled-pipeline`
- `setup-automation`
- `using-connection-cli`

## Core model

- MarcoPolo is a persistent remote workspace at `/workspace`
- `workspace_shell(...)` is the MCP tool for running shell commands and
  processing files there
- `connection ...` and `cron ...` are CLI tools available inside that workspace
  shell environment
- `connection_setup(...)`, `install_demo_connection(...)`, and
  `preview_dashboard(...)` are dedicated MCP tools for setup and dashboard
  preview

## Startup checklist

When entering a MarcoPolo task:

1. Read `/workspace/README.md`
2. Read `/workspace/RULES.md`
3. If working with a connection, run `workspace_shell("connection list --json")`
4. Before authoring for a connection, read `connections/<name>/README.md`,
   `connections/<name>/RULES.md`, and `connections/<name>/SYNTAX.md`
5. Route into the relevant plugin skill for the concrete task

## Critical checks

- run shell commands for `/workspace` through `workspace_shell(...)`
- discover available CLI flags with
  `workspace_shell("connection --help")`,
  `workspace_shell("connection <verb> --help")`, and
  `workspace_shell("cron help --json")`
- treat `connection list --json` capabilities as authoritative
- do not hand-author files in `.dv/`

## Routing guidance

- add or repair a connection → `setup-connection`
- query or join data → `query-and-analyze`
- create a quick one-off chart in the current conversation → inline
  visualization, not a durable workspace artifact
- build or refine a dashboard → `build-dashboard`
- build a scheduled data or AI workflow → `build-scheduled-pipeline`
- schedule recurring work → `setup-automation`
- detailed `connection` CLI behavior → `using-connection-cli`
