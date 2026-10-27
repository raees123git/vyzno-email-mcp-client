# LangGraph Email

A command-line email assistant using Gemini and MCP tools to create drafts and send emails through Vyzno.

## Setup

Requires Python 3.12+, uv, and a running email MCP server.

Install dependencies:

```powershell
uv sync
```

Create a `.env` file:

```dotenv
GOOGLE_API_KEY=your-google-api-key
GEMINI_MODEL=your-gemini-model
MCP_URL=http://127.0.0.1:8000/mcp
VYZNO_COOKIE=your-cookie-header
VYZNO_CSRF_TOKEN=your-csrf-token
VYZNO_MAILBOX_ID=your-mailbox-id
```

Keep `.env` private. Set `MCP_TOKEN` if the MCP server requires authentication.

## Run

Start the MCP server from its project folder:

```powershell
uv run python -m mcp_server_email.server
```

Then start this application from the `langgraph-email` folder:

```powershell
uv run python -m langgraph_email.app
```

Enter your email request. Press Ctrl+C to stop.

## Flow

```text
User → Gemini agent → MCP tools → Vyzno → texinity-mail
```

The agent asks for missing information and calls the appropriate tools. Sending creates a draft first, then sends it using the returned draft ID.