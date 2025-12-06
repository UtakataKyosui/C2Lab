---
name: deps
description: Check for outdated dependencies using cargo-outdated
argument-hint: ""
allowed-tools: [Bash]
---

# Dependencies Check Command

Check for outdated dependencies and security vulnerabilities.

## Execution

1. Check if `cargo-outdated` is installed:
   ```bash
   cargo outdated --version || echo "Not installed"
   ```

2. If installed, run:
   ```bash
   cargo outdated --workspace --root-deps-only
   ```

3. Display results in table format:
   | Package | Current | Latest | Kind |
   |---------|---------|--------|------|

4. If `cargo-audit` is available, also check for vulnerabilities:
   ```bash
   cargo audit
   ```

5. Suggest updates for outdated packages.

Refer to cargo-tools skill for dependency management guidance.
