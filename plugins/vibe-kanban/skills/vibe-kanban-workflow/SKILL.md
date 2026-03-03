---
name: vibe-kanban Workflow
description: This skill should be used when a user asks about orchestrating Claude Code with vibe-kanban, running parallel Claude Code sessions, designing tasks for AI coding agents, or managing a kanban board connected to Claude Code. It also applies when the user says "vibe-kanbanのワークフロー", "並列でClaude Codeを使いたい", "タスク設計のコツ", "how to run multiple Claude Code agents", "connect Claude Code to a kanban board", "worktree-based task management", or "AIエージェントのタスクを管理したい".
---

# vibe-kanban Workflow

vibe-kanban is a local-first kanban board designed to orchestrate AI coding agents (Claude Code, Codex, Gemini CLI). Each task runs in an isolated git worktree, enabling parallel development with multiple Claude Code sessions.

## Core Concepts

- **Workspace**: A vibe-kanban project tied to a git repository
- **Issue**: A discrete unit of work assigned to an AI coding agent
- **Session**: A Claude Code run within an isolated git worktree
- **Worktree**: Git working tree created per task to avoid branch conflicts
- **Review**: Diff inspection and PR creation after agent completes work

## Initial Setup

Install and start vibe-kanban:

```bash
npx vibe-kanban
```

The UI opens at `http://localhost:3000` by default. Connect to a git repository by pointing to the project directory.

Configure Claude Code as an agent in vibe-kanban's agent settings, selecting:
- **Agent type**: Claude Code
- **Model**: a Claude Sonnet model for routine tasks, Claude Opus for complex tasks (check available models in vibe-kanban agent settings)

For interactive setup guidance, run `/vibe-kanban:setup` (a slash command provided by this plugin).

## Optimal Task Design

Write issues that Claude Code can execute autonomously without interactive clarification. Good tasks are specific, bounded, and self-contained.

**Effective task structure:**
```
Title: [Action verb] [specific component] [measurable outcome]

Description:
- Context: What already exists, what the current behavior is
- Goal: Exact expected result or behavior
- Acceptance criteria: How to verify completion
- Files affected: Key files/directories to look at (optional)
- Do NOT do: Explicit out-of-scope items
```

**Good examples:**
- "Add rate limiting middleware to POST /api/users endpoint (max 10 req/min)"
- "Fix TypeError in UserCard when profileImage is null"
- "Write unit tests for calculateTax() covering edge cases (zero, negative, large values)"

**Avoid:**
- Vague titles: "Fix the bug", "Improve performance"
- Multi-phase tasks: "Refactor entire auth system and add OAuth"
- Tasks requiring human decisions mid-execution: "Choose between approach A or B"

See `references/task-design-patterns.md` for detailed templates and antipatterns.

## Workflow: Single Task

1. **Create issue** in vibe-kanban UI with a clear title and description
2. **Start task** → vibe-kanban creates a new git worktree and starts a Claude Code session
3. **Monitor** via the session view in vibe-kanban (see Claude Code's progress)
4. **Review** diffs when the session ends
5. **Create PR** from the vibe-kanban interface if changes look good
6. **Close/reopen** if revisions are needed (vibe-kanban keeps the worktree)

## Workflow: Parallel Tasks

Run multiple Claude Code sessions simultaneously for independent work:

1. Create multiple issues for non-overlapping features
2. Start each task sequentially → separate worktrees prevent conflicts
3. Monitor all sessions from the kanban view
4. Review and merge in order of completion

**Critical constraint**: Avoid parallel tasks that modify the same files. Merge conflicts require manual resolution outside vibe-kanban.

See `references/parallel-workflow.md` for patterns like feature slicing and independent module strategy.

## Session Management Best Practices

**Before starting a task:**
- Check if vibe-kanban is running at `http://localhost:3000`
- Verify no uncommitted changes in the main worktree that would block task creation
- Ensure issue description is complete before starting (Claude Code cannot ask follow-up questions during automated sessions)

**During a session:**
- Avoid manually editing files in the task's worktree while Claude Code is running
- Use vibe-kanban's session view to observe progress rather than interrupting
- Let the session complete before reviewing; premature termination may leave inconsistent state

**After session completion:**
- Review the full diff before accepting
- Check generated tests actually pass (`Status` section in the review view)
- Look for unintended side effects in adjacent files

## MCP Integration

This plugin includes a `.mcp.json` that connects Claude Code directly to vibe-kanban's MCP server:

```bash
npx vibe-kanban@latest --mcp
```

When the plugin is enabled, the `vibe_kanban` MCP server starts automatically. Use `/mcp` to verify available tools (e.g., listing tasks, updating status, creating issues).

**Using MCP tools to manage tasks:**
- List current issues and their status via MCP tools
- Update task status (e.g., move to Review) directly from a Claude Code session
- Create new issues without opening the browser UI

vibe-kanban also centralizes MCP server configuration for all connected agents. Configure additional MCP servers once in vibe-kanban's agent settings under `MCP Servers` and they propagate to all Claude Code sessions automatically.

See `references/mcp-configuration.md` for common MCP server configurations to add to vibe-kanban.

## Task Status Lifecycle

| Status | Meaning | Next Actions |
|--------|---------|--------------|
| **Backlog** | Not yet started | Prioritize, refine description |
| **In Progress** | Agent running | Monitor, wait for completion |
| **Review** | Agent done, awaiting review | Inspect diff, run tests |
| **Done** | Reviewed and merged | Close issue |
| **Cancelled** | Dropped or superseded | Archive |

Move tasks through statuses manually after reviewing completed work. vibe-kanban does not auto-close tasks.

## Troubleshooting Common Issues

**Session hangs or produces no output:**
- Check if Claude Code has an auth token (`~/.claude/credentials`)
- Verify the model specified in agent config is accessible
- Restart the session from vibe-kanban (the worktree is preserved)

**Worktree conflict on task start:**
- Indicates another task is using the same branch name
- Delete stale worktrees via vibe-kanban UI or `git worktree prune`

**Diff is empty after session:**
- Claude Code may have hit a clarification loop (issue description was ambiguous)
- Refine the issue and restart

