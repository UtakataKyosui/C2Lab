---
name: vibe-kanban:open
description: ブラウザで vibe-kanban を開く。vibe-kanban が起動していない場合は起動方法を案内する
allowed-tools:
  - Bash
---

vibe-kanban をブラウザで開いてください。

## 手順

1. Bash ツールで接続確認:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null
   ```

2. **接続成功（200 または 301）の場合**:
   ```bash
   open http://localhost:3000
   ```
   「vibe-kanban をブラウザで開きました。」と報告してください。

3. **接続失敗の場合**:
   以下を案内してください:

   ```
   vibe-kanban が起動していません。

   別のターミナルで以下を実行してください:
     npx vibe-kanban

   起動後、このコマンドを再度実行するか、手動で http://localhost:3000 を開いてください。

   カスタムポートを使用している場合:
     VK_PORT=<port> npx vibe-kanban
   ```

4. macOS 以外（Linux）の場合は `open` の代わりに `xdg-open` を使用してください:
   - macOS: `open http://localhost:3000`
   - Linux: `xdg-open http://localhost:3000`
   - Windows (WSL): `cmd.exe /c start http://localhost:3000`
