---
name: jj-vcs
description: Jujutsu (jj) VCSを使用する際のコマンドガイド。GitからJJへの移行、jjコマンドの使い方、バージョン管理操作を行う際に参照する。
globs:
  - "**/.jj/**"
---

# Jujutsu (jj) VCS コマンドガイド

Jujutsu（jj）は、Gitと互換性を持ちながらよりシンプルで強力なワークフローを提供する次世代バージョン管理システムです。

## 基本概念

- **チェンジ（Change）**: jjでは「コミット」ではなく「チェンジ」という概念を使用
- **ワーキングコピー**: 常に自動的にスナップショットされる（`git add`不要）
- **ブックマーク**: Gitのブランチに相当する概念
- **操作ログ**: すべての操作履歴を追跡し、`jj undo`で取り消し可能

## クイックリファレンス（最もよく使うコマンド）

| 操作 | コマンド |
|-----|---------|
| 状態確認 | `jj status` または `jj st` |
| 差分表示 | `jj diff` |
| 履歴表示 | `jj log` |
| コミット | `jj commit -m "メッセージ"` |
| 説明編集 | `jj describe -m "メッセージ"` |
| 新規チェンジ | `jj new` |
| 取り消し | `jj undo` |
| リモート取得 | `jj git fetch` |
| プッシュ | `jj git push -b <bookmark>` |

## 詳細ドキュメント

より詳細な情報は以下のファイルを参照してください：

- **git-to-jj.md**: GitコマンドとJJコマンドの完全な対応表
- **commands.md**: 主要コマンドの詳細な使い方とオプション
- **revisions.md**: リビジョン指定方法（@, @-, チェンジIDなど）
- **workflows.md**: 新規機能開発・不具合修正のワークフロー
- **best-practices.md**: ベストプラクティスとトラブルシューティング

## ヘルプの確認

```bash
jj help           # 全体のヘルプ
jj help <command> # 特定コマンドのヘルプ
```

## 参考リンク

- 公式ドキュメント: https://www.jj-vcs.dev/
- CLIリファレンス: https://www.jj-vcs.dev/latest/cli-reference/
