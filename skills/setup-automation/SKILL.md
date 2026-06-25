---
name: setup-automation
description: Manage recurring jobs in the MarcoPolo workspace using the `cron` CLI and produce durable outputs in `artifacts/`. Use this skill when the user already has a command or script and wants it scheduled, refreshed, paused, resumed, deleted, or inspected.
---

# Set up automation

Use this skill when a refresh, query, or artifact needs to run repeatedly
without re-authoring the underlying logic. If the user needs a full scheduled
pipeline designed and implemented, use `build-scheduled-pipeline` instead.

The in-workspace canonical reference is `/workspace/workflows/setup-automation.md`.

## Compatibility

Prefer product MCP data tools when the current session exposes them:

- `connections_list`
- `data_query`

Older agent sessions may expose only `workspace_shell`. In those sessions, use
the compatibility path for agent-side connection discovery or bounded query
probes:

- `workspace_shell("connection list --json")`
- `workspace_shell("connection query <name> --inline '<sql>' --sample-rows <n> --json")`
- `workspace_shell("connection query <name> --file <workspace-relative-query-file> --sample-rows <n> --json")`

The schedule itself still runs workspace commands through `cron`, not MCP tool
calls.

## Schedule a recurring job

The `cron` CLI runs in the workspace pod alongside `connection`. Invoke it
through `workspace_shell`.

1. First, write the query, command, or script you want to schedule. The cron
   runner has no TTY and no assistant in the loop, so the command has to
   succeed on its own with no prompts or interactive input.

2. Inspect the managed cron interface.

   ```text
   workspace_shell("cron help --json")
   ```

3. Create the recurring job.

   ```text
   workspace_shell("cron create <name> --command \"<workspace command>\" --cron \"<expr>\" --json")
   ```

4. Confirm and inspect.

   ```text
   workspace_shell("cron list --json")
   workspace_shell("cron get <name> --json")
   ```

## Manage existing jobs

```text
workspace_shell("cron list --json")
workspace_shell("cron get <name> --json")
workspace_shell("cron pause <name> --json")
workspace_shell("cron resume <name> --json")
workspace_shell("cron delete <name> --json")
workspace_shell("cron history <name> --limit 20 --json")
```

## Where things live

- Schedule definitions: `schedules/<name>.json`
- Run history: `.dv/schedules/<name>_history.jsonl`

The `schedules/` directory is part of the workspace and survives across
sessions. `.dv/schedules/` is runtime state.

## Build durable outputs

When the schedule should produce something the user looks at later, write into
`artifacts/`.

- Use one subdirectory per logical output.
- Use date-stamped filenames so runs preserve history.
- Keep final user-facing files in `artifacts/`; keep scratch output elsewhere.

For visual outputs, point the schedule at a query, materialization step, or
pipeline that refreshes the data consumed by the dashboard or generated app.

## Patterns

### Refresh upstream data into DUCKDB on a schedule

```text
workspace_shell("cron create refresh-revenue --command \"connection query <name> --file connections/<name>/queries/revenue.sql --json\" --cron \"0 */6 * * *\" --json")
```

### Run a Python pipeline nightly

```text
workspace_shell("cron create nightly-rollup --command \"python scripts/rollup.py\" --cron \"0 2 * * *\" --json")
```

## Common pitfalls

- Interactive commands hang because the runner has no TTY.
- Always use workspace-relative paths from the root.
- Long-running jobs may need `--timeout <seconds>`.
- Always pass `--json`.
- Re-check `connection list --json` if a job starts failing after connection
  capability changes.

## Pointers

- writing the underlying query -> `query-and-analyze`
- per-verb flag reference -> `using-connection-cli`
- building a dashboard or generated app -> `build-dashboard`
- building a scheduled workflow -> `build-scheduled-pipeline`
- workspace layout -> `using-marcopolo-workspace`
