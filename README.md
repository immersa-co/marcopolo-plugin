# MarcoPolo Plugin for Claude and Codex

The MarcoPolo plugin connects Claude and Codex to a secure, persistent remote
workspace for working with company data, querying connections, joining results
across sources, building dashboards, and running scheduled workflows. It
bundles the MarcoPolo MCP server plus shared skills that keep workspace-first
data work consistent across clients.

## Installation

### Claude

#### Claude Code

```bash
git clone https://github.com/immersa-co/marcopolo-plugin.git
```

Start Claude Code in the plugin directory or a parent directory. It detects the
plugin automatically.

#### Claude Desktop / Claude.ai

Plugins require admin privileges. Add this repo to your organization's private
plugin marketplace, or download as a zip and upload through Plugins (Preview)
settings.

#### Verify

Run `/skills` in Claude Code. You should see:

- `using-marcopolo-workspace`
- `using-connection-cli`
- `setup-connection`
- `query-and-analyze`

### Codex

Codex uses `.codex-plugin/plugin.json` and reuses the same `skills/` and
`.mcp.json` files as Claude. The `agents/` directory remains Claude-specific;
Codex gets its behavior from the bundled skills and plugin manifest metadata.

For Codex, the recommended setup is a personal install so the plugin is
available across projects.

```bash
mkdir -p ~/.codex/plugins
git clone https://github.com/immersa-co/marcopolo-plugin ~/.codex/plugins/marcopolo
```

Add or update `~/.agents/plugins/marketplace.json`:

```json
{
  "name": "my-plugins",
  "interface": {
    "displayName": "My Plugins"
  },
  "plugins": [
    {
      "name": "marcopolo",
      "source": {
        "source": "local",
        "path": "./.codex/plugins/marcopolo"
      },
      "policy": {
        "installation": "INSTALLED_BY_DEFAULT",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

Then:

1. Restart Codex.
2. Open the plugin directory in Codex.
3. Select your personal marketplace.
4. Verify `marcopolo` appears installed by default or install it manually if
   your local policy differs.

#### Verify

After installation, confirm the plugin exposes:

- `using-marcopolo-workspace`
- `using-connection-cli`
- `setup-connection`
- `query-and-analyze`

Also confirm the `marcopolo` MCP server loads from `.mcp.json` when you start a
Codex session in this repo.

## Session compatibility

The MarcoPolo MCP server exposes these tools:

- `workspace_shell(command, timeout=30)` for Unix shell commands in
  `/workspace` (files, DuckDB, scripts, git, crontab scheduling, diagnostics)
- `connections_list()`
- `connection_add(type, intent?, timeout?)`
- `connection_describe(connection_name, database?, table?, timeout?)`
- `connection_test(connection_name, timeout?)`
- `connection_browse(connection_name, remote_path="", detailed=false, timeout?)`
- `connection_download(connection_name, remote_path, local_path?, timeout?)`
- `connection_upload(connection_name, local_path, remote_path, timeout?)`
- `connection_edit_context(connection_name, source_file, timeout?)`
- `connection_query(connection_name, query_file? | operation?, params?, input_data?, include_results=false, timeout?)`
- `execution_status(execution_id)`
- `data_query(connection_name, query_file, params?, max_rows?)`
- `install_demo_connection(demo_connection, display_name?, intent_text?)`

Each `connection_*` tool runs exactly that `connection` CLI verb with `--json`
and returns the same result shape as `workspace_shell`. A call that outlives
its `timeout` returns `status: "running"` with an `execution_id`; check it with
`execution_status`.

Generated dashboards, Remote Artifacts, and external app code use `data_query`.
`workspace_shell` is for agent sessions, not the runtime contract for generated
artifacts.

## How to use it

Once the plugin is installed, use your client normally. The plugin adds the
MarcoPolo MCP server plus shared skills, so you can ask for data work in
natural language without manually wiring tools together.

Good first prompts:

- `List the connections available through MarcoPolo and tell me which one looks relevant for revenue reporting.`
- `Install a demo connection so I can try MarcoPolo without my own credentials.`
- `Inspect the schema for the orders table before writing any SQL.`
- `Query monthly revenue for the last 12 months and build a dashboard from the result.`
- `Build a scheduled pipeline that refreshes this report every weekday morning.`

Behavior by client:

- Claude uses the bundled skills and the `marcopolo` agent in this repo.
- Codex uses the shared skills from `skills/` and the MCP server from
  `.mcp.json`; it does not use the Claude-specific `agents/` directory.

## What you can do

- Query any connection.
- Join across connections through the workspace-local DUCKDB connection.
- Explore schemas and refresh metadata snapshots before writing queries.
- Work with cloud storage for connections that advertise those capabilities.
- Build dashboards and generated apps backed by governed MarcoPolo data.
- Build scheduled data and AI workflows.
- Manage recurring workspace jobs through cron.
- Install demo connections.

## Plugin contents

| Component         | Description                                                                                  |
|-------------------|----------------------------------------------------------------------------------------------|
| **MCP Server**    | Connects to `https://mcp.marcopolo.dev`                                                      |
| **Claude plugin** | `.claude-plugin/plugin.json`                                                                 |
| **Codex plugin**  | `.codex-plugin/plugin.json`                                                                  |
| **Agent**         | `marcopolo` - data analyst with workspace-first defaults (Claude only)                       |
| **Skills**        | `using-marcopolo-workspace`, `using-connection-cli`, `setup-connection`, `query-and-analyze` |

## In-workspace guidance

Once a session is running, the workspace's own guidance files are the canonical
instructions for day-to-day operation:

- `/workspace/README.md`
- `/workspace/RULES.md`
- `/workspace/workflows/README.md`

Those files define the preferred tool path, workspace conventions, and the
compatibility fallback for older sessions.

## Documentation

- [Plugin documentation](https://docs.marcopolo.dev/getting-started)
- [Getting started](https://docs.marcopolo.dev/getting-started)
- [MCP Tools Reference](https://docs.marcopolo.dev/how-it-works/tools)
- [Security](https://docs.marcopolo.dev/security)

## License

Apache-2.0
