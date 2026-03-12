# CI チェックコマンドリファレンス

push 前に実行すべき CI コマンドを言語・ツールごとに示す。

## TypeScript / JavaScript

```bash
# フォーマット確認
npx prettier --check .

# フォーマット自動修正
npx prettier --write .

# Lint
npx eslint . --max-warnings 0

# 型チェック
npx tsc --noEmit

# テスト
pnpm test
# または
npm test
```

monorepo（pnpm workspace）の場合:

```bash
pnpm --filter=<package-name> exec prettier --check .
pnpm --filter=<package-name> exec eslint . --max-warnings 0
```

## Python

```bash
# Lint
ruff check .

# フォーマット確認
ruff format --check .

# フォーマット自動修正
ruff format .

# 型チェック（mypy を使う場合）
mypy .
```

## Rust

```bash
# フォーマット確認
cargo fmt --check

# フォーマット自動修正
cargo fmt

# Lint
cargo clippy -- -D warnings

# テスト
cargo test
```

## Markdown / ドキュメント

```bash
# textlint（globstar が必要なため shopt を明示、または find で展開）
shopt -s globstar && npx textlint **/*.md
# または: npx textlint $(find . -name "*.md" -not -path "*/node_modules/*")

# markdownlint
shopt -s globstar && npx markdownlint **/*.md
# または: npx markdownlint $(find . -name "*.md" -not -path "*/node_modules/*")
```

## 複数言語が混在するプロジェクト

ファイルの変更差分を確認して、変更がある言語の CI のみ実行する:

```bash
# 変更ファイル一覧を確認（main ブランチとの差分）
git diff --name-only main...HEAD  # git
jj diff --name-only -r 'main..@'  # jj
```

**推奨**: 変更量が小さくても、全 CI を一度に実行して push する。
部分的に CI を通しても、push 後に別の CI が落ちるリスクが残る。
