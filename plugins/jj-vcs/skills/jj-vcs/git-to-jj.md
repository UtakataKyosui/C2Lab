# GitコマンドとJJコマンドの対応表

GitユーザーがJJに移行する際のコマンド対応表です。

## リポジトリ操作

| Git | jj | 説明 |
|-----|-----|------|
| `git init` | `jj git init` | リポジトリ初期化（Gitと共存） |
| `git init` | `jj git init --no-colocate` | リポジトリ初期化（JJのみ） |
| `git clone <url>` | `jj git clone <url>` | リモートリポジトリをクローン |
| `git fetch` | `jj git fetch` | リモートから変更を取得 |
| `git fetch origin` | `jj git fetch --remote origin` | 特定リモートから取得 |
| `git push --all` | `jj git push --all` | すべての変更をプッシュ |
| `git push -u origin <branch>` | `jj git push -b <bookmark>` | 特定ブックマークをプッシュ |
| `git pull` | `jj git fetch` + `jj rebase` | フェッチしてリベース |

## 変更操作

| Git | jj | 説明 |
|-----|-----|------|
| `git status` | `jj status` / `jj st` | 現在の状態を表示 |
| `git diff` | `jj diff` | 差分を表示 |
| `git diff HEAD` | `jj diff` | 現在のチェンジの差分 |
| `git diff --staged` | （不要） | JJにステージングはない |
| `git add -A && git commit` | `jj commit` / `jj ci` | 変更をコミット |
| `git commit --amend` | `jj squash` | 変更を親チェンジに統合 |
| `git reset --hard` | `jj abandon` | チェンジを放棄 |
| `git checkout <commit>` | `jj edit <revision>` | 特定リビジョンを編集 |
| `git stash` | （不要） | 自動スナップショット |
| `git stash pop` | （不要） | 自動スナップショット |

## コミットメッセージ操作

| Git | jj | 説明 |
|-----|-----|------|
| `git commit --amend` | `jj describe` / `jj desc` | チェンジの説明を編集 |
| `git commit -m "msg"` | `jj commit -m "msg"` | メッセージ指定でコミット |
| `git commit --amend -m "msg"` | `jj describe -m "msg"` | 説明を更新 |

## ブランチ/ブックマーク操作

| Git | jj | 説明 |
|-----|-----|------|
| `git branch` | `jj bookmark list` | ブックマーク一覧 |
| `git branch <name>` | `jj bookmark create <name> -r @` | ブックマーク作成 |
| `git branch -d <name>` | `jj bookmark delete <name>` | ブックマーク削除 |
| `git branch -D <name>` | `jj bookmark delete <name>` | 強制削除（同じ） |
| `git branch -f <name>` | `jj bookmark move <name> --to @` | ブックマーク移動 |
| `git checkout -b <name>` | `jj new` + `jj bookmark create <name>` | 新規ブックマーク |
| `git checkout <branch>` | `jj edit <bookmark>` | ブックマークに移動 |
| `git switch <branch>` | `jj new <bookmark>` | ブックマーク上に新規チェンジ |

## 履歴操作

| Git | jj | 説明 |
|-----|-----|------|
| `git log` | `jj log` | 履歴表示 |
| `git log --oneline` | `jj log --no-graph` | シンプルな履歴 |
| `git log -p` | `jj log -p` | パッチ付き履歴 |
| `git show <commit>` | `jj show <revision>` | リビジョン詳細 |
| `git rebase <base>` | `jj rebase -d <base>` | リベース |
| `git rebase -i` | `jj squash` / `jj split` | インタラクティブ編集 |
| `git cherry-pick <commit>` | `jj new <revision>` | 特定リビジョンから作成 |
| `git revert <commit>` | `jj backout -r <revision>` | リビジョン打消し |
| `git merge <branch>` | `jj new <rev1> <rev2>` | マージ |

## 高度な操作

| Git | jj | 説明 |
|-----|-----|------|
| `git add -p` | `jj split` | 部分的に分割 |
| `git commit -p` | `jj split` | チェンジを分割 |
| `git reflog` | `jj op log` | 操作ログ表示 |
| `git reset --hard HEAD@{1}` | `jj undo` | 直前操作を取り消し |
| `git diff <a> <b>` | `jj diff --from <a> --to <b>` | 2リビジョン間の差分 |
| `git blame <file>` | `jj file annotate <file>` | ファイルの変更履歴 |
| `git bisect` | `jj bisect` | 二分探索 |

## JJ固有の便利なコマンド

| コマンド | 説明 |
|---------|------|
| `jj undo` | 直前の操作を取り消し（Gitにはない） |
| `jj op log` | すべての操作履歴を表示 |
| `jj op restore <op>` | 特定の操作時点に復元 |
| `jj duplicate <rev>` | リビジョンを複製 |
| `jj absorb` | 変更を適切な祖先に自動分配 |

## 重要な違い

1. **ステージングがない**: `git add`は不要。すべての変更が自動的にトラッキングされる
2. **常にスナップショット**: ワーキングコピーは常に保存される（stash不要）
3. **ブランチ→ブックマーク**: jjではブランチの代わりにブックマークを使用
4. **安全な操作**: すべての操作は`jj undo`で取り消し可能
