# PR Review Workflow — Bookmark を活用したレビュー対応

## 1. Bookmark の基本概念

**Bookmark** は jj における Git のブランチ相当の概念です。ただし jj の「Change（変更）」はブランチなしでも成立するため、Bookmark は主に「外部との同期ポイント」として機能します。

### Git ブランチとの対比

| 概念           | Git                        | jj (Jujutsu)                         |
|----------------|----------------------------|--------------------------------------|
| 作業単位       | コミット + ブランチ        | **Change**（ブランチ不要）           |
| 外部公開の目印 | ブランチ                   | **Bookmark**                         |
| HEAD の概念    | ブランチが指すコミット     | `@`（現在の作業 Change）             |
| 切り替え       | `git checkout <branch>`    | `jj edit <change-id>`                |
| 作業途中の保存 | `git stash`                | **不要**（Change は常に保存済み）    |
| リモートへの公開 | `git push`               | `jj git push -b <bookmark-name>`     |

**重要**: jj では Bookmark を付けなくても Change は存在し続けます。Bookmark は「PR として外部に見せたい Change の目印」です。

---

## 2. Bookmark の基本操作

### 作成・確認・移動・削除

```bash
# Bookmark を作成（現在の @ に紐付け）
jj bookmark create <name>

# 特定の Change に Bookmark を作成
jj bookmark create <name> -r <change-id>

# 全 Bookmark を一覧表示（リモート含む）
jj bookmark list --all-remotes

# Bookmark を現在の @ に移動
jj bookmark set <name>

# Bookmark を特定の Change に移動
jj bookmark set <name> -r <change-id>

# Bookmark を削除（ローカルのみ）
jj bookmark delete <name>

# Bookmark のリモート追跡を忘れる（ローカルの記録だけ削除）
jj bookmark forget <name>
```

### リモートとの同期

```bash
# Bookmark を GitHub/GitLab に push
jj git push -b <bookmark-name>

# リモートの変更を取得
jj git fetch

# 全 Bookmark を push（注意: 想定外の Bookmark も push される可能性あり）
jj git push --all
```

---

## 3. PRレビューへの対応フロー（1PR）

PR のレビューコメントを受けて修正する典型的なフローです。

### Step 1: 現状確認

```bash
# リモート含め全 Bookmark と Change の状態を確認
jj bookmark list --all-remotes

# ログで全体の変更ツリーを確認
jj log
```

出力例：
```
◆  abc123  my-feature  origin/my-feature
│  feat: ユーザー認証機能の追加
~
```

### Step 2: 対象 Change へ移動

```bash
# Bookmark 名で対象 Change に移動（git stash 不要）
jj edit my-feature

# または Change ID で直接指定
jj edit abc123
```

### Step 3-A: 既存 Change を直接修正（推奨: 履歴をきれいに保ちたい場合）

```bash
# @ が my-feature Change を指している状態でファイルを編集
# （ファイルを直接編集すればOK。jj はワーキングツリーを自動追跡）

# 修正内容を確認
jj diff

# Change の説明を更新（必要な場合）
jj describe -m "feat: ユーザー認証機能の追加（レビュー対応）"
```

### Step 3-B: 新しい Change を積み上げる（推奨: 修正履歴を残したい場合）

```bash
# 現在の Change の上に新しい Change を作成
jj new -m "fix: レビュー指摘事項の修正"

# Bookmark を新しい Change に移動
jj bookmark set my-feature

# ファイルを編集して修正
```

### Step 4: リモートへ push

```bash
# Bookmark を指定して push
jj git push -b my-feature
```

---

## 4. 複数PRが並行している場合の管理

jj の最大の強みは、**複数の PR を同時に抱えていてもコンテキスト切り替えが瞬時**にできる点です。

### 全体把握

```bash
# main から派生した全ての Change を確認
jj log -r 'main..all()'

# Bookmark 付きの Change だけを確認
jj log -r 'bookmarks()'
```

出力例：
```
◆  xyz789  feature-b  origin/feature-b
│  feat: 検索機能の実装
│
│ ◆  abc123  feature-a  origin/feature-a
├─╯  feat: ユーザー認証機能の追加
│
◆  main123  main  origin/main
   chore: 初期設定
```

### コンテキスト切り替え（git stash 完全不要）

```bash
# feature-a のレビュー対応中に feature-b の急ぎ修正が入った場合
jj edit feature-b  # 即座に切り替え。保存・stash 一切不要

# feature-b の修正が終わったら feature-a に戻る
jj edit feature-a
```

### 各 PR を独立して push

```bash
# feature-a だけ push
jj git push -b feature-a

# feature-b だけ push
jj git push -b feature-b
```

---

## 5. Bookmark 衝突への対処

リモートで他の人が同じ Bookmark に push した場合、`jj git fetch` 後に衝突が発生することがあります。

### 衝突の確認

```bash
jj git fetch
jj bookmark list --all-remotes
```

衝突した Bookmark は `?` マークで表示されます：
```
my-feature: abc123 ?
  @origin: xyz789
```

### 対処法: rebase で解消

```bash
# ローカルの Change をリモートの最新の上に rebase
jj rebase -s my-feature -d origin/my-feature

# Bookmark を rebase 後の Change に移動
jj bookmark set my-feature -r @

# push（--force-with-lease 相当の安全な push）
jj git push -b my-feature
```

---

## 6. Bookmark の整理

マージ済み PR の Bookmark は積極的に整理しましょう。

### `delete` vs `forget` の違い

| コマンド               | 動作                                          | 用途                              |
|------------------------|-----------------------------------------------|-----------------------------------|
| `jj bookmark delete`   | ローカルを削除（リモートは `jj git push -b <name>` で明示的に削除）  | PR マージ後の完全削除             |
| `jj bookmark forget`   | ローカルの追跡記録だけ削除（リモートは残る）  | 他人のブランチを追跡し終えた場合  |

```bash
# マージ済み Bookmark を完全削除（リモートも削除）
jj bookmark delete merged-feature
jj git push -b merged-feature  # リモートから削除

# マージ済みの全 Bookmark を一括削除（確認してから実行）
jj bookmark list | grep "merged-" | xargs -I{} jj bookmark delete {}
```

### main との同期

```bash
# main を最新に更新
jj git fetch
jj bookmark set main -r origin/main

# 全ての作業中 Change を新しい main の上に rebase
jj rebase -s 'roots(main..all())' -d main
```

---

## まとめ: jj の PR ワークフローの利点

1. **`git stash` が不要** — jj はすべての Change を常に保存する
2. **瞬時のコンテキスト切り替え** — `jj edit` だけで OK
3. **履歴の柔軟な書き換え** — PR をきれいに保ちながらレビュー対応
4. **衝突は後回し可能** — コンフリクト状態でも作業を継続できる
