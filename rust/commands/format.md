---
name: format
description: Format Rust code using cargo fmt
argument-hint: "[path]"
allowed-tools: [Bash]
---

# Rust Format Command

Format Rust code according to the Rust style guide using `cargo fmt`.

## Execution

Run cargo fmt on specified path or current directory:

```bash
cargo fmt
```

For workspace projects:
- Add `--all` to format all workspace members if `workspace_mode` is "all"

Display formatted files and confirmation message.
