---
name: Jujutsu VCS ワークフロー
description: This skill should be used when the user asks to use "jj", "Jujutsu", "ブランチ管理", manages workspaces with "jj workspace", creates commits with "jj commit", pushes with "jj git push", views history with "jj log", or when they want to manage code changes using jj instead of git. Also activates when user mentions "jj diff", "jj rebase", "jj squash", "jj describe", "jj bookmark", or references working with multiple branches in parallel.
version: 0.1.0
---

# Jujutsu VCS ワークフロー

Jujutsu（jj）は Git の運用上の問題を解決する次世代 VCS。コミットの概念を「変更（change）」として扱い、ブランチ代わりに「ブックマーク（bookmark）」を使う。C2Lab では git コマンドの代わりに常に jj を使用する。

## 基本原則

- jj コマンドは必ず**非インタラクティブフラグ**を使う（インタラクティブエディタは使わない）
- `jj commit -m 'message'` 形式で記述する
- Push は必ず `jj-safe-push` スキルを使う
- shell wrapper が `jj git push` をブロックする場合は `command jj git push` でバイパスする

## 基本コマンド

### 状態確認

```bash
# 現在の状態確認
jj status

# コミット履歴を見る
jj log

# 変更の差分を見る
jj diff

# 特定のリビジョンの差分
jj diff -r <revision>

# ログを詳細表示
jj log --no-pager -r 'ancestors(trunk(), 10)..'
```

### 変更（Change）の作成・編集

```bash
# 現在の変更に説明を付ける（コミットメッセージ相当）
jj describe -m "fix: バグを修正"

# 変更を確定して新しい空の変更を作る（git commit 相当）
jj commit -m "feat: 新機能を追加"

# 新しい空の変更を作る（次の作業用）
jj new

# 特定の変更の上に新しい変更を作る
jj new <revision>
```

### ブックマーク（Bookmark）管理

ブックマークは Git のブランチに相当する概念。

```bash
# ブックマーク一覧
jj bookmark list

# 新しいブックマークを作る
jj bookmark create feature/my-feature

# 現在の変更にブックマークを設定
jj bookmark set feature/my-feature

# ブックマークを特定リビジョンに移動
jj bookmark set feature/my-feature -r <revision>

# ブックマークを削除
jj bookmark delete feature/my-feature
```

### Workspace（並行開発）

workspace は Git の worktree に相当。複数のブランチを同時に作業するために使う。

```bash
# workspace を追加（ブックマークを指定）
jj workspace add ../feature-a -r feature/feature-a

# workspace 一覧
jj workspace list

# workspace を削除
jj workspace forget ../feature-a

# 削除後は cwd が無効になる場合がある → ユーザーにセッション再起動を促す
```

> **注意**: workspace を削除すると cwd が stale になる場合がある。その場合は直ちにユーザーにセッション再起動を促す。

### リベース・統合

```bash
# 現在の変更を別のリビジョンにリベース
jj rebase -d <target-revision>

# ブックマーク全体をリベース
jj rebase -b feature/my-feature -d main

# 変更を親にスカッシュ（squash）
jj squash

# 親の変更に特定ファイルをスカッシュ
jj squash --into @-

# 変更を破棄
jj abandon
```

### ファイル操作

```bash
# ファイルを元の状態に戻す
jj restore <file>

# 全ファイルを元に戻す
jj restore .

# ファイルを別リビジョンから復元
jj restore --from <revision> <file>
```

### リモート操作

```bash
# リモートからフェッチ
jj git fetch

# リモートにプッシュ（jj-safe-push スキルを使うこと）
# 直接使う場合（wrapper でブロックされたら command を付ける）
command jj git push --bookmark feature/my-feature

# 全ブックマークをプッシュ
command jj git push --all
```

## よく使うワークフロー

### 機能開発フロー

```bash
# 1. main から最新を取得
jj git fetch

# 2. workspace を作成して作業開始
jj workspace add ../my-feature -r main

# 3. 変更作業...

# 4. 変更を確定
jj commit -m "feat: 新機能を実装"

# 5. ブックマークを作成
jj bookmark create feature/my-feature

# 6. プッシュ（jj-safe-push スキルを使用）
```

### コンフリクト解消フロー

```bash
# 1. リベース実行
jj rebase -d main

# コンフリクトがある場合、jj は変更を保留状態にする
# 2. コンフリクトファイルを確認
jj status

# 3. ファイルを直接編集してコンフリクトを解消

# 4. 解消後に状態確認
jj diff
```

### 複数変更のまとめ方

```bash
# 直前の変更を親にスカッシュ
jj squash

# 特定のリビジョン間をスカッシュ
jj rebase --insert-before @- -s @
jj squash
```

## C2Lab 固有の注意事項

- `.claude/settings.json` で git コマンドが禁止されている → jj のみ使用
- Push は `jj-safe-push` スキルで diverge を事前検出してから実行
- 単一コミットだけの Push は原則行わない（複数コミットをまとめる）

## jj log の読み方

```
@  qnlzwqyz user@example.com 2026-01-01 12:00:00 feature/my-feature* abc12345
│  feat: 新機能を実装
◉  pxktqmyz user@example.com 2026-01-01 11:00:00 main abc12344
│  chore: initial setup
```

- `@` = 現在の変更（作業中）
- `*` = ブックマークが最新コミットより進んでいる
- リビジョンID の先頭数文字でコマンドに使用できる

## Additional Resources

### Reference Files

詳細なコマンドリファレンスと高度なワークフロー:
- **`references/jj-commands.md`** - コマンド完全リファレンス
- **`references/jj-vs-git.md`** - git コマンドとの対応表
