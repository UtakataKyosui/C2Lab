# dev-cost-tracker

Claude Code の開発コスト（トークン使用量・費用）を機能単位で記録するプラグイン。

## 機能

- **セッション終了時のリマインダー**: Stop フックでコスト未記録のセッションをリマインド
- **`/record-cost` コマンド**: `/cost` の出力を元に `.dev-costs.json` へコスト情報を記録
- **コスト分析スキル**: 記録されたデータの分析・レポート作成をサポート

## インストール

```bash
claude plugins add ./plugins/dev-cost-tracker
```

## 使い方

### コストの記録

作業が完了し、コストを記録するタイミングで `/record-cost` を実行します。
セッション情報を元に `ccusage` 経由でコスト情報が自動取得・記録されます。

1. `/record-cost` を実行
2. （自動処理）環境変数のセッションIDを元に `ccusage` でコスト情報を取得
3. （自動取得に失敗した場合のフォールバック）`/cost` コマンドで手動取得した出力を貼り付ける
4. 機能名を入力（作業時間・メモは任意）
5. 内容を確認して保存

### データの確認

`.dev-costs.json` に JSON 形式で記録される。コスト分析や見積もりの参考に利用できる。

## ファイル構成

```
dev-cost-tracker/
├── .claude-plugin/
│   └── plugin.json          # プラグインマニフェスト
├── hooks/
│   ├── hooks.json            # フック定義
│   └── scripts/
│       ├── stop_reminder.py      # Stop フックスクリプト
│       └── test_stop_reminder.py # テスト
├── commands/
│   └── dev-cost-tracker/
│       └── record-cost.md    # /record-cost コマンド
├── skills/
│   └── dev-cost-tracker/
│       └── SKILL.md          # コスト分析スキル
└── README.md
```

## ライセンス

MIT
