---
name: lint
description: Run cargo clippy to lint Rust code and apply automatic fixes
argument-hint: "[path]"
allowed-tools: [Bash, Read, Edit, Write]
---

# Rust Lint Command

Run `cargo clippy` to check for common mistakes and apply automatic fixes.

## Execution Steps

1. **Determine scope**: If `[path]` argument provided, lint only that file/crate. Otherwise, lint current directory.

2. **Run clippy with auto-fix**:
   ```bash
   cargo clippy --fix --allow-dirty --allow-staged
   ```

   For workspace projects (based on user settings):
   - If `workspace_mode` is "all": Add `--workspace` flag
   - If "current" (default): Lint current crate only

3. **Parse and display results** in table format:
   | File | Line | Issue | Severity | Auto-Fixed |
   |------|------|-------|----------|------------|
   | ... | ... | ... | ... | ✓/✗ |

4. **Apply fixes**: Automatically apply all suggested fixes (based on Phase 3 spec: auto-apply fixes).

5. **Summary**: Display count of issues found and fixed.

## Notes

- This command automatically applies fixes as specified in the design
- Uses `--allow-dirty` to work with uncommitted changes
- Respects workspace settings from `.claude/rust.local.md`
- Refer to error-patterns skill for understanding common issues

Run cargo clippy with automatic fixes and present results in structured format.
