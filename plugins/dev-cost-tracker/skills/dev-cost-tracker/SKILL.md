---
name: dev-cost-tracker
description: 開発コストの追跡・分析ガイド。コスト、トークン使用量、費用、予算、見積もり、費用対効果に関する質問時に使用する。
globs:
  - "**/.dev-costs.json"
---

# Development Cost Tracking Guide

## 概要

Claude Code を使った開発のコスト（トークン使用量・費用）を機能単位で追跡するためのガイド。定額プランでも従量課金ベースでコストを算出し、費用対効果の分析や見積もりの参考にする。

## コスト情報の取得

`ccusage` を使い、`~/.claude/projects/` のログからセッション単位のコストを取得する。

```bash
# セッション別コストを JSON で取得
npx ccusage@latest session --json

# 特定セッションのみ取得
npx ccusage@latest session --json --id <session-id>

# 日付フィルタ
npx ccusage@latest session --json --since 20260222

# キャッシュ済み料金を使用（高速化）
npx ccusage@latest session --json --offline
```

### ccusage session --json の出力形式

```json
{
  "sessions": [
    {
      "sessionId": "プロジェクトパスベースのID",
      "inputTokens": 76,
      "outputTokens": 8354,
      "cacheCreationTokens": 141434,
      "cacheReadTokens": 3508839,
      "totalTokens": 3658703,
      "totalCost": 2.85,
      "lastActivity": "2026-02-22",
      "modelsUsed": ["claude-opus-4-6"],
      "modelBreakdowns": [
        {
          "modelName": "claude-opus-4-6",
          "inputTokens": 76,
          "outputTokens": 8354,
          "cacheCreationTokens": 141434,
          "cacheReadTokens": 3508839,
          "cost": 2.85
        }
      ],
      "projectPath": "Unknown Project"
    }
  ]
}
```

## コストの記録フロー

1. 作業完了後に `/record-cost` を実行
2. `ccusage session --json` でコスト情報を自動取得
3. 機能名とメタデータを入力
4. `.dev-costs.json` に保存

## .dev-costs.json スキーマ

```json
{
  "version": "1.0.0",
  "records": [
    {
      "id": "UUID v4",
      "feature_name": "機能名（必須）",
      "date": "YYYY-MM-DD",
      "session_id": "セッションID",
      "duration_minutes": null,
      "files_changed": null,
      "tool_calls": null,
      "input_tokens": 150000,
      "output_tokens": 30000,
      "cache_read_tokens": 3508839,
      "cache_creation_tokens": 141434,
      "total_cost_usd": 1.25,
      "model": "claude-opus-4-6",
      "memo": null,
      "recorded_at": "ISO 8601 with timezone"
    }
  ]
}
```

## 分析のヒント

### コスト効率の指標

- **1機能あたりの平均コスト**: 全レコードの `total_cost_usd` の平均
- **トークン効率**: `output_tokens / input_tokens` の比率（低いほどコンテキストが大きい）
- **キャッシュ効率**: `cache_read_tokens / input_tokens` の比率（高いほどキャッシュが効いている）
- **時間あたりコスト**: `total_cost_usd / duration_minutes`

### コスト削減のポイント

- 大きな機能は小さなタスクに分割して記録する
- コンテキストが大きくなりすぎたらセッションを分割する
- 類似タスクのコストを比較して見積もりの精度を上げる
- キャッシュ効率が低い場合はプロンプトの構造を見直す

### レポート作成

`.dev-costs.json` のデータを使って以下の分析が可能:

- 機能別コストランキング
- 日別・週別コスト推移
- モデル別コスト比較
- プロジェクト全体の累計コスト
- キャッシュ効率の推移

## 参考: その他のコスト監視手段

- **OpenTelemetry**: `CLAUDE_CODE_ENABLE_TELEMETRY=1` で `claude_code.cost.usage` / `claude_code.token.usage` メトリクスを収集可能。組織的な監視向け（https://code.claude.com/docs/ja/monitoring-usage）
- **ROI 測定ガイド**: https://github.com/anthropics/claude-code-monitoring-guide
