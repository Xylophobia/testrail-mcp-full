# TestRail MCP Server

A Model Context Protocol (MCP) server for TestRail that allows interaction with TestRail's API through a standardized protocol.

## Features

- Authentication with TestRail API
- Broad TestRail API coverage through MCP tools
- Paginated list endpoints use the current TestRail response shapes where supported
- Multipart attachment upload and base64 attachment download support
- Support for dynamic filter metadata and dynamic filter payloads on documented run and plan tools
- Full support for the Model Context Protocol
- Compatible with any MCP client (Claude Desktop, Cursor, Windsurf, etc.)

## Supported TestRail API Areas

The server exposes tools for these TestRail API groups:

- Projects: get, list with filters, add, update, delete
- Milestones: get, list with filters, add, update, delete
- Plans: get, list with filters, add, update, close, delete, manage plan entries and plan-entry runs
- Suites: get, list with pagination, add, update, delete with soft mode
- Sections: get, list with suite and pagination filters, add, update, move, delete with soft mode
- Cases: get, list with current filters, history, add, update, bulk update, copy, move, delete
- Runs: get, list with current filters, add, update, close, delete with soft mode
- Tests: get, list with status and label filters, update labels, bulk update labels
- Results: get, list by test/run/case with filters, add single and bulk results
- Datasets: get, list with pagination, add, update, delete
- Variables: list, add, update, delete
- Metadata and lookups: templates, case fields, result fields, case types, priorities, test statuses, case statuses, dynamic filter fields
- Labels: get, list with pagination, update
- Users: get user, get current user, get by email, list, add, update
- Configurations: get groups/configurations, add, update, delete
- Shared steps: get, list with filters, history, add, update, delete
- Attachments: upload to cases, plans, plan entries, results, and runs; list attachments for cases, plans, plan entries, runs, and tests; retrieve and delete attachments
- Reports: list and run project reports and cross-project reports

Known remaining gaps for complete API coverage include roles, BDD import/export, creating case fields, and editing existing results via the newer `edit_result/{result_id}` endpoint.

## Installation
### Manual Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/Xylophobia/testrail-mcp-full.git
   cd testrail-mcp-full
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

## Configuration

The TestRail MCP server requires specific environment variables to authenticate with your TestRail instance. These must be set before running the server.

1. Create a `.env` file in the root directory of the project:
   ```
   TESTRAIL_URL=https://your-instance.testrail.io
   TESTRAIL_USERNAME=your-email@example.com
   TESTRAIL_API_KEY=your-api-key
   ```

   **Important Notes:**
   - `TESTRAIL_URL` should be the full URL to your TestRail instance (e.g., `https://example.testrail.io`)
   - `TESTRAIL_USERNAME` is your TestRail email address used for login
   - `TESTRAIL_API_KEY` is your TestRail API key (not your password)
     - To generate an API key, log in to TestRail, go to "My Settings" > "API Keys" and create a new key

2. Verify that the configuration is loaded correctly:
   ```bash
   uvx testrail-mcp --config
   ```
   
   This will display your TestRail configuration information, including your URL, username, and the first few characters of your API key for verification.

If you're using this server with a client like Claude Desktop or Cursor, make sure the environment variables are accessible to the process running the server. You may need to set these variables in your system environment or ensure they're loaded from the `.env` file.

## Usage

### Running the Server

The server can be run directly using the installed script:

```bash
uvx testrail-mcp
```

This will start the MCP server in stdio mode, which can be used with MCP clients that support stdio communication.

### Using with MCP Clients

#### Codex

Codex supports MCP servers in both the CLI and the IDE extension, and the configuration is shared between them.

Add this to `~/.codex/config.toml`:

```toml
[mcp_servers.testrail]
enabled = true
command = "uvx"
args = ["testrail-mcp"]

[mcp_servers.testrail.env]
TESTRAIL_URL = "https://your-instance.testrail.io"
TESTRAIL_USERNAME = "your-email@example.com"
TESTRAIL_API_KEY = "your-api-key"
```

After updating the config, restart Codex and verify the server is available from your Codex MCP tool list.

#### Claude Desktop

In Claude Desktop, add a new server with the following configuration:

```json
{
  "mcpServers": {
    "testrail": {
      "command": "uvx",
      "args": [
        "testrail-mcp"
      ],
      "env": {
        "TESTRAIL_URL": "https://your-instance.testrail.io",
        "TESTRAIL_USERNAME": "your-email@example.com",
        "TESTRAIL_API_KEY": "your-api-key"
      }
    }
  }
}
```

#### Cursor

In Cursor, add a new custom tool with the following configuration:

```json
{
  "name": "TestRail MCP",
  "command": "uvx",
  "args": [
    "testrail-mcp"
  ],
  "env": {
    "TESTRAIL_URL": "https://your-instance.testrail.io",
    "TESTRAIL_USERNAME": "your-email@example.com",
    "TESTRAIL_API_KEY": "your-api-key"
  }
}
```

#### Windsurf

In Windsurf, add a new tool with the following configuration:

```json
{
  "name": "TestRail MCP",
  "command": "uvx",
  "args": [
    "testrail-mcp"
  ],
  "env": {
    "TESTRAIL_URL": "https://your-instance.testrail.io",
    "TESTRAIL_USERNAME": "your-email@example.com",
    "TESTRAIL_API_KEY": "your-api-key"
  }
}
```

#### Testing with MCP Inspector

For testing and debugging, you can use the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector \
  -e TESTRAIL_URL=<your-url> \
  -e TESTRAIL_USERNAME=<your-username> \
  -e TESTRAIL_API_KEY=<your-api-key> \
  uvx testrail-mcp
```

This will open a web interface where you can explore and test all the available tools and resources.

## Development

This server is built using:

- [FastMCP](https://github.com/jlowin/fastmcp) - A Python framework for building MCP servers
- [Requests](https://requests.readthedocs.io/) - For HTTP communication with TestRail API
- [python-dotenv](https://github.com/theskumar/python-dotenv) - For environment variable management

### Verification

Run the local regression tests and Python compile check before publishing changes:

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile testrail_mcp/*.py tests/*.py
```

The tests focus on request construction for current TestRail endpoint paths, query parameters, soft-delete modes, attachment handling, and selected response transport behavior.

## License

MIT
