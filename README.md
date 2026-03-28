# MarcoPolo Plugin for Claude

The MarcoPolo plugin turns Claude into a data analyst that knows how to work with your company's data. It connects Claude to your datasources through the MarcoPolo MCP server and adds built-in skills that guide Claude through proven data workflows — reading your business context, exploring schemas, writing correct queries, and iterating on results.

## What you can do

- **Query any datasource** — Ask questions in natural language. Claude writes and executes the correct SQL, caching results in DuckDB for follow-up analysis.
- **Join data across sources** — Combine results from Snowflake, Salesforce, BigQuery, PostgreSQL, and more in a single analysis.
- **Explore and understand data** — Claude reads your RULES.md business context and navigates schemas before querying.
- **Work with cloud storage** — Browse, download, and process files from S3, Azure Blob, and Google Drive.
- **Build visualizations** — Create dashboards and charts directly from query results.
- **Automate data tasks** — Schedule recurring queries, reports, and pipelines.

## Plugin contents

| Component | Description |
|-----------|-------------|
| **MCP Server** | Connects to `https://mcp.marcopolo.dev` |
| **Skills** | `query-workflow`, `using-marcopolo`, `workspace-navigation` |
| **Agent** | Data analyst agent with local/remote filesystem awareness |

## MCP Tools

The plugin provides access to the full MarcoPolo toolset:

- `list_datasources()` — Discover available datasources
- `get_schema()` — Explore datasource structure (databases, tables, columns)
- `query()` — Execute queries against any datasource
- `browse()` / `download()` — Navigate and fetch files from storage
- `execute_command()` — Run shell commands in your secure workspace
- `create_data_view()` — Build dashboards and visualizations
- `generate_connector_url()` — Add new datasources

## Documentation

- [Plugin documentation](https://docs.marcopolo.dev/plugin)
- [Getting started](https://docs.marcopolo.dev/getting-started)
- [MCP Tools Reference](https://docs.marcopolo.dev/tools)
- [Security](https://docs.marcopolo.dev/security)

## License

Apache-2.0
