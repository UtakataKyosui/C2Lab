---
name: workspace
description: Analyze and display workspace structure and health
argument-hint: ""
allowed-tools: [Bash, Read]
---

# Workspace Analysis Command

Analyze Cargo workspace structure, dependencies, and configuration.

## Execution

1. Run the workspace-info script:
   ```bash
   ${CLAUDE_PLUGIN_ROOT}/skills/cargo-tools/scripts/workspace-info.sh
   ```

2. Additional analysis:
   - Check for duplicate dependencies: `cargo tree --duplicates`
   - List workspace members: `cargo metadata --format-version 1`
   - Check workspace configuration in root Cargo.toml

3. Display workspace structure diagram showing crate relationships

4. Provide recommendations for:
   - Using workspace dependencies if not already
   - Fixing duplicate dependencies
   - Improving workspace organization

Refer to workspace-management skill for detailed guidance.
