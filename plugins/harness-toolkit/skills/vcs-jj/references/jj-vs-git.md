# jj コマンドと git コマンドの対応表

| 操作 | git | jj |
|---|---|---|
| 状態確認 | `git status` | `jj status` |
| 差分表示 | `git diff` | `jj diff` |
| 履歴表示 | `git log` | `jj log` |
| コミット | `git commit -m "msg"` | `jj commit -m "msg"` |
| コミットメッセージ編集 | `git commit --amend` | `jj describe -m "msg"` |
| ブランチ作成 | `git checkout -b name` | `jj bookmark create name` |
| ブランチ切り替え | `git checkout name` | `jj new name` / `jj edit name` |
| ブランチ一覧 | `git branch` | `jj bookmark list` |
| ブランチ削除 | `git branch -d name` | `jj bookmark delete name` |
| マージ | `git merge name` | `jj rebase -d name` + `jj squash` |
| リベース | `git rebase main` | `jj rebase -d main` |
| スタッシュ | `git stash` | `jj new` (変更を新しい Change に) |
| ファイル復元 | `git checkout -- file` | `jj restore file` |
| リモートフェッチ | `git fetch` | `jj git fetch` |
| リモートプッシュ | `git push` | `command jj git push` |
| Worktree 追加 | `git worktree add ../path name` | `jj workspace add ../path -r bookmark` |
| Worktree 一覧 | `git worktree list` | `jj workspace list` |
| Worktree 削除 | `git worktree remove ../path` | `jj workspace forget ../path` |
| タグ作成 | `git tag v1.0` | `jj tag create v1.0` |
| reset (soft) | `git reset HEAD~1` | `jj squash --into @-` (逆) |
| コミット分割 | `git reset HEAD~1` + 再コミット | `jj split` |
| 変更の取り消し | `git revert` | `jj backout` |

## 主な概念の違い

| 概念 | git | jj |
|---|---|---|
| 作業中の変更 | Working tree + Index | Change (@) |
| コミット単位 | commit | change |
| ブランチポインタ | branch | bookmark |
| 現在位置 | HEAD | @ |
| インデックス/ステージング | あり | なし（自動） |
| マージコミット | あり | 基本なし（rebase 推奨） |

## jj 特有の操作

```bash
# 現在の Change (@ = HEAD 相当) を確認
jj log -r @

# 変更の親を確認
jj log -r @-

# 全ブックマークを表示
jj bookmark list --all

# コンフリクトがある場合
jj status  # コンフリクトファイルが表示される
# → ファイルを直接編集して解消
# → jj diff でコンフリクト解消を確認

# undo (最後の操作を取り消し)
jj undo

# 操作履歴を確認
jj op log
```
