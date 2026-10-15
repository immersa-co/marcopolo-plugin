# `connection test`

```
workspace_shell("connection test <name> --json")
```

Verify stored credentials for a connection.

For generated API connections, this runs the saved read-only probe against the
published configuration. Where a source table is defined, it checks the response
shape, columns, types, and keys on a bounded sample (up to two pages for GET
collections). Success covers that probe and sample, not every API operation or
all pagination. This command does not run an LLM, repair, or republish the
connector. For mapping failures, share the error with the Marcopolo team rather
than editing the generated client.

## When to run

- Right after a new connection is added (via `connection_setup` or
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
is usually to rerun `connection_setup` to reissue the browser flow.
