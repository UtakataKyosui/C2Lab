# wasm-optimizer

JS/TS コードの重い処理を検出し、WebAssembly（WASM）や高速代替ライブラリへの最適化を提案するプラグイン。

## 概要

画像処理・暗号化・数値計算・圧縮・大量データ操作など、WASM で高速化できる処理パターンをファイル変更時に自動検出する。単一ファイルの分析からプロジェクト全体の監査まで段階的な最適化をサポートする。

## 提供コンポーネント

### Commands (Skills)

| コマンド | 説明 |
|----------|------|
| `init` | プロジェクトのバンドラー・WASM 設定状況を検出し、WASM 最適化の準備状況を確認する |
| `scan` | プロジェクト全体をスキャンし、WASM 最適化の機会を優先度付きでレポートする |
| `suggest <file>` | 指定ファイルの重い処理パターンを分析し、WASM 代替の before/after コードを提示する |
| `integrate <library>` | 指定 WASM ライブラリの統合ガイドを表示する（インストール・バンドラー設定・Worker 設定） |

### Agents

| エージェント | 説明 |
|--------------|------|
| `wasm-pattern-detector` | 単一の JS/TS ファイルを静的解析し、WASM 置き換え可能な重い処理パターンを検出して具体的な提案を行う |
| `wasm-audit-reporter` | プロジェクト全体の JS/TS ファイルを走査し、WASM 最適化の機会を優先度付きでレポートする |

### Skills

| スキル名 | 説明 |
|----------|------|
| `wasm-optimizer` | JS/TS コードの重い処理パターンを検出し、WASM や高速代替ライブラリへの最適化を提案する |

**スキルが自動ロードされるファイルパターン**:
- `**/*.js`, `**/*.ts`, `**/*.tsx`, `**/*.jsx`, `**/*.mjs`

### リファレンス

| ファイル | 内容 |
|----------|------|
| `references/wasm-library-catalog.md` | WASM ライブラリカタログ（用途別分類・パフォーマンス比較） |
| `references/integration-patterns.md` | WASM 統合パターン（Vite, Webpack, Worker 等） |

## 使い方

```
/init               # WASM 最適化の準備状況を確認
/scan               # プロジェクト全体を監査
/suggest src/utils/image.ts   # 特定ファイルを分析
/integrate sharp    # sharp ライブラリの統合ガイド
```

## フック

| イベント | 対象 | 処理 |
|----------|------|------|
| `PostToolUse` | Edit / Write | JS/TS ファイル変更後に `detect-heavy-patterns.py` で重い処理パターンを自動検出する |
