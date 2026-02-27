# review-workflow

PR レビューコメントへの対応を自動化するプラグイン。

## 概要

GitHub PR のレビューコメントを取得し、コード修正・検証・コミット・Push までの一連のワークフローを自動実行する。`review-fixer` サブエージェントが各レビュースレッドを処理し、修正計画（`fix-plan.json`）を出力する。

## 提供コンポーネント

### Commands (Skills)

| コマンド | 説明 |
|----------|------|
| `respond-review` | PR レビューコメントを取得し、修正・検証・コミット・Push までの一連のワークフローを実行する |

**使用ツール**: Bash, Read, Edit, Write, Glob

### Agents

| エージェント | 説明 |
|--------------|------|
| `review-fixer` | PR レビューコメントに基づいてコード修正を実施する SubAgent。修正計画（`fix-plan.json`）を出力する。 |

### Skills

| スキル名 | 説明 |
|----------|------|
| `review-workflow` | PR レビュー対応ワークフローの自動化スキル。レビューコメント取得から修正・検証・コミット・Push の流れを管理する。 |

### リファレンス

| ファイル | 内容 |
|----------|------|
| `references/fix-plan-format.md` | `fix-plan.json` の出力フォーマット仕様 |
| `references/config-example.md` | ワークフロー設定例 |

## 使い方

```
/respond-review    # PR レビューコメントへの対応を開始
```

PR番号を指定するか、現在のブランチから自動検出してレビューコメントに対応する。

## フック

なし
