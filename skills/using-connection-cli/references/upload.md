# `connection upload` (capability-gated)

MCP tool: `connection_upload(connection_name, local_path, remote_path, timeout=None)`. It runs this CLI verb with `--json` and returns the result shape of `workspace_shell`; the CLI envelope is `stdout`. The CLI form below also works inside `workspace_shell`, for example in scripts and cron jobs.

```
connection upload <name> --local-path <workspace-file> --remote-path <provider-path> --json
```

Push a workspace file to a provider.

## Capability rule

Only call `upload` if the connection's `capabilities` array (from
`connection list --json`) includes `upload`. Skip it otherwise — uploading
to providers that don't advertise the verb may fail in surprising ways or
have unintended side effects.

## Flags

- `--local-path <workspace-file>` (required) — workspace file path to
  upload.
- `--remote-path <provider-path>` (required) — provider-side destination
  path.
- `--json` — always pass.

## Response shape

```json
{
  "success": true,
  "operation": "upload",
  "source": "<workspace-file>",
  "path": "<provider-path>"
}
```

## When you'd use this

- Pushing a generated artifact back to a shared drive.
- Round-tripping a transformed file (download → process → upload).
- Publishing a CSV/Parquet output produced by a scheduled job.
