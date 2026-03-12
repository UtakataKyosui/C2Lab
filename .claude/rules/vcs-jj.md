# VCS・jj/Git ワークフロー

## 基本ルール

- このリポジトリでは常に `jj` を使用する（`.claude/settings.json` で git コマンドは禁止されている）。Push は必ず `jj-safe-push` skill を使う
- レビューに対応したら Push する
- 単一のコミットのみでの Push は原則行わない

## jj 操作

- jj コマンドは常に非インタラクティブフラグを使う（例: `jj commit -m 'message'`）。インタラクティブエディタは使わない
- shell wrapper が `jj git push` をブロックする場合は `command jj git push` でバイパスする
- worktree を削除すると cwd が無効になる場合がある。cwd が stale になったらすぐユーザーにセッション再起動を促す
