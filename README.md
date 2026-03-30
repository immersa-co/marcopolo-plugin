# MarcoPolo Plugin for Claude

The MarcoPolo plugin connects Claude to your datasources through the MarcoPolo MCP server and adds skills that solve three problems with raw MCP connections: Claude operating on the wrong workspace, unreliable multi-step query workflows, and tool discovery failures as MCP servers proliferate. See the [plugin documentation](https://docs.marcopolo.dev/getting-started/claude-plugin) for details.

## Installation

### Claude Code

```bash
git clone https://github.com/immersa-co/marcopolo-plugin.git
```

Start Claude Code in the plugin directory or a parent directory. It detects the plugin automatically.

### Claude Desktop / Claude.ai

Plugins require admin privileges. Add this repo to your organization's private plugin marketplace, or download as a zip and upload through Plugins (Preview) settings.

### Verify

Run `/skills` in Claude Code. You should see `query-workflow`, `using-marcopolo`, and `workspace-navigation`.

## What you can do

- **Query any datasource** - Ask questions in natural language. Claude writes and executes the correct SQL, caching results in DuckDB for follow-up analysis.
- **Join data across sources** - Combine results from Snowflake, Salesforce, BigQuery, PostgreSQL, and more in a single analysis.
- **Explore and understand data** - Claude reads your RULES.md business context and navigates schemas before querying.
- **Work with cloud storage** - Browse, download, and process files from S3, Azure Blob, and Google Drive.
- **Build visualizations** - Create dashboards and charts directly from query results.
- **Automate data tasks** - Schedule recurring queries, reports, and pipelines.

## Plugin contents

| Component | Description |
|-----------|-------------|
| **MCP Server** | Connects to `https://mcp.marcopolo.dev` |
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
