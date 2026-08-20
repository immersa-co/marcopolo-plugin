# MarcoPolo Plugin for Claude and Codex

The MarcoPolo plugin connects Claude and Codex to a secure, persistent remote
workspace for working with company data, querying connections, joining results
across sources, building dashboards, and running scheduled workflows. It
bundles the MarcoPolo MCP server plus shared skills that keep workspace-first
data work consistent across clients.

## Installation

### Claude

#### Claude Code

Install MarcoPolo from the MarcoPolo marketplace:

```bash
claude plugin marketplace add immersa-co/marcopolo-plugins
claude plugin install marcopolo@marcopolo-plugins
```

Third-party marketplaces do not auto-update by default. In Claude Code, open
`/plugin`, select **Marketplaces**, choose `marcopolo-plugins`, and enable
auto-update. Background updates can take up to ten minutes after startup; run
`/reload-plugins` when prompted or start a new session.

Organization administrators can register the marketplace and enable updates in
managed settings:

```json
{
  "extraKnownMarketplaces": {
    "marcopolo-plugins": {
      "source": {
        "source": "github",
        "repo": "immersa-co/marcopolo-plugins"
      },
      "autoUpdate": true
    }
  }
}
```

Each user still installs the externally sourced plugin once with the command
above. To force an update immediately:

```bash
claude plugin marketplace update marcopolo-plugins
claude plugin update marcopolo@marcopolo-plugins
```

For local plugin development, clone the repository and load it explicitly for
the session:

```bash
git clone https://github.com/immersa-co/marcopolo-plugin.git
claude --plugin-dir ./marcopolo-plugin
```

Development-directory loading uses the checkout in place. Pull changes and
start a new session to test a newer revision.

#### Claude Desktop / Claude.ai

Plugins require admin privileges. Add this repo to your organization's private
plugin marketplace, or download as a zip and upload through Plugins (Preview)
settings.

#### Verify

Run `/plugin details marcopolo@marcopolo-plugins` in Claude Code. The component
inventory should include:

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

Newer MarcoPolo sessions may expose the preferred product data tools:

- `connections_list`
- `data_query`

Older sessions may expose only `workspace_shell`. Core querying still works in
those sessions through the compatibility path:

- `workspace_shell("connection list --json")`
- bounded `workspace_shell("connection query ... --json")`

The plugin skills and workspace guides are written to prefer the product data
tools when available and fall back to `workspace_shell` when they are not.

Generated dashboards, Remote Artifacts, and external app code should prefer
`data_query` when the product surface exposes it. `workspace_shell` is the
agent-session fallback, not the runtime contract for generated artifacts.

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
