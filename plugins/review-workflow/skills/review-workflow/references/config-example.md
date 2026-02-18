# review-workflow 設定ファイルの例

`.claude/review-workflow.local.md` をプロジェクトルートに作成する。

## Next.js + TypeScript プロジェクト

```markdown
---
verify:
  typecheck: "npx tsc --noEmit"
  test: "npm test"
  lint: "npx eslint . --max-warnings 0"
---
```

## monorepo (pnpm workspace)

```markdown
---
verify:
  typecheck: "pnpm --filter=@myapp/dashboard exec tsc --noEmit"
  test: "pnpm --filter=@myapp/dashboard test"
  lint: "pnpm --filter=@myapp/dashboard exec eslint . --max-warnings 0"
  format: "pnpm --filter=@myapp/dashboard exec prettier --check ."
---
```

## Docker ベースのプロジェクト

```markdown
---
verify:
  typecheck: "cd web && npx tsc --noEmit"
  test: "cd web && npm test"
  build: "docker compose build web"
---
```

## Python プロジェクト

```markdown
---
verify:
  typecheck: "mypy src/"
  test: "pytest"
  lint: "ruff check ."
---
```

## Rust プロジェクト

```markdown
---
verify:
  check: "cargo check"
  test: "cargo test"
  clippy: "cargo clippy -- -D warnings"
---
```
