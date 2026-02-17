#!/bin/bash
# jj git push を --dry-run なしで実行することを防止する Claude Code hook
# 同一セッション内で --dry-run が先に実行されていれば許可する

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo 'Error: required dependency "jq" is not installed or not found in PATH.' >&2
  exit 1
fi

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id')
# Sanitize SESSION_ID to prevent path traversal by removing directory components.
SANITIZED_SESSION_ID=$(basename "$SESSION_ID")

# jj git push を含むコマンドかどうかを判定
if ! echo "$COMMAND" | grep -qE '(^|&&\s*|;\s*)jj\s+git\s+push'; then
  exit 0
fi

STATE_DIR="${TMPDIR:-/tmp}/jj-safe-push"
STATE_FILE="${STATE_DIR}/${SANITIZED_SESSION_ID}"

# --dry-run を含む場合: 実行を許可し、状態を記録
if echo "$COMMAND" | grep -qE 'jj\s+git\s+push\s+.*--dry-run|jj\s+git\s+push\s+--dry-run'; then
  mkdir -p "$STATE_DIR"
  date +%s > "$STATE_FILE"
  exit 0
fi

# --dry-run なしの jj git push: 事前に dry-run が実行済みか確認
if [ -f "$STATE_FILE" ]; then
  # dry-run 実行済み → 許可し、状態をクリア（次回の push でも再度 dry-run を要求）
  rm -f "$STATE_FILE"
  exit 0
fi

# dry-run 未実行 → 拒否
jq -n '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: "jj git push を直接実行することは禁止されています。まず jj git push --dry-run で push 内容を確認してから実行してください。"
  }
}'
