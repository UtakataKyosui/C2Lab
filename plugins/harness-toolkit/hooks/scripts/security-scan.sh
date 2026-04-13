#!/bin/bash
# PostToolUse hook: Write/Edit 後に Semgrep で変更ファイルをセキュリティスキャン
# 問題が見つかった場合は結果を出力する（rtk があればトークン削減）
set -euo pipefail

# semgrep が利用可能か確認
if ! command -v semgrep &>/dev/null; then
  exit 0
fi

# jq が利用可能か確認（stdin パースに必要）
if ! command -v jq &>/dev/null; then
  echo "harness-toolkit [security-scan]: jq not found, skipping scan." >&2
  exit 0
fi

# stdin から file_path を直接抽出（メモリ効率のため変数に一括格納しない）
FILE_PATH=$(jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# 絶対パスでなければプロジェクトディレクトリと結合
if [[ "$FILE_PATH" != /* ]]; then
  FILE_PATH="$PROJECT_DIR/$FILE_PATH"
fi

# パストラバーサル防止: 解決済みパスが PROJECT_DIR 内にあるか検証
RESOLVED_PATH=$(cd "$(dirname "$FILE_PATH")" 2>/dev/null && echo "$(pwd)/$(basename "$FILE_PATH")") || exit 0
if [[ "$RESOLVED_PATH" != "$PROJECT_DIR"/* ]]; then
  echo "harness-toolkit [security-scan]: File outside project dir, skipping: $RESOLVED_PATH" >&2
  exit 0
fi
FILE_PATH="$RESOLVED_PATH"

# ファイルが存在するか確認
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# セキュリティスキャン対象の拡張子に絞る
case "$FILE_PATH" in
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs|\
  *.py|*.go|*.java|*.rb|*.php|\
  *.yaml|*.yml|*.json)
    ;;
  *)
    # 対象外の拡張子はスキップ
    exit 0
    ;;
esac

# 大きなファイル（1MB超）はスキップ
FILE_SIZE=$(wc -c < "$FILE_PATH" 2>/dev/null || echo 0)
if [ "$FILE_SIZE" -gt 1048576 ]; then
  exit 0
fi

# Semgrep でスキャン（auto モードで言語自動検出）
RESULT=$(semgrep --config auto --quiet "$FILE_PATH" 2>&1) || true

# 結果が空（問題なし）の場合はスキップ
if [ -z "$RESULT" ]; then
  exit 0
fi

# 問題がある場合は出力（rtk があればトークン削減）
echo "harness-toolkit [security-scan]: $FILE_PATH"
if command -v rtk &>/dev/null; then
  echo "$RESULT" | rtk
else
  echo "$RESULT"
fi

exit 0
