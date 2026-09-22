# Embedded agents with the Python SDK

Use this path when building a Python application that embeds a LangGraph or
LangChain agent with `marcopolo-sdk>=0.3.0`. The application supplies its own
model and credentials. The plugin's MCP server remains a separate surface;
inspect the installed tool schema before selecting arguments.

Install `marcopolo-sdk[langchain]`. The adapter supports
`langchain-core>=0.3.79,<2` and produces asynchronous tools for LangGraph's
`ToolNode`:

```python
from marcopolo import Marcopolo
from marcopolo.toolkit.langchain import langchain_tools

async with Marcopolo(access_token=user_token) as client:
    tools = langchain_tools(client.toolkit)
    # Run the agent while this client is open.
```

`client.toolkit.tools()` provides framework-neutral definitions;
`await client.toolkit.execute(name, arguments)` executes one. These
definitions ship with the SDK. The service publishes the catalog at
`GET /api/v1/toolkit/tools` for other consumers.

## Discover, query, and combine

1. Call `connections_list` and select a connection that advertises `query`.
2. Read `query_guide(connection=...)` and inspect the relevant
   `connection_catalog` levels before authoring queries. Supply `database`
   and then `table` to inspect columns.
3. Call `data_query` with `connection` and exactly one of `query_text` or
   `query_path`. Use `inline=false` for intermediate results. The response
   contains an `operation_id`, total `row_count`, and result-store `relation`,
   without records entering the model context.
4. Join or aggregate those relations by calling `data_query` on connection
   `DUCKDB`. Request `inline=true` and a small `max_rows` for the final answer.
   `max_rows` limits returned records, not the materialized relation.
5. Use `operation_records(operation_id=..., limit=..., offset=...)` when an
   explicit page is needed. `limit` must be between 1 and 5,000 (default 500).
   Those records enter the model context.

`inline` defaults to true. Always set it to false when intermediate records
should stay outside the prompt. The SDK `data_query` arguments are not the
MCP tool's `connection_name`, `query_file`, and `params` arguments.

## Results and failures

The model reads `ToolExecution.text`; the application receives structured
`ToolExecution.data`. LangChain places these in `ToolMessage.content` and
`ToolMessage.artifact`. Keep artifacts out of the model prompt unless their
contents are needed for the answer.

An artifact result can have `row_count=null`; this means its row count is
unknown. Follow the artifact guidance instead of treating it as an empty result.

Failed requests and failed query operations set `ToolExecution.failed=true`
and `ToolMessage.status="error"`. Rejected requests carry `data.error`;
operations that ran and failed preserve their identity and `data.failure`.
Use the failure message or guidance to correct recoverable errors.
Authentication and SDK compatibility failures raise to application code.

## End-user identity and setup

For an embedded customer chatbot, the backend can exchange its namespace
key through `MarcopoloNamespace.issue_user_token(email)` and construct the
client with the returned access token. Each tool call then uses that user's
visibility. Tokens expire after five minutes; application code must obtain
a fresh token and client when needed. Keep namespace keys in the backend.

`connection_setup` starts hosted authorization and returns an authorization
URL for the user. After the user authorizes access, poll
`connection_setup_status` until ready or failed. Never ask the model to
supply provider passwords or refresh tokens as tool arguments.
