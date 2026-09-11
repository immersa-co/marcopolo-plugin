# `connection edit-context`

Replace the shared tenant context for one connection after the user confirms
the proposed change.

```text
workspace_shell("connection edit-context <name> connections/<name>/scratch/<file>.md")
```

The second argument is a workspace Markdown file containing the complete
replacement context. It must resolve inside `/workspace`. The command has no
`--json` flag.

Only connection owners and tenant admins can update context. A successful save
becomes canonical tenant state and is projected to running workspaces for every
user who can see the connection. Already-running model turns retain any context
they loaded before the update.

Do not edit `connections/<name>/RULES.md` directly. It is a managed projection,
so a later tenant refresh will replace direct edits. Draft under
`connections/<name>/scratch/` and submit that file through `edit-context`.

This command does not manage `/workspace/RULES.md`, `local_files`, or `DUCKDB`.
