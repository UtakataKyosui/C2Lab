# ui-test-coverage

UIコンポーネントの Props / State / イベントハンドラ / 条件分岐を静的解析し、最低限必要なテスト数（全組み合わせ直積）を計算してカバレッジギャップをJSON形式でレポートするClaude Codeプラグイン。

## 機能

- **静的解析**: `.tsx` / `.jsx` / `.vue` / `.svelte` コンポーネントを解析
- **計算式**: `Π(各propの値数) × Π(各stateの値数)` = 最低テスト数
- **FW自動検出**: `package.json` から Vitest / Jest / Playwright / Cypress を自動判定
- **ギャップ分析**: 必要テスト数 vs 実際のテスト数を比較してカバレッジ率を算出
- **JSON出力**: CI/CDパイプラインに組み込み可能なJSONレポート

## 前提条件

- Python 3.10 以上（標準ライブラリのみ使用、追加インストール不要）

## 使い方

Claude Code で以下のように話しかけると自動的にスキルが起動します:

```
UIのテストカバレッジを分析して
テスト数が足りているか確認して
最低限必要なテスト数を計算して
analyze UI test coverage
```

引数を指定して直接実行することもできます:

```
src/components ディレクトリのテストカバレッジを分析して coverage-report.json に出力して
```

## スクリプト直接実行

```bash
# カレントディレクトリのプロジェクトを解析
python scripts/ui_test_coverage.py .

# 特定ディレクトリを解析してファイルに保存
python scripts/ui_test_coverage.py /path/to/project --output report.json

# サマリーのみ出力
python scripts/ui_test_coverage.py . --summary-only

# 特定コンポーネントに絞る
python scripts/ui_test_coverage.py . --component "*/components/**/*.tsx"
```

## 出力例

```json
{
  "projectRoot": "/path/to/project",
  "frameworks": {
    "unit": ["vitest"],
    "e2e": ["playwright"]
  },
  "summary": {
    "components": { "total": 42, "analyzed": 42 },
    "minTests": {
      "total": 485,
      "topComplexComponents": [
        { "file": "src/components/Form.tsx", "name": "Form", "minTests": 72, "calculation": "mode(2) × emailValid(2) × passwordValid(2) × submitStatus(3) × role(3) = 72" }
      ]
    },
    "actualTests": { "unit": 120, "e2e": 15, "total": 135 },
    "gap": { "delta": -350, "coveragePercent": 27.8, "status": "insufficient" }
  }
}
```

## スキル

| スキル | トリガー | 説明 |
|---|---|---|
| `analyze` | 「テストカバレッジを分析して」等 | Python スクリプトを実行してレポートを生成・解釈 |
| `formula` | 「計算式を教えて」等 | 直積による最低テスト数の計算根拠を解説 |

## 計算式の根拠

UIコンポーネントは props と state の**組み合わせ**ごとに独立した振る舞いを持つため、完全な動作保証には全組み合わせのテストが必要です。

```
Button: variant(3) × disabled(2) × size(3) × isLoading(2) = 36テスト最低必要
Form:   mode(2) × emailValid(2) × passwordValid(2) × submitStatus(3) = 24テスト最低必要
```

詳細は `formula` スキルまたは `skills/formula/SKILL.md` を参照してください。
