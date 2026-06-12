---
name: build-scheduled-pipeline
description: Build a Marcopolo scheduled data or AI pipeline that queries governed connections, writes outputs such as DuckDB tables or artifacts, and runs on a schedule. Use when the user asks to automate, schedule, refresh, monitor, or repeatedly run a data workflow.
---

# Build Scheduled Pipeline

Use this skill when the user wants a repeatable data or AI workflow, not just a
generic recurring command. This skill owns pipeline design, implementation,
dry-run validation, and the schedule handoff. For simple schedule management of
an already-existing command, use `setup-automation`.

## Inputs

Extract or ask for the minimum missing inputs:

- Goal: what the pipeline should produce.
- Sources: connection names or data domain.
- Schedule: cron expression or natural-language cadence plus timezone.
- Output: DuckDB table, file, dashboard dataset, notification, or artifact.
- Freshness and retention expectations.
- Failure behavior: alert, retry, pause, or write error output.

Do not collect credentials in chat. Use web-app handoff or approved connection
setup flows when data access is missing.

## Workflow

1. Discover and verify data access.
   - Prefer `connections_list` to discover visible connections.
   - Use `workspace_shell("connection list --json")` when validating the
     workspace runtime path or debugging connection CLI behavior.
   - Test or describe required connections before writing the pipeline.
   - If access is missing, stop and hand off to the web app or connection setup.

2. Design the pipeline contract.
   - Name the pipeline.
   - List inputs, transforms, outputs, schedule, timeout, and owner.
   - Define bounded queries and output table or file names.
   - Decide whether outputs feed a dashboard, downstream code, or a user-facing
     artifact.

3. Implement the runtime script.
   - Prefer a workspace script under `pipelines/` or `scripts/`.
   - Use query files for complex provider queries.
   - Use DuckDB for joins, intermediate state, and repeatable outputs.
   - Make the script idempotent where practical.
   - Print structured status or write a small run summary file.

4. Dry-run the pipeline.
   - Execute the script through `workspace_shell(...)`.
   - Verify row counts, output paths, and failure handling.
   - Fix connection, SQL, Python, or DuckDB issues before scheduling.

5. Create or update the schedule.
   - Today, scheduling is still implemented through the workspace `cron` CLI.
   - Use `workspace_shell("cron create <name> --command \"<workspace-command>\" --cron \"<expr>\" --timeout <seconds> --json")`.
   - Use `workspace_shell("cron list --json")`,
     `workspace_shell("cron get <name> --json")`, and
     `workspace_shell("cron history <name> --limit 20 --json")` to verify.
   - Do not overwrite an existing schedule without user approval.

6. Document operation.
   - State where outputs live.
   - State how to inspect history and failures.
   - State what permissions are required for future runs.

## Verification

Before final response:

- required connections are visible to the session
- the pipeline script dry-run succeeded, or the exact blocker is documented
- outputs were created or verified
- the cron expression is valid
- the schedule was created, updated, or intentionally left as a dry-run
  artifact
- a history or status command works when a schedule exists

## Final Response

Return:

- pipeline name
- files created or modified
- schedule expression and timezone assumption
- output locations
- dry-run result
- schedule status or history command
- remaining setup, permission, or product-contract gaps

## Boundary With Other Skills

- use `query-and-analyze` when the user only needs one-off analysis or manual
  query authoring
- use `setup-automation` when the user already has a command and only needs
  generic cron management
- use this skill when the user needs the full scheduled-pipeline shape:
  design, implementation, validation, and scheduling

## MCP Boundary

Current pipeline work should use:

- `connections_list` or `workspace_shell("connection list --json")` for
  connection discovery
- `workspace_shell(...)` with the `connection` CLI, DuckDB, scripts, and
  `cron` for implementation and scheduling
- web-app handoff for datasource setup, credential consent, sharing, and
  governance changes

Do not introduce pipeline-specific MCP tools such as schedule creation,
pipeline validation, or run status until the product has pipeline-specific
runtime objects behind them.
