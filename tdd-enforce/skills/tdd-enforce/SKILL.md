---
name: tdd-enforce
description: テスト駆動開発（TDD）の方法論とRed-Green-Refactorサイクルの実践ガイド。テストの書き方、言語別テストフレームワークの選定、TDDパターンを提供する。テスト、TDD、テスト駆動、ユニットテスト、テストファーストに関する質問時に使用する。
globs:
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/*_test.*"
  - "**/test_*.*"
  - "**/tests/**"
  - "**/__tests__/**"
---

# Test-Driven Development (TDD) Enforcement Guide

## TDD の基本原則

**すべての実装コードには、対応するテストが必要。テストを先に書き、テストが失敗することを確認してから実装する。**

### Red-Green-Refactor サイクル

1. **Red**: 失敗するテストを書く
   - 実装したい振る舞いをテストとして記述
   - テストを実行し、失敗することを確認（コンパイルエラーも Red）
2. **Green**: テストをパスする最小限のコードを書く
   - テストを通すために必要最小限のコードだけを実装
   - 完璧な設計は後回し
3. **Refactor**: コードを改善する
   - テストがパスした状態を維持しながらリファクタリング
   - 重複排除、命名改善、構造整理

### テスト設計パターン

**Arrange-Act-Assert (AAA)**:
```
// Arrange: テストの準備
// Act: テスト対象の実行
// Assert: 結果の検証
```

**Given-When-Then**:
```
// Given: 前提条件
// When: 操作
// Then: 期待結果
```

## 言語別テストフレームワーク Quick Reference

| 言語 | フレームワーク | コマンド |
|---|---|---|
| Rust | cargo test (built-in) | `cargo test` |
| TypeScript/JS | Vitest | `npx vitest` |
| TypeScript/JS | Jest | `npx jest` |
| Python | pytest | `pytest` |
| Go | testing (built-in) | `go test ./...` |
| C# | xUnit / NUnit | `dotnet test` |
| Java | JUnit 5 | `mvn test` / `gradle test` |
| Ruby | RSpec / Minitest | `rspec` / `ruby -Itest` |
| Elixir | ExUnit (built-in) | `mix test` |
| Swift | XCTest (built-in) | `swift test` |

## テストファイル命名規則

| 言語 | テストファイルパターン | 例 |
|---|---|---|
| Rust | 同一ファイル内 `#[cfg(test)]` or `tests/` | `src/lib.rs`, `tests/integration.rs` |
| TypeScript | `{name}.test.ts`, `{name}.spec.ts` | `Button.test.tsx` |
| Python | `test_{name}.py`, `{name}_test.py` | `test_parser.py` |
| Go | `{name}_test.go` | `parser_test.go` |
| Java | `{Name}Test.java` | `ParserTest.java` |

## TDD でテストが不要なもの

以下のファイルはテスト不要:
- 設定ファイル（`*.config.*`, `*.json`, `*.yaml`, `*.toml`, `Cargo.toml` 等）
- README、ドキュメント（`*.md`）
- 型定義のみのファイル（`*.types.ts`, `*.d.ts`）
- バレルファイル（`index.ts` でエクスポートのみ）
- 環境変数（`.env*`）
- CI/CD 設定（`.github/`, `Dockerfile` 等）

## 詳細ドキュメント

- [testing-frameworks.md](./testing-frameworks.md) - 言語別テストフレームワーク詳細ガイド
- [tdd-patterns.md](./tdd-patterns.md) - TDD パターンとアンチパターン
- [test-design.md](./test-design.md) - テスト設計の原則とベストプラクティス
