---
name: build-scheduled-pipeline
description: Build a Marcopolo scheduled data or AI pipeline that queries governed connections, writes outputs such as DuckDB tables or artifacts, and runs on a schedule. Use when the user asks to automate, schedule, refresh, monitor, or repeatedly run a data workflow.
---

# Build Scheduled Pipeline

Create a scheduled Marcopolo data or AI pipeline. The current implementation
uses workspace scripts plus the `cron` CLI. Do not assume pipeline-specific MCP
tools until Marcopolo exposes first-class pipeline runtime objects.

## Compatibility

Prefer product MCP data tools when the current session exposes them:

- `connections_list`
- `data_query`

Older agent sessions may expose only `workspace_shell`. In those sessions, use
the compatibility path for agent-side discovery and bounded query validation:

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
`data_query` when the product surface exposes it. The shell path is a
compatibility fallback for agent-side work.

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
   - Prefer `connections_list` to discover visible connections when available.
   - Use `workspace_shell("connection list --json")` when the product tool is
     unavailable or when validating the workspace runtime path.
   - Test or describe required connections before writing the pipeline.
   - If access is missing, stop and hand off to the web app or connection
     setup.

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
   - Execute the script through `workspace_shell`.
   - Verify row counts, output paths, and failure handling.
   - Use bounded `data_query` or bounded `workspace_shell("connection query ... --json")`
     probes to validate source queries before scheduling.
   - Fix connection, SQL, Python, or DuckDB issues before scheduling.

5. Create or update the schedule.
   - Use `workspace_shell("cron create <name> --command \"<workspace-command>\" --cron \"<expr>\" --timeout <seconds> --json")`.
   - Use `workspace_shell("cron list --json")`,
     `workspace_shell("cron get <name> --json")`, and
     `workspace_shell("cron history <name> --json")` to verify.
   - Do not overwrite an existing schedule without user approval.

6. Document operation.
   - State where outputs live.
   - State how to inspect history and failures.
   - State what permissions are required for future runs.

## Verification

Before final response:

- Required connections are visible to the session.
- Pipeline script dry-run succeeded, or the exact blocker is documented.
- Outputs were created or verified.
- Cron expression is valid.
- Schedule was created, updated, or intentionally left as a dry-run artifact.
- History or status command works when a schedule exists.

## Final Response

Return:

- Pipeline name.
- Files created or modified.
- Schedule expression and timezone assumption.
- Output locations.
- Dry-run result.
- Schedule status or history command.
- Remaining setup, permission, or product-contract gaps.

## Boundary With Other Skills

- use `query-and-analyze` when the user only needs one-off analysis or manual
  query authoring
- use `setup-automation` when the user already has a command and only needs
  cron management
- use this skill when the user needs the full scheduled-pipeline shape:
  design, implementation, validation, and scheduling
