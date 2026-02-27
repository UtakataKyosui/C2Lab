# scaffdog-colocation

scaffdog を使ったコロケーションパターンの導入・管理を支援するプラグイン。

## 概要

コンポーネント・機能単位でファイルをグループ化するコロケーションパターンの実践を支援する。scaffdog テンプレートの生成・スキャフォールディング・バリデーションを提供し、プロジェクト全体で一貫したファイル構造を維持する。ファイル保存時に自動でコロケーション違反を検出する。

## 提供コンポーネント

### Commands (Skills)

| コマンド | 説明 |
|----------|------|
| `init` | scaffdog とコロケーションパターンをプロジェクトに導入する。フレームワーク検出・scaffdog インストール案内・スターターテンプレート生成を行う。 |
| `generate-template` | 指定されたファイルタイプと設定に基づいて scaffdog テンプレートファイルを生成する |
| `scaffold` | scaffdog テンプレートからファイルをスキャフォールディングする。CLI または Claude 直接作成を選択可能。 |
| `validate` | プロジェクトのファイル構造がコロケーションパターンに準拠しているか検証し、違反レポートを生成する |
| `add-file-type` | 既存のコンポーネントディレクトリに新しいファイルタイプ（stories, constants, hooks 等）を追加する |

### Agents

| エージェント | 説明 |
|--------------|------|
| `colocation-validator` | プロジェクトのファイル構造がコロケーションパターンに準拠しているか検証し、違反を Markdown テーブルで報告する |
| `scaffdog-template-generator` | フレームワーク検出とユーザー設定に基づいて正確な scaffdog テンプレートファイルを生成する |

### Skills

| スキル名 | 説明 |
|----------|------|
| `scaffdog-colocation` | コロケーションパターンに基づくファイル分割と scaffdog テンプレート生成を支援する |

**スキルが自動ロードされるファイルパターン**:
- `.scaffdog/**/*.md`

### ガイド

| ファイル | 内容 |
|----------|------|
| `colocation-patterns.md` | コロケーションパターンの概念と実践方法 |
| `framework-examples.md` | React, Vue, Next.js 等のフレームワーク別の実例 |
| `file-naming-conventions.md` | ファイル命名規則 |
| `scaffdog-syntax.md` | scaffdog テンプレート構文リファレンス |

## 使い方

```
/init                  # プロジェクトにコロケーションを導入
/scaffold              # テンプレートからファイルを生成
/validate              # コロケーション違反を確認
/add-file-type stories # stories ファイルを追加
```

## フック

| イベント | 対象 | 処理 |
|----------|------|------|
| `PostToolUse` | Edit / Write | ファイル変更後に `validate-colocation.py` でコロケーション違反を自動検出する |
