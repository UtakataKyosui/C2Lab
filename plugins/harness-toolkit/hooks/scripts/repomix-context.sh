#!/bin/bash
# Stop hook: セッション終了時に変更ファイルの差分ベースで repomix を実行
# CONTEXT.md を生成して次セッションの初期コンテキストとして利用する
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# repomix が利用可能か確認
if ! command -v repomix &>/dev/null; then
  exit 0
fi

# jj または git で変更ファイルを取得（untracked も含む）
CHANGED=""
if command -v jj &>/dev/null; then
  CHANGED=$(jj diff --name-only 2>/dev/null || echo "")
fi
if [ -z "$CHANGED" ] && command -v git &>/dev/null; then
  CHANGED=$(git ls-files --modified --others --exclude-standard 2>/dev/null || echo "")
fi

# 変更ファイルがない場合はスキップ
if [ -z "$CHANGED" ]; then
  exit 0
fi

# 存在するファイルのみ対象にし、カンマを含むファイル名はスキップ
VALID_FILES=()
while IFS= read -r file; do
  # カンマを含むファイル名は repomix --include の区切り文字と衝突するためスキップ
  if [[ "$file" == *","* ]]; then
    echo "harness-toolkit [context]: Skipping file with comma in name: $file" >&2
    continue
  fi
  if [ -f "$PROJECT_DIR/$file" ]; then
    VALID_FILES+=("$file")
  fi
done <<< "$CHANGED"

if [ ${#VALID_FILES[@]} -eq 0 ]; then
  exit 0
fi

# カンマ区切りのパターンに変換
FILES_PATTERN=$(printf '%s,' "${VALID_FILES[@]}" | sed 's/,$//')

# repomix で変更ファイルを圧縮して CONTEXT.md に出力
OUTPUT_FILE="$PROJECT_DIR/CONTEXT.md"
repomix \
  --include "$FILES_PATTERN" \
  --output "$OUTPUT_FILE" \
  --style markdown \
  --no-git-sort-by-changed-date \
  2>&1 || \
repomix \
  --include "$FILES_PATTERN" \
  --output "$OUTPUT_FILE" \
  --style markdown \
  2>&1

FILE_COUNT=${#VALID_FILES[@]}
echo "harness-toolkit [context]: Generated CONTEXT.md from $FILE_COUNT changed file(s)."
echo "  Next session: 'CONTEXT.md を読んで前回の作業を把握してください'"

exit 0
