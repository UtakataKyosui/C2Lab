#!/bin/bash
# Display workspace structure and member information

set -euo pipefail

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== Cargo Workspace Information ==="
echo

# Check if we're in a workspace
if ! grep -q "^\[workspace\]" Cargo.toml 2>/dev/null; then
    echo -e "${YELLOW}Not a workspace (single crate project)${NC}"
    if [ -f "Cargo.toml" ]; then
        NAME=$(grep "^name" Cargo.toml | head -1 | cut -d'"' -f2)
        VERSION=$(grep "^version" Cargo.toml | head -1 | cut -d'"' -f2)
        echo "Package: $NAME"
        echo "Version: $VERSION"
    fi
    exit 0
fi

echo -e "${GREEN}Workspace detected${NC}"
echo

# List workspace members
echo -e "${BLUE}Workspace Members:${NC}"
if command -v jq &> /dev/null; then
    cargo metadata --format-version 1 --no-deps 2>/dev/null | \
        jq -r '.workspace_members[]' | \
        awk '{printf "  - %s (v%s)\n", $1, $2}'
else
    # Fallback without jq - parse members array more robustly
    awk '/^\[workspace\]/,/^\[/ {
        if ($0 ~ /members[[:space:]]*=/) { in_members=1; next }
        if (in_members && $0 ~ /\]/) { exit }
        if (in_members && $0 ~ /"/) {
            gsub(/.*"/, ""); gsub(/".*/, "")
            if ($0 != "") print "  - " $0
        }
    }' Cargo.toml
fi

echo

# Show dependency tree summary
echo -e "${BLUE}Dependency Overview:${NC}"
echo "  Total dependencies (including transitive):"
cargo tree --workspace --edges normal 2>/dev/null | wc -l | xargs echo "   "

echo

# Check for workspace-level configurations
echo -e "${BLUE}Workspace Configuration:${NC}"

if grep -q "^\[workspace.dependencies\]" Cargo.toml; then
    echo -e "  ${GREEN}✓ Using workspace dependencies${NC}"
    DEP_COUNT=$(grep -A 100 "^\[workspace.dependencies\]" Cargo.toml | grep "=" | grep -v "^\[" | wc -l)
    echo "    Shared dependencies: $DEP_COUNT"
else
    echo -e "  ${YELLOW}○ No workspace dependencies defined${NC}"
fi

if grep -q "^\[workspace.package\]" Cargo.toml; then
    echo -e "  ${GREEN}✓ Using workspace package metadata${NC}"
else
    echo -e "  ${YELLOW}○ No workspace package metadata${NC}"
fi

if grep -q "^\[workspace.lints\]" Cargo.toml; then
    echo -e "  ${GREEN}✓ Using workspace lints${NC}"
else
    echo -e "  ${YELLOW}○ No workspace lints defined${NC}"
fi

echo

# Show build profile info
if grep -q "^\[profile\." Cargo.toml; then
    echo -e "${BLUE}Custom Build Profiles:${NC}"
    grep "^\[profile\." Cargo.toml | sed 's/\[profile\.\(.*\)\]/  - \1/'
    echo
fi

echo "=== End of Workspace Info ==="
