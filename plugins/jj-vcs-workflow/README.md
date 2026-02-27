# jj-vcs-workflow

Jujutsu (jj) VCS の操作ガイドと安全な Push ワークフローを提供するプラグイン。

## 概要

Git からの移行、基本コマンド、並列開発、履歴操作、コンフリクト解消、PR レビュー対応、安全な Push ワークフローを網羅したガイドを提供する。また、誤った `jj git push` を PreToolUse フックでブロックする。

## 提供コンポーネント

### Skills

| スキル名 | 説明 |
|----------|------|
| `jj-vcs-workflow` | jj VCS の総合ガイド。基本コマンド・Git 移行・並列開発・履歴操作・PR レビュー・安全な Push ワークフローをカバー。 |

**スキルが自動ロードされるファイルパターン**:
- `**/.jj/**`

### ガイド

| ファイル | 内容 |
|----------|------|
| `workflows.md` | 基本的な作業フロー |
| `git-to-jj.md` | Git から jj への移行ガイド |
| `best-practices.md` | ベストプラクティス |
| `commands.md` | コマンドリファレンス |
| `revisions.md` | リビジョン指定の書き方 |
| `guides/history-maintenance.md` | 履歴管理・書き換え |
| `guides/conflict-collab.md` | コンフリクト解消・共同作業 |
| `guides/parallel-work.md` | 並列開発（複数ブランチ同時作業） |
| `guides/safe-push.md` | 安全な Push ワークフロー |
| `guides/pr-review-workflow.md` | PR レビュー対応フロー |
| `guides/workspace.md` | ワークスペース管理 |

## 使い方

jj 関連のファイルを開いているとき、または jj の操作について質問すると参照情報が自動的に提供される。

```
jj で並列開発する方法を教えて
jj rebase の使い方は？
```

## フック

| イベント | 対象 | 処理 |
|----------|------|------|
| `PreToolUse` | Bash | `jj git push`（dry-run 以外）を検出してブロックし、`jj-safe-push` skill の使用を案内する |
