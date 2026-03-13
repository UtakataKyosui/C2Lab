---
name: ci-check
description: プロジェクトの CI チェック（lint・format・型チェック・テスト）をローカルで実行する。push 前の検証に使用する。
argument-hint: "[--fix] [--only=ts|py|rust|md]"
allowed-tools:
  - Bash
  - Read
  - Glob
---

# CI チェック実行コマンド

プロジェクトの種類を自動検出して、対応する CI コマンドをすべて実行する。

## 実行手順

1. プロジェクトルートで以下のファイルを確認して言語を検出する:
   - `package.json` → TypeScript/JavaScript
   - `pyproject.toml` または `setup.py` → Python
   - `Cargo.toml` → Rust
   - `.markdownlint*` / `.textlintrc*` などの設定ファイルが存在する、または `package.json` に `markdownlint` / `textlint` の依存が含まれる → Markdown lint

2. `--only=<lang>` が指定されている場合はその言語のみ実行する。
   指定がない場合は検出されたすべての言語の CI を実行する。

3. `--fix` が指定されている場合、自動修正可能なエラー（format など）を修正してから再確認する。

4. 各 CI コマンドを順番に実行し、結果を表示する:
   - ✅ PASS: コマンドが成功した場合
   - ❌ FAIL: コマンドが失敗した場合（エラー内容を表示）

5. 全チェック完了後にサマリーを表示する:
   ```
   CI チェック結果:
   ✅ prettier: PASS
   ❌ eslint: FAIL (3 errors)
   ✅ tsc: PASS

   → 1 件の失敗があります。push 前に修正してください。
   ```

6. すべて PASS した場合のみ「push 可能です」と伝える。
   1 つでも FAIL がある場合は push を推奨しない。

## 注意事項

- CI コマンドの詳細は `pr-lifecycle` スキルの `references/ci-checks.md` を参照する
- monorepo の場合は `pnpm --filter` でパッケージを絞り込む
- 引数に `--fix` を指定した場合は format の自動修正を行うが、lint エラーは手動修正が必要
