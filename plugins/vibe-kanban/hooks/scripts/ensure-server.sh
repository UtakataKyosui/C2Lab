#!/usr/bin/env bash
# vibe-kanban サーバー状態確認フック
# vibe-kanban が起動中かどうかを確認します。サーバーの自動起動は行いません。
# （バイナリがブラウザを自動で開くため）
# 手動起動: npx vibe-kanban@latest

VK_PORT="${VK_PORT:-3000}"

code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${VK_PORT}" 2>/dev/null)

if [ "$code" = "200" ] || [ "$code" = "301" ]; then
  echo "[vibe-kanban] http://localhost:${VK_PORT} で有効です。カンバンボードを表示するには /vibe-kanban:open を実行してください。" >&2
else
  echo "[vibe-kanban] 実行されていません。別のターミナルで手動で起動してください: npx vibe-kanban@latest" >&2
fi

echo '{}'
