# Claude MCP Setup Guide

## What is MCP?

Model Context Protocol (MCP) lets Claude Desktop / Claude Code call external APIs as tools. Superset 5.0 ships with a built-in MCP server on port 5008 that exposes its REST API as callable tools.

## Prerequisites

1. Docker containers running (`docker compose up -d`)
2. Claude Desktop installed (or Claude Code with MCP support)
3. Superset health confirmed (`curl http://localhost:8088/health`)

## Configuration

### Claude Desktop

Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "superset": {
      "url": "http://localhost:5008/mcp"
    }
  }
}
```

Restart Claude Desktop after saving.

### Claude Code (CLI)

```bash
claude --mcp-server superset=http://localhost:5008/mcp
```

## Verification

In Claude Desktop, open a new conversation and ask:

```
List all dashboards in Superset
```

Claude should call the MCP tool and return the dashboard list.

## Example Prompts

Once connected, try these:

```
Create a bar chart showing average wait time by triage category from fact_ed_visits
```

```
Add the new chart to the ED Performance Dashboard
```

```
Show me the RLS rules currently configured
```

```
Create a new user 'jane.smith' with the LHD_Manager role
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| MCP server not responding | Check `docker logs superset_app` |
| Auth errors | Verify `MCP_IMPERSONATE_USER=admin` in docker-compose.yml |
| Tools not visible | Restart Claude Desktop after config change |
| Port 5008 not open | Superset may still be initialising — wait 2 min |
