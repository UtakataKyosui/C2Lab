---
name: add-crate
description: Add a new crate to the workspace
argument-hint: "<crate-name> [--lib|--bin]"
allowed-tools: [Bash, Edit, Write]
---

# Add Crate to Workspace Command

Add a new crate to the current Cargo workspace.

## Execution

1. Verify we're in a workspace (check root Cargo.toml has `[workspace]`)

2. Create new crate:
   ```bash
   cargo new --lib <crate-name>  # or --bin for binary
   ```

3. Add to workspace members in root Cargo.toml if not using glob pattern

4. Create basic directory structure and files

5. If workspace has shared dependencies, add them to new crate's Cargo.toml:
   ```toml
   [dependencies]
   common-dep = { workspace = true }
   ```

6. Display success message and next steps

Refer to workspace-management skill for workspace organization patterns.
