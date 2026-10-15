# `connection request`

Use when the connection advertises `request`. Discover its operation IDs and
parameters through the CLI:

For analysis, prefer the source tables documented in `SYNTAX.md` through
`connection query`. That path handles declared pagination and materializes typed
DuckDB relations. `request` provides direct access to individual API operations.

```sh
connection request <name> --describe --json
connection request <name> --describe --operation <operationId> --json
connection request <name> --operation <operationId> --params-json '{"page_size": 2}' --json
```

`--operation` takes the specification's `operationId`. Parameter names are the
generated Python argument names shown by `--describe`; JSON request bodies can
be provided under the `body` argument, for example `{"body":{"query":"example"}}`.
Use the operation schema to choose the body shape (object, array, or scalar). The operation detail
includes parameter documentation and referenced model fields. Marcopolo installs
the matching generated client automatically.

Never supply client transport overrides (names beginning with `_`) or credentials
in arguments. dvREPL injects the connection's saved credential. Generated clients
run with workspace permissions and cannot read the stored credential.

The envelope includes `success`, `operation`, `connection`, `status`, `headers`
and `body`. `body` is already decoded JSON and can be an object, array, scalar
or null; non-JSON response content is a string. HTTP errors retain their status and body with `success: false`;
transport or authorization failures have an `error` without an HTTP status.

Use the CLI response contract when interpreting results. Generated SDK return
types do not constrain the raw body returned by `connection request`.

Each invocation makes one request. Consult the API docs and returned body to
choose subsequent pages; an unfamiliar response is evidence to inspect.
Save useful results to workspace files and materialize selected records in
DuckDB when analysis requires it. This command does not create a relation.
