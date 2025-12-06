---
name: fix
description: Auto-fix common errors using cargo fix
argument-hint: ""
allowed-tools: [Bash, Read, Edit]
---

# Rust Fix Command

Automatically fix compiler warnings and errors using `cargo fix`.

## Execution

```bash
cargo fix --allow-dirty --allow-staged
```

For workspace: Add `--workspace` if configured.

Display:
1. Fixes applied (in table format)
2. Remaining issues that require manual intervention
3. Summary of changes

After fixing, run `cargo check` to verify the fixes worked.
