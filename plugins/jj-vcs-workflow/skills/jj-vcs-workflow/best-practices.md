# JJ ベストプラクティス

JJを効果的に使用するためのベストプラクティスとトラブルシューティングガイドです。

## 基本的なワークフロー

### 1. 頻繁に状態を確認

```bash
# 現在の状態を確認
jj status

# 履歴を確認
jj log
```

**ポイント**: JJでは`jj status`がGitより情報量が多く、現在のチェンジの状態を詳しく表示します。

### 2. こまめに説明を更新

```bash
# 作業中でも説明を書く
jj describe -m "WIP: ログイン機能の実装中"

# 完成したら更新
jj describe -m "feat: ログイン機能を実装"
```

**ポイント**: JJではコミット前でもいつでも説明を変更できます。作業の意図を記録しておくと後で便利です。

### 3. 失敗を恐れない - undoがある

```bash
# 何か間違えたら
jj undo

# 操作履歴を確認
jj op log

# 特定の時点に戻る
jj op restore <operation_id>
```

**ポイント**: JJの最大の強みは、ほぼすべての操作を取り消せることです。実験的な操作も安心して試せます。

## 効率的な作業パターン

### パターン1: 機能開発（PR を出す場合）

**重要**: PR を出す予定がある場合、作業開始前に必ず feature bookmark を作成する。作業後に `jj bookmark set main` で main を進めてしまうと、`origin/main` のブランチ保護により巻き戻しができなくなる。

```bash
# 1. mainから新しいチェンジを作成（@ が main より1つ上になる）
jj new main -m "feat: 新機能Xを実装"

# 2. ★ 作業開始前に feature bookmark を作成する（重要）
jj bookmark create feat/feature-x

# 3. 作業する（ファイル編集はそのまま行うだけ）

# 4. さらに変更を積む場合
jj new -m "fix: レビュー指摘の修正"
jj bookmark set feat/feature-x   # bookmark を最新に移動

# 5. push して PR を作成
jj git push -b feat/feature-x
gh pr create --base main --head feat/feature-x
```

**アンチパターン（やってはいけない）**:

```bash
# ❌ main bookmark を進めてから push してしまうとPRが作れない
jj bookmark set main        # main を進める
jj git push                 # origin/main に直接 push される
# → origin/main にブランチ保護があると巻き戻し不可
```

### パターン2: バグ修正

```bash
# 1. mainの最新を取得
jj git fetch

# 2. main上で新しいチェンジを作成
jj new main@origin

# 3. 修正してコミット
jj describe -m "fix: ログイン時のエラーを修正"

# 4. ブックマークを作成してプッシュ
jj bookmark create fix-login
jj git push -b fix-login
```

### パターン3: 複数の作業を並行

```bash
# JJでは複数の作業を簡単に切り替えられる

# 作業Aを開始
jj new main
jj describe -m "作業A"
# ...作業...

# 作業Bに切り替え（作業Aは自動保存される）
jj new main
jj describe -m "作業B"
# ...作業...

# 作業Aに戻る
jj edit <作業AのチェンジID>
```

### パターン4: コードレビュー対応

```bash
# 1. レビュー指摘を受けたチェンジを編集
jj edit <該当チェンジ>

# 2. 修正を加える
# ...修正...

# 3. 子孫チェンジを更新（自動的にリベースされる）
# JJでは親の変更が自動的に子孫に伝播

# 4. プッシュ
jj git push -b <bookmark>
```

## Gitユーザー向けTips

### ステージングは不要

```bash
# Git
git add file.txt
git commit -m "message"

# JJ（addは不要）
jj commit -m "message"
```

### stashも不要

```bash
# Git
git stash
git checkout other-branch
git stash pop

# JJ（自動保存される）
jj new other-branch
# 戻りたいときは
jj edit <元のチェンジ>
```

### amend → squash または describe

```bash
# Git
git commit --amend

# JJ: メッセージだけ変更
jj describe -m "new message"

# JJ: 内容も親に統合
jj squash
```

## トラブルシューティング

### コンフリクトが発生した場合

```bash
# 1. コンフリクトの状態を確認
jj status

# 2. ファイルを編集してコンフリクトを解決
# JJはコンフリクトをファイル内にマーカーとして記録

# 3. 解決後、自動的にスナップショットされる
jj status  # コンフリクトが解消されたか確認
```

### 間違ってチェンジを放棄した場合

```bash
# 直前の操作を取り消し
jj undo

# または操作ログから復元
jj op log
jj op restore <operation_id>
```

### リモートと同期がおかしい場合

```bash
# リモートの状態を取得
jj git fetch

# ローカルのブックマークをリモートに合わせる
jj bookmark track main@origin
```

### 大きなチェンジを分割したい

```bash
# 対話的に分割
jj split

# 特定のファイルだけ分離
jj split path/to/file.txt
```

## 推奨設定

### ~/.config/jj/config.toml

```toml
[user]
name = "Your Name"
email = "your.email@example.com"

[ui]
# ページャーの設定
pager = "less -FRX"

# デフォルトのdiffフォーマット
diff.format = "git"

[git]
# プッシュ時に自動的にブックマークを追跡
auto-local-bookmark = true
```

## やってはいけないこと

1. **Gitコマンドを直接使わない**: JJリポジトリでは`git`コマンドではなく`jj git`を使う
2. **`.jj`ディレクトリを削除しない**: リポジトリのデータが失われる
3. **操作ログを無視しない**: 問題が起きたら`jj op log`で確認
4. **PR前に `jj bookmark set main` で main を進めない**: feature bookmark を作らずに main を直接進めて push すると、ブランチ保護のある `origin/main` は巻き戻せなくなり PR が作れない。必ず `jj bookmark create feat/xxx` を先に作ってから作業する

## 参考リンク

- 公式ドキュメント: https://www.jj-vcs.dev/
- GitコマンドとJJコマンドの対応表: https://www.jj-vcs.dev/latest/git-command-table/
- CLIリファレンス: https://www.jj-vcs.dev/latest/cli-reference/
- GitHub: https://github.com/martinvonz/jj
