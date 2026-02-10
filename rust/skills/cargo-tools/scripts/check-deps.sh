#!/bin/bash
# Comprehensive dependency health check for Rust projects
# Checks for outdated dependencies and security vulnerabilities

set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "=== Rust Dependency Health Check ==="
echo

# Check if we're in a Rust project
if [ ! -f "Cargo.toml" ]; then
    echo -e "${RED}Error: No Cargo.toml found in current directory${NC}"
    exit 1
fi

# Check for cargo-outdated
if ! command -v cargo-outdated &> /dev/null; then
    echo -e "${YELLOW}Warning: cargo-outdated not installed${NC}"
    echo "Install with: cargo install cargo-outdated"
    OUTDATED_CHECK=false
else
    OUTDATED_CHECK=true
fi

# Check for cargo-audit
if ! command -v cargo-audit &> /dev/null; then
    echo -e "${YELLOW}Warning: cargo-audit not installed${NC}"
    echo "Install with: cargo install cargo-audit"
    AUDIT_CHECK=false
else
    AUDIT_CHECK=true
fi

echo

# Run outdated check
if [ "$OUTDATED_CHECK" = true ]; then
    echo -e "${GREEN}Checking for outdated dependencies...${NC}"
    if cargo outdated --workspace --root-deps-only; then
        echo -e "${GREEN}✓ All dependencies are up to date${NC}"
    else
        echo -e "${YELLOW}! Some dependencies are outdated${NC}"
    fi
    echo
fi

# Run security audit
if [ "$AUDIT_CHECK" = true ]; then
    echo -e "${GREEN}Checking for security vulnerabilities...${NC}"
    if cargo audit; then
        echo -e "${GREEN}✓ No known vulnerabilities found${NC}"
    else
        echo -e "${RED}! Security vulnerabilities detected${NC}"
        echo -e "${YELLOW}Run 'cargo audit fix' to attempt automatic fixes${NC}"
    fi
    echo
fi

# Check for duplicate dependencies
echo -e "${GREEN}Checking for duplicate dependencies...${NC}"
DUPLICATES=$(cargo tree --duplicates --edges normal 2>/dev/null | grep -v "^$" || true)
if [ -z "$DUPLICATES" ]; then
    echo -e "${GREEN}✓ No duplicate dependencies found${NC}"
else
    echo -e "${YELLOW}! Duplicate dependencies detected:${NC}"
    echo "$DUPLICATES"
    echo
    echo -e "${YELLOW}Consider updating dependencies to use consistent versions${NC}"
fi

echo
echo "=== Dependency Check Complete ==="
