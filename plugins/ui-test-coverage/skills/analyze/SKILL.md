---
name: ui-test-coverage:analyze
description: This skill should be used when the user asks to "UIのテストカバレッジを分析して", "テスト数が足りているか確認して", "最低限必要なテスト数を計算して", "UIコンポーネントのテスト不足を調べて", "analyze UI test coverage", "check if tests are enough", "calculate minimum tests". Runs a Python static analysis script against the project, calculates the Cartesian product of UI component features, and reports the gap between required and actual test counts as JSON.
version: 0.1.0
argument-hint: "[project_dir] [--output report.json] [--summary-only]"
allowed-tools: Bash, Read, Glob
---

# UI Test Coverage Analyzer

## 概要

UIコンポーネントを静的解析して最低限必要なテスト数を計算し、既存テスト数と比較してギャップをJSONレポートとして出力するスキル。

**計算式**: `product(各propの値数) × product(各stateの値数)` = コンポーネントごとの最低テスト数

## 実行手順

### 1. スクリプトのパスを確認

```bash
SCRIPT="${CLAUDE_PLUGIN_ROOT}/scripts/ui_test_coverage.py"
```

### 2. 解析を実行

```bash
# 基本（カレントディレクトリ）
python "$SCRIPT" .

# プロジェクトディレクトリ指定
python "$SCRIPT" /path/to/project

# サマリーのみ（詳細コンポーネントリストを除く）
python "$SCRIPT" . --summary-only

# JSONファイルに保存
python "$SCRIPT" . --output coverage-report.json

# 特定コンポーネントのみ
python "$SCRIPT" . --component "*/components/**/*.tsx"
```

### 3. 結果の解釈

スクリプトが出力するJSONの構造:

```json
{
  "components": [
    {
      "file": "Button.tsx",
      "minTests": {
        "count": 72,
        "normalTests": 9,
        "errorTests": 63,
        "normalFactors": [
          { "name": "variant", "values": 3 },
          { "name": "size", "values": 3 }
        ],
        "errorFactors": [
          { "name": "disabled", "values": 2 },
          { "name": "onClick", "values": 2 },
          { "name": "isLoading", "values": 2 }
        ],
        "calculation": "正常系: variant(3) × size(3) = 9 | 異常系パターン: disabled(2) × onClick(2) × isLoading(2) = 8 | 合計: 9 × 8 = 72 (純正常系 9 + 異常系含む 63)"
      }
    }
  ],
  "summary": {
    "minTests": { "total": 485 },
    "actualTests": { "unit": 120, "e2e": 15, "total": 135 },
    "gap": { "delta": -350, "coveragePercent": 27.8, "status": "insufficient" }
  }
}
```

**正常系 vs 異常系の見方**:
- `normalTests`: 「全パラメーターが正常値」のパターン数 = 最低限の正常系テスト数
- `errorTests`: disabled・loading・エラー等の異常系パターンを含むテスト数
- `normalFactors`: required enum/union props（variant, size 等）= 正常系バリアント軸
- `errorFactors`: boolean props, optional, states, event handlers = 異常系の軸

### 4. ユーザーへの報告

JSONレポートを受け取ったら、以下の情報をサマリーとして伝える:

1. **テスト充足状況**: `gap.status` が `sufficient` / `insufficient`
2. **カバレッジ率**: `gap.coveragePercent` %
3. **最低必要テスト数の内訳**: 正常系 + 異常系（`normalTests` / `errorTests`）
4. **実際のテスト数**: `actualTests.total`
5. **不足の多いコンポーネント**: `topComplexComponents` の上位5件
6. **推奨アクション**:
   - まず `normalTests` 分の正常系テストを作成する
   - 次に `errorFactors` の各軸（disabled, loading, error等）を網羅する異常系テストを追加する

## 解析ロジック

### 対象ファイル

| 種別 | 拡張子 |
|---|---|
| コンポーネント | `.tsx` `.jsx` `.vue` `.svelte` |
| Unit テスト | `.test.tsx` `.test.ts` `.spec.tsx` `.spec.ts` 等 |
| E2E テスト | `e2e/` `cypress/` `playwright/` ディレクトリ内のテスト |

### スキップするディレクトリ

`node_modules`, `.git`, `dist`, `build`, `.next`, `.nuxt`, `coverage`, `out`

### Props の値数推定

| TypeScript型 | 推定値数 |
|---|---|
| `boolean` | 2 |
| `'a' \| 'b' \| 'c'` (Union) | 3 |
| `string` | 2 (正常値/空) |
| `number` | 2 (正常値/境界値) |
| `T \| undefined` | count_type_values(T) + 1 |
| `T[]` / `Array<T>` | 2 (空/非空) |
| `ReactNode` | 2 |

### 対象外 Props

`children`, `className`, `style`, `id`, `key`, `ref` は汎用的すぎるため除外。

## 制限事項

- **Vue Options API 非対応**: Vue の `props: { name: String }` 形式（Options API）は解析されない。Composition API の `defineProps()` のみ対応。Options API を使うコンポーネントは `minTests: 1` と報告される。
- **Storybook ファイル除外**: `*.stories.tsx` / `*.story.tsx` などはコンポーネントとして解析されない。
- **カスタムテストヘルパー**: `it()` / `test()` 以外のカスタムテスト関数を使っている場合、テスト数が過少評価される。

## トラブルシューティング

### Pythonが見つからない

```bash
python3 "$SCRIPT" .
```

### 解析結果が0の場合

- `node_modules` にコンポーネントが混入していないか確認
- 対象拡張子（.tsx/.vue/.svelte）のファイルが存在するか確認:
  ```bash
  find . -name "*.tsx" -not -path "*/node_modules/*" | head -20
  ```

### テスト数が実際より少ない

スクリプトは `it(` / `test(` / `describe(` のパターンでカウントするため、カスタムテストヘルパーを使っているプロジェクトでは過少評価になる場合がある。

## 参考

- 計算式の詳細: `formula` スキル（「テスト数の計算式を説明して」で起動）
- スクリプト本体: `${CLAUDE_PLUGIN_ROOT}/scripts/ui_test_coverage.py`
