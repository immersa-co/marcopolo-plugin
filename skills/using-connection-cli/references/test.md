# `connection test`

MCP tool: `connection_test(connection_name, timeout=None)`. It runs this CLI verb with `--json` and returns the result shape of `workspace_shell`; the CLI envelope is `stdout`. The CLI form below also works inside `workspace_shell`, for example in scripts and cron jobs.

```
connection test <name> --json
```

Verify stored credentials for a connection.

## When to run

- Right after a new connection is added (via `connection_add` or
  `install_demo_connection`).
- After the user changes credentials.
- When a query that used to work starts failing with auth-shaped errors.

There's no need to run `test` before every query — credentials don't
expire on a per-call basis.

## Response shape

On success:

```json
{
  "success": true,
  "operation": "test",
  "message": "Connection test succeeded."
}
```

On failure, surface `error` and `message` to the user. Most failures
indicate incomplete browser setup, wrong host/port, or missing network
access — not something you can fix from the session. The right next step
is usually to rerun `connection_add` to reissue the browser flow.
