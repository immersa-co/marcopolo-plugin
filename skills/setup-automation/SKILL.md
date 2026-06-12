---
name: setup-automation
description: Schedules recurring jobs in the MarcoPolo workspace and produces durable outputs in `artifacts/`. Use this skill whenever the user wants a query, script, refresh, or report to run on a schedule.
---

# Set up automation

Use this skill when an existing query, script, refresh, or artifact needs to
run repeatedly without the agent manually re-executing it.

This skill owns generic workspace `cron` usage and recurring job management.
If the user needs a full scheduled data or AI pipeline designed and implemented from scratch, use `build-scheduled-pipeline`.

## Preferred surfaces

- run shell commands through `workspace_shell(...)`
- use the `cron ...` CLI for schedule management
- use `query-and-analyze` or an existing script first so the scheduled command
  already exists and can run non-interactively
- use `build-scheduled-pipeline` instead when the work needs pipeline design,
  implementation, dry-run validation, and schedule creation as one package

## Run a job on a schedule

1. Write the query or script in the workspace first
2. Confirm the command succeeds without prompts or interactive input
3. Inspect the managed cron interface with `workspace_shell("cron help --json")`
4. Create the recurring job with:

   ```text
   workspace_shell("cron create <name> --command \"<workspace command>\" --cron \"<expr>\" --json")
   ```

5. Confirm the saved job with:

   ```text
   workspace_shell("cron list --json")
   workspace_shell("cron get <name> --json")
   ```

## Durable outputs

- generate outputs with shell, Python, Node, or `connection`
- write user-facing results into `artifacts/`
- keep scheduled command paths rooted at the workspace root
- commit durable logic and docs when appropriate
- keep schedule definitions in `schedules/`

## Manage existing jobs

```text
workspace_shell("cron list --json")
workspace_shell("cron get <name> --json")
workspace_shell("cron pause <name> --json")
workspace_shell("cron resume <name> --json")
workspace_shell("cron delete <name> --json")
workspace_shell("cron history <name> --limit 20 --json")
```

## Failure routing

- if a job starts failing, re-check the saved command, workspace-relative
  paths, and connection capabilities
- use `cron history <name> --limit 20 --json` to inspect recent runs before
  changing the job definition

## Boundary With Other Skills

- use this skill for generic cron-management work over an existing command
- use `build-scheduled-pipeline` for new end-to-end scheduled workflows
- use `query-and-analyze` when the user only needs the underlying query or
  script, not the schedule
