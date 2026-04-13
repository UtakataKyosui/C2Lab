#!/bin/bash
# SessionStart hook: harness-toolkit が必要とする CLI ツールの存在確認
# 不足ツールがあれば警告し、harness-setup Agent の利用を促す
set -euo pipefail

TOOLS=("fd" "rg" "jj" "repomix" "semgrep")
OPTIONAL_TOOLS=("rtk" "rust-parallel" "tre" "proto" "knip" "ghasec")
MISSING=()
MISSING_OPTIONAL=()

for tool in "${TOOLS[@]}"; do
  if ! command -v "$tool" &>/dev/null; then
    MISSING+=("$tool")
  fi
done

for tool in "${OPTIONAL_TOOLS[@]}"; do
  if ! command -v "$tool" &>/dev/null; then
    MISSING_OPTIONAL+=("$tool")
  fi
done

if [ ${#MISSING[@]} -eq 0 ] && [ ${#MISSING_OPTIONAL[@]} -eq 0 ]; then
  echo "harness-toolkit: All tools available."
  exit 0
fi

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "harness-toolkit [WARN]: Required tools not found: ${MISSING[*]}"
  echo "  → Run the harness-setup agent to get installation instructions."
  echo "  → Example: 'harness-toolkit の不足ツールをインストールしたい'"
fi

if [ ${#MISSING_OPTIONAL[@]} -gt 0 ]; then
  echo "harness-toolkit [INFO]: Optional tools not found: ${MISSING_OPTIONAL[*]}"
fi

exit 0
