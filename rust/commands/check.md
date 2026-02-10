---
name: check
description: Run cargo check to verify compilation without building
argument-hint: "[path]"
allowed-tools: [Bash]
---

# Rust Check Command

Run `cargo check` for fast compilation verification without producing binaries.

## Execution

```bash
cargo check --all-targets
```

For workspace: Add `--workspace` if `workspace_mode` is "all".

Parse output and display:
1. Compilation errors in table format
2. Warning count
3. Error count
4. Success/failure status

Refer to error-patterns skill if errors are detected.
