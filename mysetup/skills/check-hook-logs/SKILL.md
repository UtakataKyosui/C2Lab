---
name: check-hook-logs
description: Checks and displays the integrated Claude Code hooks logs. Use this skill when troubleshooting hook behavior, investigating prompt evaluations, reviewing security warnings, or analyzing session statistics. The logs are stored in ~/.claude/hook-logs/ and contain information about prompt quality scores, command validations, MCP tool usage, and session activities.
---

# Check Hook Logs

Displays and analyzes the integrated Claude Code hooks logs to troubleshoot issues or review hook activity.

## When to Use This Skill

- When troubleshooting why prompts are being blocked or allowed
- To review bash command security warnings
- To analyze MCP tool usage patterns
- To check session statistics and activity logs
- When investigating unexpected hook behavior

## Instructions

1. **Check if the logs directory exists**:
   ```bash
   ls -la ~/.claude/hook-logs/
   ```

2. **List recent log files**:
   ```bash
   ls -lht ~/.claude/hook-logs/ | head -20
   ```

3. **Display recent log entries**:
   ```bash
   tail -50 ~/.claude/hook-logs/hook.log
   # For session stats, check the JSON files:
   # ls -lht ~/.claude/hook-logs/session-*.json | head -5
   # cat ~/.claude/hook-logs/session-<session_id>.json | jq .
   ```

4. **Search for specific events** (if requested by user):
   - Prompt evaluations: `grep -i "prompt" ~/.claude/hook-logs/*.log`
   - Security warnings: `grep -i "destructive\|security" ~/.claude/hook-logs/*.log`
   - MCP tool usage: `grep -i "mcp\|tool" ~/.claude/hook-logs/*.log`
   - Session stats: `grep -i "session\|stats" ~/.claude/hook-logs/*.log`

5. **Analyze and report**:
   - Summarize the types of events logged
   - Highlight any errors or warnings
   - Show relevant log entries based on user's query
   - Suggest actions if issues are found

## Log Information

The hooks log the following events:
- **Prompt Evaluations**: Quality scores and pass/fail status
- **Bash Command Validation**: Security level and warnings for destructive commands
- **MCP Tool Tracking**: Tool usage categorization (deployment, data, search, etc.)
- **File Operations**: Format/lint activities on Rust files
- **Session Statistics**: Session start/stop, command counts, tool usage

## Log File Naming

Log files are typically named:
```
hook.log
```

## Troubleshooting

If no logs are found:
- Check that hooks are properly configured in `hooks.json`
- Verify the binary exists at the configured path
- Ensure hooks have been triggered at least once
- Check file permissions on `~/.claude/hook-logs/` directory

If logs show errors:
- Review error messages for specific issues
- Check that the hooks binary has proper permissions
- Verify all dependencies are installed
- Consider rebuilding the hooks with the `build-hooks` skill
