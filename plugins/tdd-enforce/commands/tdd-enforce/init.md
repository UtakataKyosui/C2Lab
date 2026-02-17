---
description: プロジェクトのTDD環境を初期化する。言語検出、テストフレームワーク提案、テスト設定の確認を行う。
---

# tdd-enforce: init

プロジェクトに TDD 環境を初期化します。

## 手順

### 1. プロジェクト言語の検出

プロジェクトルートのファイルから言語を特定する:

| ファイル | 言語 |
|---|---|
| `Cargo.toml` | Rust |
| `package.json` | TypeScript / JavaScript |
| `pyproject.toml`, `setup.py`, `requirements.txt` | Python |
| `go.mod` | Go |
| `*.csproj`, `*.sln` | C# / .NET |
| `pom.xml`, `build.gradle` | Java |

### 2. 既存テスト環境の確認

言語に応じて既存のテスト設定を確認する:

- **Rust**: `Cargo.toml` の `[dev-dependencies]`、`tests/` ディレクトリ
- **TypeScript**: `vitest.config.*`, `jest.config.*`, `package.json` の test スクリプト
- **Python**: `pytest.ini`, `pyproject.toml` の `[tool.pytest]`, `conftest.py`
- **Go**: `*_test.go` ファイルの存在

### 3. テストフレームワーク提案

テスト環境が未設定の場合、言語に応じた推奨フレームワークを提案する。
`/tdd-enforce:suggest-framework` コマンドの内容を参照し、ユーザーに選択させる。

### 4. テストコマンドの確認

プロジェクトでテスト実行に使うコマンドをユーザーに確認する:

```
検出されたテスト実行コマンド:
  cargo test

このコマンドでよろしいですか？
```

### 5. 初期化完了メッセージ

```
✓ TDD 環境初期化完了

プロジェクト: Rust
テストフレームワーク: cargo test (built-in)
テストディレクトリ: src/ (inline) + tests/

TDD を開始するには:
  1. /tdd-enforce:cycle でTDDサイクルを開始
  2. Write/Edit 時に自動でテスト存在チェックが実行されます
```
