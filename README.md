# MarcoPolo Plugin for Claude and Codex

The MarcoPolo plugin connects Claude and Codex to your datasources through the MarcoPolo MCP server and adds shared skills that solve three problems with raw MCP connections: operating on the wrong workspace, unreliable multi-step query workflows, and tool discovery failures as MCP servers proliferate. See the [plugin documentation](https://docs.marcopolo.dev/getting-started/claude-plugin) for details.

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

Run `/skills` in Claude Code. You should see `query-workflow`, `using-marcopolo`, and `workspace-navigation`.

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

- `query-workflow`
- `using-marcopolo`
- `workspace-navigation`

Also confirm the `marcopolo` MCP server loads from `.mcp.json` when you start a Codex session in this repo.

## How to use it

Once the plugin is installed, use Claude or Codex normally. The plugin adds the MarcoPolo MCP server plus the shared skills, so you can ask for data work in natural language without manually wiring tools together.

Good first prompts:

- `List the datasources available through MarcoPolo and tell me which one looks relevant for revenue reporting.`
- `Use MarcoPolo to inspect the schema for the orders table before writing any SQL.`
- `Query monthly revenue for the last 12 months and build a chart from the result.`
- `Browse our storage datasource, find the latest CSV export, and summarize what is in it.`
- `Create a recurring MarcoPolo automation that refreshes this report every weekday morning.`

Behavior by client:

- **Claude** uses the bundled skills and the `marcopolo` agent in this repo.
- **Codex** uses the shared skills from `skills/` and the MCP server from `.mcp.json`; it does not use the Claude-specific `agents/` directory.

## What you can do

- **Query any datasource** - Ask questions in natural language. The AI writes and executes the correct SQL, caching results in DuckDB for follow-up analysis.
- **Join data across sources** - Combine results from Snowflake, Salesforce, BigQuery, PostgreSQL, and more in a single analysis.
- **Explore and understand data** - The AI reads your RULES.md business context and navigates schemas before querying.
- **Work with cloud storage** - Browse, download, and process files from S3, Azure Blob, and Google Drive.
- **Build visualizations** - Create dashboards and charts directly from query results.
- **Automate data tasks** - Schedule recurring queries, reports, and pipelines.

## Plugin contents

| Component | Description |
|-----------|-------------|
| **MCP Server** | Connects to `https://mcp.marcopolo.dev` |
| **Claude plugin** | `.claude-plugin/plugin.json` |
| **Codex plugin** | `.codex-plugin/plugin.json` |
| **Skills** | `query-workflow`, `using-marcopolo`, `workspace-navigation` |
| **Agent** | Data analyst agent with local/remote filesystem awareness |

## MCP Tools

The plugin provides access to the full MarcoPolo toolset:

- `list_datasources()` - Discover available datasources
- `get_schema()` - Explore datasource structure (databases, tables, columns)
- `query()` - Execute queries against any datasource
- `browse()` / `download()` - Navigate and fetch files from storage
- `execute_command()` - Run shell commands in your secure workspace
- `create_data_view()` - Build dashboards and visualizations
- `generate_connector_url()` - Add new datasources

## Documentation

- [Plugin documentation](https://docs.marcopolo.dev/getting-started/claude-plugin)
- [Getting started](https://docs.marcopolo.dev/getting-started)
- [MCP Tools Reference](https://docs.marcopolo.dev/how-it-works/tools)
- [Security](https://docs.marcopolo.dev/security)

## License

Apache-2.0
