#!/bin/bash
# PreCompact hook: コンテキスト圧縮前にコードベース全体のスナップショットを生成
# コンテキストが失われる前に repomix でフルスナップショットを保存する
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# repomix が利用可能か確認
if ! command -v repomix &>/dev/null; then
  exit 0
fi

# ファイル数が多すぎる場合はスキップ（タイムアウト防止）
FILE_COUNT=$(find "$PROJECT_DIR" -type f \
  ! -path "*/.git/*" \
  ! -path "*/.jj/*" \
  ! -path "*/node_modules/*" \
  2>/dev/null | wc -l || echo 0)
if [ "$FILE_COUNT" -gt 5000 ]; then
  echo "harness-toolkit [context]: Skipping full snapshot (project has $FILE_COUNT files, threshold: 5000)."
  exit 0
fi

# フルスナップショットを生成
OUTPUT_FILE="$PROJECT_DIR/CONTEXT_FULL.md"
repomix \
  --output "$OUTPUT_FILE" \
  --style markdown \
  2>&1

echo "harness-toolkit [context]: Full snapshot saved to CONTEXT_FULL.md before compaction."

exit 0
