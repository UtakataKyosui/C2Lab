---
name: コード探索（fd / ripgrep / tre）
description: This skill should be used when the user wants to "ファイルを検索", "コードを検索", "ディレクトリ構造を確認", use "fd", "rg", "ripgrep", "tre", search for specific patterns in code, find files by name or extension, or explore codebase structure. Also activates when user asks about "高速ファイル検索", "コード内検索", or mentions Rust-based CLI search tools.
version: 0.1.0
---

# コード探索（fd / ripgrep / tre）

`fd`・`ripgrep`・`tre` は従来の `find`・`grep`・`tree` を Rust で高速に再実装したツール群。`.gitignore` を自動尊重し、高速な検索を実現する。

## fd — ファイル検索（find の代替）

### 基本使用法

```bash
# ファイル名でパターン検索（デフォルトは部分一致）
fd <pattern>

# 特定のディレクトリ内を検索
fd <pattern> <dir>

# 拡張子で絞り込み
fd -e ts          # .ts ファイルのみ
fd -e ts -e tsx   # .ts と .tsx

# 完全一致（正規表現）
fd '^index\.ts$'

# 隠しファイルも含める
fd -H <pattern>

# .gitignore を無視
fd -I <pattern>

# ディレクトリを除外
fd -E node_modules -E dist <pattern>
```

### よく使うパターン

```bash
# 特定ディレクトリ配下の TypeScript ファイルを全て見つける
fd -e ts src/

# テストファイルを見つける
fd '\.test\.' -e ts

# 設定ファイルを見つける
fd -g '*.config.*'

# 最近更新されたファイルを見つける（30秒以内）
fd --changed-within 30s

# 特定サイズ以上のファイルを見つける
fd --size +1mb

# 見つけたファイルに対してコマンドを実行
fd -e ts -x wc -l {}
```

### find との違い

```bash
# find (非推奨)
find . -name "*.ts" -not -path "*/node_modules/*"

# fd (推奨) — gitignore を自動尊重
fd -e ts
```

## ripgrep (rg) — コード内検索（grep の代替）

### 基本使用法

```bash
# パターン検索
rg <pattern>

# 特定ディレクトリを検索
rg <pattern> <dir>

# 大文字小文字を無視
rg -i <pattern>

# 完全一致（単語単位）
rg -w <pattern>

# 行番号を表示（デフォルトで表示）
rg -n <pattern>

# マッチしたファイル名のみ表示
rg -l <pattern>

# マッチしたファイルとカウントを表示
rg -c <pattern>
```

### ファイル種別でフィルタ

```bash
# TypeScript のみ
rg --type ts <pattern>
rg -t ts <pattern>

# 複数の型
rg -t ts -t tsx <pattern>

# 特定拡張子を除外
rg --type-not js <pattern>
```

### コンテキスト表示

```bash
# マッチ前後 3 行を表示
rg -C 3 <pattern>

# マッチ前 2 行
rg -B 2 <pattern>

# マッチ後 2 行
rg -A 2 <pattern>
```

### 高度な検索

```bash
# 正規表現で検索
rg 'function\s+\w+\s*\('

# 複数パターンを OR 検索
rg 'pattern1|pattern2'

# 関数定義を検索
rg 'export (function|const|class) \w+'

# import 文を検索
rg '^import .+ from'

# 特定文字列を含まない行
rg -v 'exclude_pattern'

# 隠しファイルも含める
rg -. <pattern>

# .gitignore を無視
rg --no-ignore <pattern>

# 特定ディレクトリを除外
rg --glob '!node_modules/**' <pattern>
```

### grep との違い

```bash
# grep (非推奨)
grep -r "pattern" src/ --include="*.ts" --exclude-dir=node_modules

# rg (推奨) — gitignore 自動尊重、高速
rg "pattern" -t ts src/
```

## tre — ディレクトリ構造表示（tree の代替）

### 基本使用法

```bash
# カレントディレクトリのツリー表示
tre

# 特定ディレクトリのツリー表示
tre <dir>

# 深さを制限
tre -d 2      # 2階層まで
tre --depth 3 # 3階層まで

# 隠しファイルを含める
tre -a

# ファイルのみ（ディレクトリを除く）
# デフォルトで .gitignore を尊重
```

### 出力をコンテキストに使う

```bash
# ディレクトリ構造をコンパクトに把握
tre -d 2 src/

# node_modules 等を除外（.gitignore で管理されていれば自動除外）
tre src/
```

## 組み合わせパターン

### コードベース全体の調査

```bash
# 1. ディレクトリ構造を把握
tre -d 2

# 2. 特定のファイル種別を一覧
fd -e ts src/

# 3. 特定パターンを持つファイルを検索
rg -l 'useEffect' src/

# 4. 詳細を確認
rg -C 3 'useEffect' src/components/
```

### 特定の関数・クラスを見つける

```bash
# 関数定義の場所を特定
rg 'export function myFunction' -l

# 使用箇所を特定
rg 'myFunction' --type ts

# ファイルの場所を確認
fd 'myFile.ts'
```

### rtk でトークンを削減

検索結果が大きい場合、rtk でトークンを削減する:

```bash
# rg の出力をトークン削減（rtk が利用可能な場合）
rg 'pattern' | rtk

# fd の出力をトークン削減
fd -e ts | rtk
```

## 注意事項

- Claude Code の Grep ツールは内部で ripgrep を使用 → 単純な検索は Grep ツールで十分
- 複雑なパイプライン処理や CLI ツールの出力を他コマンドに渡す場合に Bash で fd/rg を直接使う
- `fd` と `rg` は `.gitignore` を自動尊重するため、`node_modules`・`dist` 等は基本的に自動除外

## Additional Resources

- **`references/fd-patterns.md`** - fd の高度なパターン集
- **`references/rg-patterns.md`** - ripgrep の正規表現パターン集
