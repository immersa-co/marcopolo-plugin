---
name: setup-automation
description: Schedule recurring jobs in the MarcoPolo workspace with the standard `crontab`, and put durable outputs in `artifacts/`. Use this skill when the user already has a command or script and wants it scheduled, refreshed, paused, resumed, deleted, or inspected.
---

# Set up automation

Use this when an existing command or script needs to run on a schedule. For a
pipeline designed and built from scratch, use `build-scheduled-pipeline`.

Schedule it with the standard `crontab`, invoked through `workspace_shell`. There
is no MarcoPolo-specific cron tooling — use cron the way you already would.

The only things worth knowing that aren't generic cron:

- cron runs **shell commands in the pod**, not MCP tools — schedule a
  `connection query …`, a script, or `python3 …`, not a `data_query` call.
- Nothing collects cron's output here (no mailbox), so redirect a job to a log
  file under `/workspace` if you want to inspect its runs.
- Put durable, user-facing outputs in `artifacts/` (one subdir per output,
  date-stamped filenames); keep scratch elsewhere.

## Pointers

- writing the command or query -> `query-and-analyze`, `using-connection-cli`
- a full scheduled pipeline -> `build-scheduled-pipeline`
- workspace layout -> `using-marcopolo-workspace`
