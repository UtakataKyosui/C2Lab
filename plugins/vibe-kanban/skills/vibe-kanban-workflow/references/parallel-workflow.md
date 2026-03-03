# Parallel Workflow Strategies for vibe-kanban

## Core Principle: Worktree Isolation

Each vibe-kanban task runs in its own git worktree—a separate working directory with its own branch. This means:
- Multiple Claude Code sessions can run simultaneously
- No file system conflicts between tasks
- Each session's changes are isolated until explicitly merged

**Safe to parallelize**: Tasks touching completely different files or modules
**Unsafe to parallelize**: Tasks that edit the same files (merge conflicts on PR creation)

---

## Strategy 1: Feature Slicing (Recommended)

Divide work along feature boundaries rather than layer boundaries.

**Example: Adding a "Comments" feature**

✅ **Parallel-safe breakdown (feature slices):**
- Task A: "Add comments table and migration for the comments feature"
- Task B: "Add GET /api/posts/:id/comments endpoint"
- Task C: "Add POST /api/posts/:id/comments endpoint"
- Task D: "Add CommentList component to PostDetail page"

Each task touches distinct files. Tasks B and C both touch routes, so run sequentially or split by file.

❌ **Not parallel-safe (layer slices):**
- Task A: "Add all backend API for comments" (routes, models, migrations)
- Task B: "Add all frontend UI for comments" (components, state, API calls)

Frontend task B will need to call the API from Task A—sequential dependency.

---

## Strategy 2: Independent Module Strategy

Identify genuinely independent modules and run one task per module.

**Example project structure:**
```
src/
  auth/          ← Task A (auth refactor)
  payments/      ← Task B (add Stripe integration)
  reporting/     ← Task C (add CSV export)
  notifications/ ← Task D (add email templates)
```

Each module has its own directory with minimal cross-dependencies. Safe to run all four tasks in parallel.

**Dependency check before parallelizing:**
1. Does Task B import from Task A's module? → Sequential
2. Do both tasks modify `package.json`? → Sequential (lock file conflicts)
3. Do both tasks modify shared config files? → Sequential
4. Do both tasks modify shared utility files? → Sequential

---

## Strategy 3: Sequential Pipeline

When tasks have dependencies, use vibe-kanban's column ordering as a visual pipeline.

```
Backlog → In Progress → Review → Done
```

Start Task B only after Task A reaches "Done" (or at least "Review" if B doesn't depend on A's final state).

**Example pipeline:**
```
Day 1:
  Task A: "Add User model and migration" → In Progress

Day 1 afternoon (after A is reviewed):
  Task B: "Add UserService with CRUD methods" → In Progress (depends on A's model)
  Task C: "Add user avatar upload endpoint" → In Progress (independent of B)
```

---

## Strategy 4: Branch-per-Experiment

Use vibe-kanban for A/B implementation experiments:

- Task A: "Implement caching using Redis"
- Task B: "Implement caching using in-memory LRU cache"

Both run in isolation. Review both diffs, pick the better one, close the other.

---

## Conflict Detection Checklist

Before starting parallel tasks, verify:

- [ ] Tasks do not share modified files (check `Files to Check` sections)
- [ ] Tasks do not both add dependencies to `package.json` / `Cargo.toml` / etc.
- [ ] Tasks do not both modify `schema.prisma` or migration files
- [ ] Tasks do not both touch shared configuration (`tsconfig.json`, `vite.config.ts`, etc.)
- [ ] Tasks do not both modify environment variable definitions (`.env.example`)
- [ ] Tasks do not both change shared utility functions

---

## Managing Stale Worktrees

After completing or abandoning a task, vibe-kanban keeps the worktree. Clean up periodically:

**Via vibe-kanban UI**: Select completed task → "Delete worktree" button

**Via git CLI** (for abandoned tasks):
```bash
git worktree list          # see all worktrees
git worktree remove <path> # remove specific worktree
git worktree prune         # remove worktrees whose directories are gone
```

**Automatic cleanup**: Set `DISABLE_WORKTREE_CLEANUP=false` in vibe-kanban environment (default behavior cleans up on task deletion).

---

## Monitoring Parallel Sessions

vibe-kanban's kanban view shows all active sessions at once. Check:
- **Green indicator**: Session is actively running (Claude Code is working)
- **Yellow indicator**: Session is idle (Claude Code completed or is waiting)
- **Red indicator**: Session errored (check session log)

For sessions running > 30 minutes without output, inspect the session log. Long silences often indicate:
- Claude Code is in a loop requesting clarification
- The task requires information not provided in the description
- Model rate limiting

---

## Merging Parallel Work

After multiple parallel tasks complete:

1. Review each diff independently in vibe-kanban
2. Merge the task with no dependencies first
3. For dependent tasks, rebase or update the branch against the merged base before review
4. Use vibe-kanban's "Create PR" flow for each task
5. Merge PRs in dependency order

**Rebase flow for a task that needs updating:**
```bash
cd <task-worktree-path>  # path shown in vibe-kanban task detail
git fetch origin
git rebase origin/main   # or your base branch
# Resolve conflicts if any
git push --force-with-lease
```

Then return to vibe-kanban to review the updated diff.
