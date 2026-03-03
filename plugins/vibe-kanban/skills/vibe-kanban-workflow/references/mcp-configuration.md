# MCP Configuration for vibe-kanban

## Overview

vibe-kanban centralizes MCP (Model Context Protocol) server configuration for all connected AI agents. Instead of configuring MCP servers in each project's `.mcp.json`, configure them once in vibe-kanban and they propagate to Claude Code sessions automatically.

## Accessing MCP Settings

1. Open vibe-kanban at `http://localhost:3000`
2. Navigate to **Settings** (gear icon)
3. Select **Agent Profiles** → your Claude Code profile
4. Expand the **MCP Servers** section

## Common MCP Server Configurations

### Context7 (Library Documentation)

Provides up-to-date library documentation to Claude Code sessions.

```json
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  }
}
```

### Filesystem (Local File Access)

Grants Claude Code access to specific directories.

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
  }
}
```

### GitHub (Repository Operations)

Enables GitHub API access for PR creation and issue management.

```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"
    }
  }
}
```

### PostgreSQL (Database Access)

Provides read-only database access for schema inspection.

```json
{
  "postgres": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
  }
}
```

### Playwright (Browser Automation)

Enables UI testing and screenshot capture.

```json
{
  "playwright": {
    "command": "npx",
    "args": ["-y", "@playwright/mcp"]
  }
}
```

## Environment Variable Injection

vibe-kanban passes configured environment variables to each Claude Code session. Reference sensitive values via env vars rather than hardcoding:

```json
{
  "my-api": {
    "command": "npx",
    "args": ["-y", "my-mcp-server"],
    "env": {
      "API_KEY": "${MY_API_KEY}"  // resolves from vibe-kanban's environment
    }
  }
}
```

Set the environment variable in vibe-kanban's `.env` file or in the system environment before starting vibe-kanban.

## Per-Task MCP Overrides

For tasks requiring specific MCP access not needed globally:

1. Create a separate agent profile in vibe-kanban (e.g., "Claude Code + DB Access")
2. Add the MCP server to that profile only
3. Assign the task to the specialized agent profile when starting the session

## Verifying MCP Connections

In a Claude Code session started by vibe-kanban, run `/mcp` to see connected servers and available tools. If a server is missing:

1. Check vibe-kanban agent settings for the server configuration
2. Verify the MCP server package is installed (`npx -y` installs on demand)
3. Check vibe-kanban logs for MCP startup errors (terminal where `npx vibe-kanban` runs)

## Recommended MCP Set for Development

Minimal useful set for most development workflows:

```json
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  },
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
    }
  }
}
```

- **context7**: Prevents outdated API usage by providing current docs
- **github**: Enables Claude Code to create PRs and check CI status autonomously
