---
name: using-connection-cli
description: Reference for the in-workspace `connection` CLI. Use this skill when looking up available verbs, flags, response shape, capability-gated behavior, or live help for `connection` commands.
---

# Using the `connection` CLI

This is the dedicated `connection` command reference skill. Keep detailed
verb, flag, and response-shape guidance here rather than spreading it across
task-oriented skills or workflow docs.

Run the CLI through `workspace_shell(...)`:

```text
workspace_shell("connection <verb> [args] --json")
```

Always prefer `--json` unless a workflow explicitly needs another format.

## Capability rule

`workspace_shell("connection list --json")` returns each connection's
`capabilities` array. That list is authoritative: do not call `browse`,
`download`, or `upload` unless the verb appears in the selected connection's
capabilities.

## Verbs at a glance

| Verb | What it does | Reference |
|---|---|---|
| `list` | Discover connections and capabilities | `references/list.md` |
| `add` | Get a browser setup URL for a credentialed connection | `references/add.md` |
| `test` | Verify stored credentials | `references/test.md` |
| `describe` | Write metadata snapshots into `connections/<name>/metadata/` | `references/describe.md` |
| `query` | Execute a saved query file and materialize the result into DuckDB | `references/query.md` |
| `browse` | List provider-side files for storage connections | `references/browse.md` |
| `download` | Fetch a provider file into the workspace | `references/download.md` |
| `upload` | Push a workspace file to the provider | `references/upload.md` |

## Response shape

Every `--json` response includes at least:

```json
{ "success": true | false, "operation": "<verb>", ... }
```

On failure, expect `error` and usually `message`. On success, use the
per-verb references for the exact payload shape.

## Live help

Use live CLI help as the source of truth when flags may have changed:

```text
workspace_shell("connection --help")
workspace_shell("connection <verb> --help")
```
