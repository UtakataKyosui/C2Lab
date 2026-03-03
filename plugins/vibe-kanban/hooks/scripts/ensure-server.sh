#!/usr/bin/env bash
# vibe-kanban server status check hook
# Reports whether vibe-kanban is running. Does NOT auto-start the server,
# because the binary unconditionally opens a browser window on launch.
# Start the server manually: npx vibe-kanban@latest

VK_PORT="${VK_PORT:-3000}"

code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${VK_PORT}" 2>/dev/null)

if [ "$code" = "200" ] || [ "$code" = "301" ]; then
  echo "[vibe-kanban] Active at http://localhost:${VK_PORT} — run /vibe-kanban:open to view your kanban board."
else
  echo "[vibe-kanban] Not running. Start it manually in a separate terminal: npx vibe-kanban@latest"
fi
