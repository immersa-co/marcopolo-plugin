# MarcoPolo Plugin for Claude and Codex

The MarcoPolo plugin connects Claude and Codex to a secure, persistent remote workspace for working with your company's data — querying connections, joining results across sources, building dashboards, and scheduling automations. It bundles the MarcoPolo MCP server plus shared skills that solve three problems with raw MCP connections: operating on the wrong workspace, unreliable multi-step query workflows, and tool discovery failures as MCP servers proliferate. See the [plugin documentation](https://docs.marcopolo.dev/getting-started) for details.

## Installation

### Claude

#### Claude Code

```bash
git clone https://github.com/immersa-co/marcopolo-plugin.git
```

Start Claude Code in the plugin directory or a parent directory. It detects the plugin automatically.

#### Claude Desktop / Claude.ai

Plugins require admin privileges. Add this repo to your organization's private plugin marketplace, or download as a zip and upload through Plugins (Preview) settings.

#### Verify

Run `/skills` in Claude Code. You should see `using-marcopolo-workspace`, `using-connection-cli`, `setup-connection`, `query-and-analyze`, `build-dashboard`, and `setup-automation`.

### Codex

Codex uses `.codex-plugin/plugin.json` and reuses the same `skills/` and `.mcp.json` files as Claude. The `agents/` directory remains Claude-specific; Codex gets its behavior from the bundled skills and plugin manifest metadata.

For Codex, the recommended setup is a personal install so the plugin is available across projects.

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
4. Verify `marcopolo` appears installed by default or install it manually if your local policy differs.

#### Verify

After installation, confirm the plugin exposes:

- `using-marcopolo-workspace`
- `using-connection-cli`
- `setup-connection`
- `query-and-analyze`
- `build-dashboard`
- `setup-automation`

Also confirm the `marcopolo` MCP server loads from `.mcp.json` when you start a Codex session in this repo.

## How to use it

Once the plugin is installed, use your client normally. The plugin adds the MarcoPolo MCP server plus the shared skills, so you can ask for data work in natural language without manually wiring tools together.

Good first prompts:

- `List the connections available through MarcoPolo and tell me which one looks relevant for revenue reporting.`
- `Install a demo connection so I can try MarcoPolo without my own credentials.`
- `Inspect the schema for the orders table before writing any SQL.`
- `Query monthly revenue for the last 12 months and build a dashboard from the result.`
- `Browse our storage connection, find the latest CSV export, and summarize what is in it.`
- `Schedule a recurring job that refreshes this report every weekday morning.`

Behavior by client:

- **Claude** uses the bundled skills and the `marcopolo` agent in this repo.
- **Codex** uses the shared skills from `skills/` and the MCP server from `.mcp.json`; it does not use the Claude-specific `agents/` directory.

## What you can do

- **Query any connection** - Ask questions in natural language. The assistant writes query files in the workspace and executes them through the `connection` CLI; results are materialized into DuckDB for follow-up analysis.
- **Join across connections** - Combine results from Snowflake, Salesforce, BigQuery, Postgres, and more through the workspace-local DUCKDB connection.
- **Explore schemas** - The assistant refreshes metadata snapshots into `connections/<name>/metadata/` and reads them before writing queries.
- **Work with cloud storage** - Browse, download, and upload files for connections that advertise those capabilities (S3, Azure Blob, Google Drive).
- **Build dashboards** - Author `.dashboard` manifests plus `view.tsx` components and preview them interactively.
- **Schedule recurring jobs** - Use the workspace `cron` CLI for managed recurring queries, refreshes, and pipelines.
- **Install demo connections** - Try MarcoPolo with hosted demo data, no credentials needed.

## Plugin contents

| Component | Description |
|-----------|-------------|
| **MCP Server** | Connects to `https://mcp.marcopolo.dev` |
| **Claude plugin** | `.claude-plugin/plugin.json` |
| **Codex plugin** | `.codex-plugin/plugin.json` |
| **Agent** | `marcopolo` - data analyst with workspace-first defaults (Claude only) |
| **Skills** | `using-marcopolo-workspace`, `using-connection-cli`, `setup-connection`, `query-and-analyze`, `build-dashboard`, `setup-automation` |

## MCP tools

The plugin exposes four MCP tools. Almost everything else happens inside the workspace through the `connection` and `cron` CLIs invoked via `workspace_shell`.

- `workspace_shell(command, timeout=30)` - run any command in the remote workspace
- `connection_setup(type, intent_text=None)` - generate a browser URL for credentialed connection setup
- `install_demo_connection(demo_connection, display_name=None, intent_text=None)` - install a hosted demo connection
- `preview_dashboard(path)` - open the interactive preview UI for a `.dashboard` manifest

## Documentation

- [Plugin documentation](https://docs.marcopolo.dev/getting-started)
- [Getting started](https://docs.marcopolo.dev/getting-started)
- [MCP Tools Reference](https://docs.marcopolo.dev/how-it-works/tools)
- [Security](https://docs.marcopolo.dev/security)

## License

Apache-2.0
