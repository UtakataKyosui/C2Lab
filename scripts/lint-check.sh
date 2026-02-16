#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--fix" ]]; then
    uvx ruff check --fix .
    uvx ruff format .
    echo "Lint & Format: fixed"
else
    uvx ruff check .
    uvx ruff format --check .
    echo "Lint & Format: OK"
fi
