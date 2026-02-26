#!/usr/bin/env bash
# plugins/ 配下の全プラグインを --plugin-dir で Claude Code に読み込むヘルパー。
#
# 使い方:
#   ./scripts/load-plugins.sh              # 全プラグインを読み込んで claude を起動
#   ./scripts/load-plugins.sh --dry-run    # 実行コマンドを表示するだけ (実行しない)
#   ./scripts/load-plugins.sh --print      # --dry-run のエイリアス
#   ./scripts/load-plugins.sh -- -p "hello" # -- 以降は claude への追加引数

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGINS_DIR="$REPO_ROOT/plugins"

dry_run=false
claude_extra_args=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run|--print)
      dry_run=true
      shift
      ;;
    --)
      shift
      claude_extra_args+=("$@")
      break
      ;;
    *)
      claude_extra_args+=("$1")
      shift
      ;;
  esac
done

if [[ ! -d "$PLUGINS_DIR" ]]; then
  echo "ERROR: $PLUGINS_DIR が見つかりません" >&2
  exit 1
fi

plugin_args=()
count=0
for dir in "$PLUGINS_DIR"/*/; do
  [[ -d "$dir" ]] || continue
  plugin_args+=("--plugin-dir" "$dir")
  count=$((count + 1))
done

if [[ $count -eq 0 ]]; then
  echo "WARNING: プラグインが見つかりません" >&2
  exit 1
fi

cmd=(claude "${plugin_args[@]}" ${claude_extra_args[@]+"${claude_extra_args[@]}"})

if [[ "$dry_run" == true ]]; then
  echo "${cmd[*]}"
else
  echo "Loading $count plugins..." >&2
  exec "${cmd[@]}"
fi
