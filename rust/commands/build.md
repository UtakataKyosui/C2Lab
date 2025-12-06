---
name: build
description: Build the Rust project and report errors
argument-hint: "[--release]"
allowed-tools: [Bash]
---

# Rust Build Command

Build the Rust project using `cargo build`.

## Execution

```bash
cargo build [--release]
```

Add `--release` flag if user specified or if argument is `--release`.

For workspace: Add `--workspace` or `-p <crate>` as appropriate.

Display build output including:
1. Compilation progress
2. Any errors (formatted in table)
3. Build time
4. Binary location if successful

If errors occur, trigger the error-fixer agent to suggest fixes.
