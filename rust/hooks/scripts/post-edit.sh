#!/bin/bash
# Hook script that runs after Edit/Write operations on Rust files
# Automatically formats and lints Rust code

set -euo pipefail

# Get the file path from tool result
FILE_PATH="$1"

# Check if it's a Rust file
if [[ ! "$FILE_PATH" =~ \.rs$ ]]; then
    exit 0  # Not a Rust file, skip
fi

# Check if we're in a Rust project
if [ ! -f "Cargo.toml" ]; then
    exit 0  # Not in a Rust project
fi

# Read settings from .claude/rust.local.md if it exists
AUTO_FORMAT=true
AUTO_LINT=true

if [ -f ".claude/rust.local.md" ]; then
    # Parse YAML frontmatter with flexible spacing
    if grep -qE "^auto_format:[[:space:]]*false" ".claude/rust.local.md"; then
        AUTO_FORMAT=false
    fi
    if grep -qE "^auto_lint:[[:space:]]*false" ".claude/rust.local.md"; then
        AUTO_LINT=false
    fi
fi

# Auto-format if enabled
if [ "$AUTO_FORMAT" = true ]; then
    echo "Formatting Rust code..."
    if ! cargo fmt --check "$FILE_PATH" 2>/dev/null; then
        cargo fmt "$FILE_PATH"
        echo "✓ Code formatted"
    fi
fi

# Auto-lint if enabled
if [ "$AUTO_LINT" = true ]; then
    echo "Linting Rust code for crate containing $FILE_PATH..."
    # Find the crate root by searching for Cargo.toml upwards from the file's directory
    CRATE_DIR=$(dirname "$FILE_PATH")
    while [[ "$CRATE_DIR" != "." && "$CRATE_DIR" != "/" && ! -f "$CRATE_DIR/Cargo.toml" ]]; do
        CRATE_DIR=$(dirname "$CRATE_DIR")
    done

    # Run clippy in the context of the file's crate to ensure correct scope in workspaces
    if [[ -f "$CRATE_DIR/Cargo.toml" ]]; then
        if ! (cd "$CRATE_DIR" && cargo clippy --quiet -- -D warnings 2>&1); then
            echo "! Clippy warnings/errors detected"
            echo "Run /rust:lint to see details and apply fixes"
            exit 1  # Block if errors found (per Phase 3 spec)
        else
            echo "✓ No lint issues"
        fi
    fi
fi

exit 0
