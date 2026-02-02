# JJ 主要コマンド詳細

各コマンドの詳細な使い方とオプションを解説します。

## jj new - 新規チェンジ作成

ワークフローの基本となるコマンド。新しいチェンジを作成します。

```bash
# 現在のチェンジの子として新規チェンジを作成
jj new

# 特定のリビジョンから新規チェンジを作成
jj new <revision>

# 複数の親を持つチェンジを作成（マージ）
jj new <rev1> <rev2>

# メッセージ付きで新規チェンジ作成
jj new -m "作業開始: 機能追加"

# 特定のブックマーク上に新規チェンジ
jj new main
```

### オプション
- `-m, --message <MESSAGE>`: チェンジの説明を指定
- `-r, --revision <REVISION>`: 親リビジョンを指定（複数指定可）
- `-A, --insert-after`: 指定リビジョンの後に挿入
- `-B, --insert-before`: 指定リビジョンの前に挿入

## jj describe - チェンジ説明の編集

チェンジのメタデータ（説明文）を更新します。エイリアス: `jj desc`

```bash
# エディタで現在のチェンジの説明を編集
jj describe

# メッセージを直接指定
jj describe -m "バグ修正: ログイン処理のエラー対応"

# 特定のリビジョンの説明を編集
jj describe -r <revision>

# 複数行のメッセージ
jj describe -m "タイトル" -m "詳細な説明"
```

### オプション
- `-m, --message <MESSAGE>`: 説明文を指定（複数回使用可）
- `-r, --revision <REVISION>`: 対象リビジョンを指定
- `--reset-author`: 作者情報をリセット
- `--stdin`: 標準入力から説明を読み込み

## jj commit - コミット

現在のワーキングコピーの変更を確定し、新しい空のチェンジを作成します。エイリアス: `jj ci`

```bash
# 現在のワーキングコピーをコミット（エディタが開く）
jj commit

# メッセージを指定してコミット
jj commit -m "機能実装完了"

# 対話的にファイルを選択
jj commit -i
```

### オプション
- `-m, --message <MESSAGE>`: コミットメッセージを指定
- `-i, --interactive`: 対話的にファイル/部分を選択
- `--reset-author`: 作者情報をリセット

## jj squash - 変更の統合

チェンジの内容を別のチェンジに統合します。

```bash
# 現在のチェンジを親に統合
jj squash

# 特定のチェンジを親に統合
jj squash -r <revision>

# 対話的に一部の変更だけ統合
jj squash -i

# 特定の宛先に統合
jj squash --into <destination>
```

### オプション
- `-r, --revision <REVISION>`: 統合元のリビジョン
- `--into <DESTINATION>`: 統合先のリビジョン（デフォルトは親）
- `-i, --interactive`: 対話的に選択
- `-m, --message <MESSAGE>`: 統合後のメッセージ

## jj rebase - リベース

リビジョンを異なる親の下に移動します。

```bash
# 現在のチェンジを別の親に移動
jj rebase -d <destination>

# 特定のリビジョンをリベース
jj rebase -r <revision> -d <destination>

# ブランチ全体をリベース
jj rebase -b <branch> -d <destination>

# ソース（およびその子孫）をリベース
jj rebase -s <source> -d <destination>
```

### オプション
- `-d, --destination <DESTINATION>`: 新しい親リビジョン
- `-r, --revisions <REVISION>`: リベースするリビジョン
- `-s, --source <SOURCE>`: ソースリビジョン（子孫も含む）
- `-b, --branch <BRANCH>`: ブランチリビジョン（祖先も含む）

## jj bookmark - ブックマーク管理

Gitのブランチに相当するブックマークを管理します。

```bash
# ブックマーク一覧
jj bookmark list
jj bookmark list -a  # すべて（リモート含む）

# ブックマーク作成
jj bookmark create feature-x -r @
jj bookmark create feature-x  # 現在のチェンジに作成

# ブックマーク移動
jj bookmark move main --to @
jj bookmark move feature-x --to <revision>

# ブックマーク削除
jj bookmark delete feature-x

# リモートブックマークの追跡
jj bookmark track main@origin
jj bookmark untrack main@origin
```

### サブコマンド
- `list`: ブックマーク一覧
- `create`: 新規作成
- `delete`: 削除
- `move`: 移動
- `rename`: 名前変更
- `track`: リモートブックマークを追跡
- `untrack`: 追跡を解除

## jj git - Git連携

Gitリポジトリとの連携操作を行います。

```bash
# リモートから取得
jj git fetch
jj git fetch --remote origin
jj git fetch --all-remotes

# プッシュ
jj git push --all
jj git push -b <bookmark>
jj git push -b feature-x --remote origin

# クローン
jj git clone <url>
jj git clone <url> <directory>

# Gitリモート管理
jj git remote list
jj git remote add origin <url>
jj git remote remove origin
```

### サブコマンド
- `fetch`: リモートから取得
- `push`: リモートにプッシュ
- `clone`: リポジトリをクローン
- `remote`: リモート管理
- `init`: Gitリポジトリとして初期化

## jj split - チェンジの分割

チェンジを複数の小さなチェンジに分割します。

```bash
# 対話的にチェンジを分割
jj split

# 特定のリビジョンを分割
jj split -r <revision>

# 特定のファイルを別チェンジに分離
jj split <file1> <file2>
```

## jj abandon - チェンジの放棄

チェンジを放棄し、子孫を親に接続します。

```bash
# 現在のチェンジを放棄
jj abandon

# 特定のリビジョンを放棄
jj abandon <revision>
```

## jj edit - リビジョンの編集

特定のリビジョンをワーキングコピーとして設定します。

```bash
# 特定のリビジョンを編集
jj edit <revision>

# ブックマークを編集
jj edit main
```

## jj log - 履歴表示

リポジトリの履歴を表示します。

```bash
# 履歴を表示
jj log

# グラフなしで表示
jj log --no-graph

# パッチ付きで表示
jj log -p

# 特定のリビジョン範囲
jj log -r <revset>

# 逆順で表示
jj log --reversed
```

## jj diff - 差分表示

変更の差分を表示します。

```bash
# 現在のチェンジの差分
jj diff

# 特定のリビジョンの差分
jj diff -r <revision>

# 2つのリビジョン間の差分
jj diff --from <rev1> --to <rev2>

# 特定のファイルの差分
jj diff <file>

# 統計情報のみ
jj diff --stat
```

## jj undo - 操作の取り消し

直前の操作を取り消します。JJ固有の強力な機能です。

```bash
# 直前の操作を取り消し
jj undo

# 操作ログを確認
jj op log

# 特定の操作時点に復元
jj op restore <operation_id>
```
