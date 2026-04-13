# jj コマンド完全リファレンス

## 基本コマンド

### jj log

```bash
jj log                          # デフォルトのログ表示
jj log --no-pager              # ページャなし
jj log -r main..@              # main から @ までの変更
jj log -r 'ancestors(@, 10)'  # 直近10コミット
jj log -T builtin_log_detailed # 詳細テンプレート
jj log --summary               # ファイル変更サマリー付き
```

### jj diff

```bash
jj diff                        # 現在の変更の差分
jj diff -r <rev>               # 指定リビジョンの差分
jj diff --from @- --to @       # 2つのリビジョン間の差分
jj diff --stat                 # 変更ファイルのサマリー
jj diff --name-only            # 変更ファイル名のみ
jj diff -- path/to/file        # 特定ファイルの差分
```

### jj commit / describe

```bash
jj commit -m "message"        # 変更を確定し新しい Change を作成
jj describe -m "message"      # 現在の Change の説明を変更
jj describe                   # エディタで説明を編集（非推奨：--no-edit を使う）
```

### jj new / edit

```bash
jj new                        # 新しい空の Change を作成
jj new main                   # main の上に新しい Change を作成
jj new @-                     # 親の上に新しい Change を作成（分岐）
jj edit <rev>                 # 指定リビジョンに移動して編集
```

### jj bookmark

```bash
jj bookmark list              # ブックマーク一覧
jj bookmark list --all        # リモートを含む全ブックマーク
jj bookmark create <name>     # 現在の @ にブックマークを作成
jj bookmark create <name> -r <rev>  # 指定リビジョンにブックマーク作成
jj bookmark set <name>        # 現在の @ にブックマークを移動
jj bookmark set <name> -r <rev>     # 指定リビジョンにブックマークを移動
jj bookmark delete <name>     # ブックマークを削除
jj bookmark track <name>@origin     # リモートブックマークをトラッキング
```

### jj rebase

```bash
jj rebase -d <target>         # 現在の Change を target にリベース
jj rebase -b <bookmark> -d <target>  # ブックマーク全体をリベース
jj rebase -r <rev> -d <target>       # 特定リビジョンをリベース
jj rebase -s <source> -d <target>    # source 以降の全 Change をリベース
```

### jj squash / unsquash

```bash
jj squash                     # 現在の Change を親にスカッシュ
jj squash --into @-           # 親にスカッシュ（明示的）
jj squash -r <rev>            # 指定リビジョンを親にスカッシュ
jj squash --interactive       # インタラクティブに選択（非推奨）
```

### jj split

```bash
jj split                      # 現在の Change を2つに分割（インタラクティブ）
jj split -- path/to/file      # 特定ファイルを別の Change に分割
```

### jj restore

```bash
jj restore path/to/file       # ファイルを変更前に戻す
jj restore .                  # 全ファイルを戻す
jj restore --from <rev> file  # 指定リビジョンからファイルを復元
```

### jj workspace

```bash
jj workspace list             # workspace 一覧
jj workspace add <path> -r <bookmark>  # workspace を追加
jj workspace forget <path>    # workspace を削除（cwd が stale になる場合あり）
```

### jj git

```bash
jj git fetch                  # リモートから取得
jj git fetch --all-remotes    # 全リモートから取得
jj git push                   # プッシュ（shell wrapper でブロックされる場合 command を付ける）
jj git push --bookmark <name> # 特定ブックマークをプッシュ
jj git push --all             # 全ブックマークをプッシュ
jj git push --dry-run         # ドライラン（実際には push しない）
```

### jj undo / undo

```bash
jj undo                       # 最後の操作を取り消し
jj op log                     # 操作履歴
jj op restore <op-id>         # 特定の操作状態に戻す
```

## リビジョン指定の書式

```
@           現在の Change
@-          親の Change
@--         祖父母の Change
main        main ブックマーク
abc1234     リビジョンID（先頭数文字で可）
trunk()     メインブランチのルート
ancestors(@, 5)  @ の5世代前まで
```

## テンプレート記法

```bash
# カスタムログフォーマット
jj log -T 'commit_id ++ " " ++ description.first_line() ++ "\n"'

# ブックマークを含むログ
jj log -T builtin_log_compact
```
