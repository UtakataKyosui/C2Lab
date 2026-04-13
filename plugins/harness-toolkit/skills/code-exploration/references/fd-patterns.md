# fd 高度なパターン集

## フィルタリング

```bash
# 特定拡張子のみ
fd -e ts -e tsx -e js

# 拡張子を除外
fd --exclude "*.min.js"

# タイプでフィルタ（f=ファイル、d=ディレクトリ、l=シンボリックリンク）
fd -t f           # ファイルのみ
fd -t d           # ディレクトリのみ

# 深さを制限
fd --max-depth 3

# 空ファイルを検索
fd --size 0

# 実行可能ファイルを検索
fd --executable

# 最近変更されたファイル
fd --changed-within 1h    # 1時間以内
fd --changed-within 7days # 7日以内
fd --changed-before 1week # 1週間より古い
```

## 大文字小文字

```bash
# 大文字小文字を区別しない（デフォルトはスマート検索）
fd -i pattern

# 正確に大文字小文字を区別する
fd -s Pattern
```

## 隠しファイル・gitignore

```bash
# 隠しファイルも含める（.gitignore は尊重）
fd -H pattern

# gitignore を無視して全ファイルを検索
fd -I pattern

# 両方（完全に全ファイル）
fd -HI pattern

# 特定ディレクトリを除外
fd -E node_modules -E .git -E dist pattern
```

## コマンド実行

```bash
# 各ファイルに対してコマンドを実行（{} = ファイルパス）
fd -e ts -x wc -l {}           # 行数を数える
fd -e ts -x prettier --write {} # フォーマット
fd -e log -x rm {}             # 削除

# 並列実行（デフォルト）
fd -e ts -x tsc --noEmit {}

# 逐次実行
fd -e ts -X tsc --noEmit {}

# 全ファイルをまとめて1コマンドに渡す
fd -e ts --print0 | xargs -0 tsc --noEmit
```

## よく使うユースケース

```bash
# テストファイルを全て検索
fd '\.test\.(ts|tsx)$'
fd --regex '\.spec\.(ts|js)$'

# 設定ファイルを検索
fd -g 'tsconfig*.json'
fd -g '*.config.{ts,js,json}'

# 特定の名前のファイルをディレクトリ内で検索
fd 'package.json' . --max-depth 2

# バイナリファイルを除外（テキストファイルのみ）
fd --type f --extension ts --extension js --extension py

# 最大サイズのファイルを検索
fd --size +1mb --type f

# シンボリックリンクを含める
fd -L pattern

# 結果をパイプで使用
fd -e ts | head -10  # 最初の10件
fd -e ts | wc -l     # 件数を数える
fd -e ts | sort      # ソート
```

## glob パターン

```bash
# シェル glob パターン（-g フラグ）
fd -g '*.{ts,tsx}'
fd -g 'index.*'
fd -g '**/components/**/*.tsx'

# 正規表現（デフォルト）
fd '\.(ts|tsx)$'
fd '^index\.'
```
