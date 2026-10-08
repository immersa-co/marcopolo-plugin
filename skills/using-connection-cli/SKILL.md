---
name: using-connection-cli
description: Reference for the in-workspace `connection` CLI — verb shape, JSON envelope, the capability rule, and per-verb flag details. Use this skill whenever any `connection` verb (`list`, `add`, `test`, `describe`, `query`, `browse`, `download`, `upload`, `edit-context`) is about to run, when looking up flags, when checking whether a verb is allowed by a connection's capabilities, or when reading the JSON response. Consult it even for routine commands — guessing flag names or capability-gating leads to wasted work and surprising failures.
---

# Using the `connection` CLI

The `connection` CLI is the verb surface for all connection work inside
the MarcoPolo workspace. From a session, each verb has a dedicated MCP tool
that runs exactly that verb with `--json`:

| Verb | MCP tool |
|---|---|
| `list` | `connections_list()` |
| `add` | `connection_add(type, intent?, timeout?)` |
| `test` | `connection_test(connection_name, timeout?)` |
| `describe` | `connection_describe(connection_name, database?, table?, timeout?)` |
| `query` | `connection_query(connection_name, query_file? \| operation?, params?, input_data?, include_results=false, timeout?)` |
| `browse` | `connection_browse(connection_name, remote_path="", detailed=false, timeout?)` |
| `download` | `connection_download(connection_name, remote_path, local_path?, timeout?)` |
| `upload` | `connection_upload(connection_name, local_path, remote_path, timeout?)` |
| `edit-context` | `connection_edit_context(connection_name, source_file, timeout?)` |

Each `connection_*` tool returns the same result shape as `workspace_shell`:
`execution_id`, `status` (`running`, `succeeded`, `failed`), `exit_code`,
`stdout` (the CLI JSON envelope), `stderr`, `failure`, and `next_actions`. A
call that outlives `timeout` returns `status: "running"` with an
`execution_id`; check it with `execution_status(execution_id)`.

The CLI form `connection <verb> [args] --json` also works inside
`workspace_shell`, which is how scripts and cron jobs invoke it. `edit-context`
intentionally has no `--json` flag.

## JSON envelope

Every `--json` response has at least:

```json
{ "success": true | false, "operation": "<verb>", ... }
```

On failure: `error`, usually `message`, and often `next_actions` and
(for unknown types) `suggested_types`. On success: verb-specific fields
documented in the per-verb references below.

## Capability rule

`connection list --json` returns each connection's `capabilities` array.
That list is **authoritative** — never call `browse`, `download`, or
`upload` on a connection unless the verb appears in its capabilities.

The reason: capabilities depend on connection type, the user's auth
state, and platform configuration. Calling a non-advertised verb wastes
work, may produce confusing errors, and clutters the workspace's audit
trail. The `connections/<name>/README.md` file mirrors the same
capabilities — both come from the same source.

## Verbs at a glance

| Verb | What it does | Reference |
|---|---|---|
| `list` | Discover connections + capabilities | `references/list.md` |
| `add` | Get a browser setup URL for a credentialed connection | `references/add.md` |
| `test` | Verify stored credentials | `references/test.md` |
| `describe` | Write metadata snapshots into `connections/<name>/metadata/` | `references/describe.md` |
| `query` | Execute a saved query file; materialize result into DuckDB | `references/query.md` |
| `browse` (gated) | List provider-side files for storage connections | `references/browse.md` |
| `download` (gated) | Fetch a provider file into the workspace | `references/download.md` |
| `upload` (gated) | Push a workspace file to the provider | `references/upload.md` |
| `edit-context` | Replace shared tenant context from a workspace Markdown file | `references/edit-context.md` |

Read the per-verb reference (it opens with the matching MCP tool and its argument names) before running a verb you haven't run
recently, especially for flags. The references include the exact
response shape, common pitfalls, and follow-on commands.

**`connection query` — three facts that cause most retries:**
- **Path:** `--file` resolves from `/workspace`, ignoring cwd. Always pass
  `connections/<name>/queries/<file>`; a bare `queries/<file>` fails with
  "No such file or directory" even if the file was just created.
- **Rows vs. handle:** by default a query returns only the relation handle
  (`relation_name` + `row_count` + `column_count`), not the rows. Pass
  `--include-results` to get the rows in `data`; add a SQL `LIMIT` for large
  results, or query the relation in DuckDB.
- **Response:** `data` is a JSON-encoded *string* — call `json.loads` on it
  to get records; `rows` in the envelope is an int count, not a record list.
  The full result lives in DuckDB as `relation_name`.

See `references/query.md` for the full flag contract and response shape.

## Self-discovery

When in doubt, ask the CLI directly through the workspace shell:

```
workspace_shell("connection --help")
workspace_shell("connection <verb> --help")
```

These are the live source of truth for flags. Prefer them over guessing
or relying on the references if the workspace platform may have moved
ahead of this skill.

## Pointers

- adding a connection end to end → `setup-connection`
- writing and running a query → `query-and-analyze`
- workspace layout and where files belong → `using-marcopolo-workspace`
