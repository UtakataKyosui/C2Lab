# ripgrep (rg) 正規表現パターン集

## TypeScript/JavaScript でよく使うパターン

```bash
# 関数・メソッド定義
rg 'export (function|const|class|type|interface) \w+'
rg '^(export )?(default )?(function|class) \w+'
rg 'const \w+ = (async )?\('  # アロー関数

# import/export
rg '^import .+ from ["\']'
rg '^export \{' -t ts
rg '^export default'

# React コンポーネント
rg '^(export (default )?)?function [A-Z]\w+\('  # 大文字始まり
rg "React\.FC|React\.Component|JSX\.Element"

# Hooks
rg 'use[A-Z]\w+\('  # useXxx() 形式
rg '^(export (default )?)?function use[A-Z]'  # カスタム Hook 定義

# 型定義
rg '^(export )?(type|interface) \w+'
rg ': (string|number|boolean|any|unknown|never)'

# async/await
rg 'async function|async \(' -t ts
rg 'await [a-zA-Z]'

# エラーハンドリング
rg 'try \{|catch \(|throw new'
rg '\.catch\(|\.finally\('
```

## セキュリティ関連パターン

```bash
# 危険なパターン
rg 'eval\('
rg 'innerHTML\s*='
rg 'dangerouslySetInnerHTML'
rg 'document\.write\('
rg '__proto__|prototype\.'

# 認証・シークレット
rg '(password|secret|token|api_key)\s*[:=]'
rg 'process\.env\.\w+'  # 環境変数使用箇所

# SQL インジェクションの可能性
rg 'query\s*[+]|execute\s*\('
```

## 複雑な検索

```bash
# 複数行にまたがるパターン
rg -U 'function \w+\([^)]*\)\s*\{' -t ts

# 特定コメントを含む行
rg '// TODO|// FIXME|// HACK|// XXX'
rg '\/\* istanbul ignore'

# console.log を検索（デバッグログ残り）
rg 'console\.(log|error|warn|debug)'

# 空の catch ブロック
rg -U 'catch\s*\([^)]*\)\s*\{\s*\}'

# 未使用変数（_ で始まるもの以外）
rg 'const [a-z]\w+ = ' | rg -v 'export|_'
```

## 除外パターン

```bash
# node_modules を除外（.gitignore で自動除外されるが明示的に）
rg pattern --glob '!node_modules/**'

# dist/build を除外
rg pattern --glob '!dist/**' --glob '!build/**' --glob '!.next/**'

# テストファイルを除外
rg pattern --glob '!**/*.test.*' --glob '!**/*.spec.*'

# 特定ディレクトリのみを検索
rg pattern src/api/ src/lib/

# 拡張子を除外
rg --type-not js pattern  # .js ファイルを除外
```

## 出力形式の制御

```bash
# ファイル名と行番号のみ（コンパクト）
rg -n --no-heading pattern

# ファイル名のみ（一致したファイル）
rg -l pattern

# 一致しないファイル
rg -L pattern

# 件数のみ
rg -c pattern

# カラーなし（パイプ処理向け）
rg --no-color pattern

# JSON 出力
rg --json pattern | jq '.data.lines.text'
```

## コンテキスト付き検索

```bash
# 前後 3 行
rg -C 3 pattern

# 定義を探す（前 1 行でコメント、後 5 行で実装）
rg -B 1 -A 5 'function myFunc'

# 最大幅を制限（長い行の省略なし）
rg --no-line-number --max-columns 200 pattern
```
