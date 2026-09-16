# `connection edit-context`

Replace the shared tenant context for one connection after the user confirms
the proposed change.

```text
workspace_shell("connection edit-context <name> connections/<name>/scratch/<file>.md")
```

The second argument is a workspace Markdown file containing the complete
replacement context. It must resolve inside `/workspace`. The command has no
`--json` flag. Start from the current `connections/<name>/RULES.md` unless the
user intentionally wants to replace all existing context.

Only connection owners and tenant admins can update context. A successful save
becomes canonical tenant state and is projected to running workspaces for every
user who can see the connection. Already-running model turns retain any context
they loaded before the update.

Do not edit `connections/<name>/RULES.md` directly. It is a managed projection,
so direct edits are not durable and may be overwritten. Users can update it in
the Marcopolo UI; agents should draft under `connections/<name>/scratch/` and
submit that file through `edit-context`.

This command does not manage `/workspace/RULES.md`, `local_files`, or `DUCKDB`.
