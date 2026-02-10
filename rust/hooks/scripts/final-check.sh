#!/bin/bash
# Hook script that runs before conversation compaction
# Performs final validation checks on the Rust project

set -euo pipefail

# Check if we're in a Rust project
if [ ! -f "Cargo.toml" ]; then
    exit 0  # Not in a Rust project
fi

echo "=== Running final Rust project checks ==="
echo

# Check compilation
echo "Checking compilation..."
if cargo check --quiet; then
    echo "✓ Project compiles successfully"
else
    echo "! Compilation errors detected"
    echo "Fix errors before ending session"
    exit 1  # Block if compilation fails
fi

# Check formatting
echo "Checking formatting..."
if cargo fmt -- --check; then
    echo "✓ Code is properly formatted"
else
    echo "! Code formatting issues detected"
    echo "Run: cargo fmt"
fi

# Check for workspace issues if this is a workspace
if grep -q "^\[workspace\]" Cargo.toml 2>/dev/null; then
    echo "Checking workspace consistency..."

    # Check for duplicate dependencies
    DUPLICATES=$(cargo tree --duplicates --edges normal 2>/dev/null | grep -v "^$" || true)
    if [ -z "$DUPLICATES" ]; then
        echo "✓ No duplicate dependencies"
    else
        echo "! Duplicate dependencies found:"
        echo "$DUPLICATES"
    fi
fi

echo
echo "=== Final checks complete ==="
exit 0
