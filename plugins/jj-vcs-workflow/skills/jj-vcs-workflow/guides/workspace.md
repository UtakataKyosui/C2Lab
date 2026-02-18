# Workspace を使った並列開発

`jj workspace` は、**同一リポジトリに複数の作業ディレクトリ（Working Copy）を接続する**機能。
Git の `worktree` に相当するが、jj の Change モデルとシームレスに統合されている。

## いつ使うか

| アプローチ | 適しているケース |
|-----------|----------------|
| `jj new` / `jj edit` | 軽量なコンテキスト切り替え。同一ディレクトリで十分な場合 |
| `jj workspace add` | **ファイルシステムレベルの分離**が必要な場合 |

Workspace を選ぶべき具体的なシーン:

- **長時間ビルド/テストの実行中に別の作業を進めたい**: テスト実行中の workspace はそのまま、別の workspace でコーディングを続行
- **異なる依存関係が必要**: 各 workspace で独立した `node_modules` や仮想環境を持てる
- **複数の Claude Code セッションを並行実行**: 各セッションが独立した作業ディレクトリで動作
- **レビュー中のコードを壊さず新機能を開発**: レビュー用 workspace を保持しつつ新しい開発を進める

## 基本操作

### Workspace の作成

```bash
# mainから分岐する新しい workspace を作成
jj workspace add ../my-feature --revision main

# 説明付きで作成（新しい Change に description を設定）
jj workspace add ../my-feature --revision main
cd ../my-feature
jj describe -m "feat: 新機能の実装"

# workspace 名を明示的に指定
jj workspace add ../bugfix --name bugfix-workspace --revision main
```

`jj workspace add <DESTINATION>` は以下を行う:
1. `<DESTINATION>` ディレクトリを作成
2. 指定した `--revision`（デフォルトは現在の Working Copy の親）の子として新しい Change を作成
3. その Change を新しい workspace の Working Copy として設定

### Workspace の一覧

```bash
jj workspace list
```

出力例:
```
default: kkmpptxz 1a2b3c4d feat: メイン作業
feature-a: mmnnoopp 5e6f7a8b feat: 機能Aの実装
bugfix: qqrrsstt 9c0d1e2f fix: バグ修正
```

各 workspace は独立した Working Copy（`@`）を持つ。`jj log` では `<workspace名>@` として表示される。

### Workspace の削除

```bash
# 特定の workspace の追跡を停止
jj workspace forget feature-a

# ディレクトリは自動削除されない。手動で削除する
rm -rf ../feature-a
```

> [!NOTE]
> `jj workspace forget` はリポジトリからの追跡を解除するだけで、ディスク上のディレクトリは残る。
> workspace 内で作成した Change はリポジトリに残り、`jj log` で引き続き参照可能。

### Workspace の名前変更

```bash
# 現在の workspace の名前を変更
jj workspace rename new-name
```

## 並列開発ワークフロー

### パターン 1: ビルド/テスト中の並行開発

```bash
# default workspace で長時間テストを開始
cd /path/to/repo
npm test  # 数分かかるテスト

# 別ターミナルで新しい workspace を作成して開発を続行
jj workspace add ../repo-feature --revision main
cd ../repo-feature
jj describe -m "feat: 別の機能を実装"
# ... コーディング ...

# テストが完了したら default に戻る
cd /path/to/repo
```

### パターン 2: 複数の Claude Code セッションを並列実行

```bash
# workspace を作成し、それぞれに description を設定
jj workspace add ../repo-task-a --revision main
jj workspace add ../repo-task-b --revision main
cd ../repo-task-a && jj describe -m "Task A: API実装"
cd ../repo-task-b && jj describe -m "Task B: UI実装"

# 各 workspace で Claude Code を起動（別ターミナルで）
cd ../repo-task-a && claude
cd ../repo-task-b && claude

# 各セッション終了後、default workspace で確認
cd /path/to/repo
jj log  # 全 workspace の Change が見える
```

### パターン 3: レビュー対応と新機能開発の並行

```bash
# レビュー対応用 workspace
jj workspace add ../repo-review --revision feature-branch-bookmark

# 新機能開発を default で続行
jj new main -m "feat: 次の機能"
# ... 開発 ...

# レビュー対応は別 workspace で
cd ../repo-review
# ... レビュー指摘の修正 ...
jj describe -m "fix: レビュー指摘を修正"
```

## Stale Workspace の更新

他の workspace でリポジトリを変更すると、別の workspace の Working Copy が「stale（古い状態）」になる場合がある。

```bash
# stale workspace を最新状態に同期
jj workspace update-stale
```

このコマンドは以下の場合に必要:
- 別の workspace で `jj rebase` や `jj squash` を行い、この workspace の Change の祖先が変更された場合
- 別の workspace でこの workspace の Change に影響する操作を行った場合

> [!TIP]
> workspace に移動して操作しようとしたときに stale 警告が出たら、まず `jj workspace update-stale` を実行する。

## Sparse Patterns

workspace 作成時に、作業に必要なファイルだけを含めることができる。

```bash
# 現在の workspace の sparse patterns をコピー（デフォルト）
jj workspace add ../ws-copy --sparse-patterns copy

# 全ファイルを含む
jj workspace add ../ws-full --sparse-patterns full

# 空の状態から始める（必要なパスだけ後で追加）
jj workspace add ../ws-minimal --sparse-patterns empty
```

大規模リポジトリで特定のディレクトリだけ作業する場合に有用。

## `jj new` / `jj edit` との使い分け

### 単一ディレクトリでの並列作業（推奨: 軽量なケース）

```bash
# A案の作業
jj new main -m "feat: Idea A"
# ... コーディング ...

# B案に切り替え（A案は自動保存される）
jj new main -m "feat: Idea B"
# ... コーディング ...

# A案に戻る
jj edit <change-id-of-A>
```

メリット: ディレクトリが増えない、切り替えが瞬時
デメリット: ビルド成果物のキャッシュが共有される、依存関係の分離ができない

### 複数 workspace での並列作業（推奨: 重いケース）

```bash
jj workspace add ../idea-a --revision main
jj workspace add ../idea-b --revision main
```

メリット: 完全なファイルシステム分離、独立した依存関係、同時にビルド/テスト可能
デメリット: ディスク容量を消費、workspace の管理が必要

## 作業完了後のクリーンアップ

```bash
# 1. 作業結果を確認
jj log

# 2. 不要になった workspace を forget
jj workspace forget feature-a

# 3. ディレクトリを削除
rm -rf ../feature-a

# 4. 不要な Change があれば abandon
jj abandon <change-id>
```

> [!NOTE]
> workspace を forget しても Change は残る。Change 自体を削除するには `jj abandon` が必要。

## 注意事項

- **同じ Change を複数の workspace で同時に編集しない**: コンフリクトの原因になる
- **workspace ディレクトリは同一リポジトリの兄弟ディレクトリに作成する**のが慣例（例: `../repo-feature`）
- **push は各 workspace で独立して実行可能**: ただし safe-push ワークフローに従うこと
- **`.jj/` ディレクトリは共有される**: 全 workspace が同じリポジトリデータを参照する
