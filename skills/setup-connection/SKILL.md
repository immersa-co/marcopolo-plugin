---
name: setup-connection
description: Adds or repairs a connection in the MarcoPolo workspace. Use this skill when the user wants demo data, a new credentialed datasource, or help fixing connection setup or credentials.
---

# Set up a connection

Use this skill when the user needs a new data source in MarcoPolo or when an
existing connection needs credential repair.

## Preferred surfaces

- hosted demo data: `install_demo_connection(...)`
- credentialed connection setup: `connection_setup(...)`
- `connection add --type ...` is a lower-level CLI fallback, not the preferred
  interactive path from an agent session

## Recommended flow

### Option A: install hosted demo data

Use this when the user wants sample data and no user-owned credentials are
required.

```text
install_demo_connection(
  demo_connection="<demo-id-or-natural-language-request>",
  display_name="<optional-friendly-name>",
  intent_text="<optional-clarification>"
)
```

On success:

1. Run `workspace_shell("connection list --json")` to confirm the connection is visible
2. Run `workspace_shell("connection test <name> --json")` if credential behavior is unclear
3. Run `workspace_shell("connection describe <name> --json")` if query authoring needs schema or file metadata
4. Read `connections/<name>/README.md`, `connections/<name>/RULES.md`, and `connections/<name>/SYNTAX.md`

### Option B: add a credentialed connection

Use this when the user has a real database, warehouse, SaaS app, or storage
account.

1. Generate the setup flow with:

   ```text
   connection_setup(type="<canonical-type>", intent_text="<optional free text>")
   ```

2. Surface the returned `url`, `instructions`, and `next_actions` to the user
3. Wait for the user to complete the browser flow
4. Confirm the connection appears with `workspace_shell("connection list --json")`
5. Read the new connection docs under `connections/<name>/`
6. Run `workspace_shell("connection test <name> --json")` when credential behavior is unclear
7. Run `workspace_shell("connection describe <name> --json")` when workspace query authoring needs metadata snapshots

## Post-setup checks

- rerun `workspace_shell("connection list --json")` after setup
- verify credentials with `workspace_shell("connection test <name> --json")`
- seed or refresh metadata with `workspace_shell("connection describe <name> --json")`
- read `connections/<name>/README.md`, `connections/<name>/RULES.md`, and `connections/<name>/SYNTAX.md` before first query authoring

## Failure routing

- if `install_demo_connection(...)` is ambiguous, surface the returned demo
  choices and retry with a specific id
- if `connection_setup(...)` cannot resolve the type, use the returned
  `valid_types` or `suggested_types` and retry
- if `connection test ...` fails after setup, send the user back through
  `connection_setup(...)` for credential repair
- if the connection does not appear in `connection list --json` immediately
  after setup, wait briefly and retry before escalating

## Notes

- use canonical connection types when known
- `connection test ...` is a diagnostic step, not required for the normal MCP
  `connections_list` / `data_query` path
- `connection describe ...` is for workspace query authoring and debugging, not
  for routine runtime data access in dashboards or generated apps
- rerunning `connection describe ...` refreshes metadata snapshots in place
