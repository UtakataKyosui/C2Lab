#!/usr/bin/env bash
# vibe-kanban セッション終了フック
# セッション終了時にタスクステータス更新をリマインドする

VK_PORT="${VK_PORT:-3000}"

code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${VK_PORT}" 2>/dev/null)

if [ "$code" = "200" ] || [ "$code" = "301" ]; then
  echo "[vibe-kanban] セッション完了。タスクのステータスを更新してください: http://localhost:${VK_PORT}" >&2
  echo "[vibe-kanban] 大きなコード変更があった場合は「Review」に、作業が未完了の場合は「In Progress」のままにしてください。" >&2
fi

echo '{}'
