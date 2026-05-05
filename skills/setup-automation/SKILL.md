---
name: setup-automation
description: Schedules recurring jobs in the MarcoPolo workspace using the `cron` CLI and produces durable outputs in `artifacts/`. Use this skill whenever the user wants something to run on a schedule, refresh automatically, repeat hourly/daily/weekly/nightly, generate recurring outputs or reports, or "keep something updated" — even when phrased informally ("run this every morning", "remind me weekly", "auto-refresh the numbers", "keep the dashboard fresh"). Also use when managing existing schedules (list, pause, resume, delete, history) or debugging a job that stopped working.
---

# Set up automation

Use automation when a refresh, query, or artifact needs to run repeatedly
without re-authoring the underlying logic.

The in-workspace canonical reference is `/workspace/workflows/setup-automation.md`.

## Schedule a recurring job

The `cron` CLI runs in the workspace pod alongside `connection`. Invoke it
through `workspace_shell`.

1. First, write the query or script you want to schedule. The cron runner
   has no TTY and no assistant in the loop, so the command has to succeed on
   its own with no prompts or interactive input — typically a query file
   you can drive with `connection query`, or a Python script under
   `scripts/`.

2. Inspect the managed cron interface.

   ```
   workspace_shell("cron help --json")
   ```

3. Create the recurring job.

   ```
   workspace_shell("cron create <name> --command \"<workspace command>\" --cron \"<expr>\" --json")
   ```

   - `<name>` is a stable identifier — it becomes the job filename.
   - `<workspace command>` is what gets executed each tick. Common shapes:
     - `connection query <name> --file connections/<name>/queries/<file>.sql --json`
     - `python scripts/<file>.py`
     - any other workspace-relative shell command
   - `<expr>` is a standard 5-field cron expression (e.g., `"0 */6 * * *"`
     for every six hours).
   - `--timeout <seconds>` overrides the default 300s execution timeout.

   On success, the response includes the saved schedule definition.

4. Confirm and inspect.

   ```
   workspace_shell("cron list --json")
   workspace_shell("cron get <name> --json")
   ```

## Manage existing jobs

```
workspace_shell("cron list --json")              # all jobs
workspace_shell("cron get <name> --json")        # single job definition
workspace_shell("cron pause <name> --json")      # disable without deleting
workspace_shell("cron resume <name> --json")     # re-enable
workspace_shell("cron delete <name> --json")     # remove definition + history
workspace_shell("cron history <name> --limit 20 --json")  # recent runs
```

## Where things live

- Schedule definitions: `schedules/<name>.json` (managed by `cron create`,
  but readable and committable to git).
- Run history: `.dv/schedules/<name>_history.jsonl` (runtime-managed; do
  not edit by hand).

The `schedules/` directory is part of the workspace and survives across
sessions; `.dv/schedules/` is runtime state.

## Build durable outputs

When the schedule should produce something the user looks at later, write
into `artifacts/`. The conventions below exist so the user can find what
they're looking for and so runs don't quietly overwrite each other:

- One subdirectory per logical output (e.g., `artifacts/weekly-revenue/`)
  so related runs stay grouped.
- Date-stamped filenames (e.g., `2026-05-12_revenue.csv`) so each run
  preserves history instead of clobbering the previous run. Without this,
  a debugging session that re-runs the job loses yesterday's output.
- Final user-facing files in `artifacts/`; intermediate or scratch files
  elsewhere (e.g., `data/downloads/`, connection `scratch/`) so the
  user's view of `artifacts/` stays clean.

For visual outputs, point the schedule at a query that refreshes the data
behind a `.dashboard` manifest — see `build-dashboard`.

## Patterns

### Refresh upstream data into DUCKDB on a schedule

```
workspace_shell("cron create refresh-revenue --command \"connection query <name> --file connections/<name>/queries/revenue.sql --json\" --cron \"0 */6 * * *\" --json")
```

### Run a Python pipeline nightly

```
workspace_shell("cron create nightly-rollup --command \"python scripts/rollup.py\" --cron \"0 2 * * *\" --json")
```

### Produce a date-stamped artifact

Have the script (or query) write into `artifacts/<output>/$(date -u +%F)_<file>`
so each run appends rather than overwrites.

## Common pitfalls

- **Interactive commands.** The runner has no TTY, so prompts, pagers,
  and anything that waits on input will hang until the timeout. Pipe to
  files, set non-interactive flags, or use the equivalent of `--quiet`.
- **Working directory assumptions.** The runner's cwd is not guaranteed
  to be `/workspace`, so a relative path like `queries/foo.sql` may
  resolve to nothing. Always use workspace-relative paths from the root
  (`connections/<name>/queries/foo.sql`).
- **Long-running jobs.** Default timeout is 300 seconds. For longer
  work, either pass `--timeout <seconds>` or split into smaller jobs —
  shorter jobs are easier to retry and easier to reason about when one
  starts failing.
- **Forgetting `--json`.** Always pass `--json` so you can parse the
  response. This applies to both the scheduled command (when it's a
  `connection` invocation) and to the `cron` calls themselves.
- **Connection capability changes.** A scheduled job that depends on a
  capability (e.g., `download`) will start failing if the connection's
  capabilities change. Re-check `connection list --json` if a job suddenly
  errors.

## Pointers

- writing the underlying query → `query-and-analyze`
- per-verb flag reference → `using-connection-cli`
- producing visual outputs → `build-dashboard`
- workspace layout (where `schedules/` and `artifacts/` sit) → `using-marcopolo-workspace`
