# rust

Rust 開発を支援するプラグイン。コードのデバッグ・最適化・レビューをサブエージェントで提供し、ファイル保存時に自動でコード品質チェックを実行する。

## 概要

Rust プロジェクトのコード品質維持を支援する。デバッグ・最適化・レビューの専門エージェントと、プロンプト入力チェック・cargo ツールによる自動検証フックを備える。Rust プロジェクト（`Cargo.toml` が存在するディレクトリ）でのみ動作する。

## 提供コンポーネント

### Agents

| エージェント | 説明 |
|--------------|------|
| `rust-code-debugger` | コンパイルエラー、borrow-checker 問題、ランタイムパニック、ロジックバグの根本原因を特定する |
| `rust-code-optimizer` | パフォーマンス・メモリ効率・クリーンアーキテクチャの観点で Rust コードを最適化する |
| `rust-code-reviewer` | 正確性・可読性・設計・慣用的 Rust の観点でコードをレビューする |

### Skills

| スキル名 | 説明 |
|----------|------|
| `rust-coder` | イディオマティックで効率的な Rust コードを書くためのガイド（データモデリング、トレイト、マクロ等） |
| `rust-debugger` | Rust のコンパイルエラー、borrow-checker 問題、パニック、ロジックバグの診断と修正 |

### ガイド

| ファイル | 内容 |
|----------|------|
| `skills/rust-coder/examples.md` | Rust コードの実例 |
| `skills/rust-coder/reference.md` | Rust 言語リファレンス |

## 使い方

```
# デバッグを依頼
rust-code-debugger エージェントで以下のエラーを調査して

# 最適化を依頼
rust-code-optimizer でこの関数のパフォーマンスを改善して

# レビューを依頼
rust-code-reviewer でコードレビューして
```

## フック

| イベント | 対象 | 処理 |
|----------|------|------|
| `SessionStart` | — | `pip3 install -q -r requirements.txt`（mistune をインストール） |
| `UserPromptSubmit` | — | Cargo.toml がある場合のみ `prompt-check.py` でプロンプトの Markdown 形式を検証する |
| `PostToolUse` | Edit / Write | Cargo.toml がある場合のみ `hook-tools.py` で `cargo check` / `cargo clippy` / `cargo fmt` を実行する |
| `Stop` | — | Cargo.toml がある場合のみ `hook-tools.py` で最終的なコード品質チェックを実行する |

> Rust プロジェクト外（`Cargo.toml` が存在しないディレクトリ）では、すべてのフックが自動的にスキップされる。
