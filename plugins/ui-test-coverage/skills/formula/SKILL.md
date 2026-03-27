---
name: ui-test-coverage:formula
description: This skill should be used when the user asks "テストの最低数はどう計算するの？", "なぜこの計算式なの？", "組み合わせテストの根拠を教えて", "how is the minimum test count calculated?", "explain the test coverage formula", "what is the Cartesian product for testing?", "UIテストの掛け合わせを説明して". Explains the mathematical basis for calculating the minimum number of frontend unit and E2E tests based on UI component feature counts and their Cartesian product.
version: 0.1.0
---

# UIテスト最低数の計算式

## 基本原理

UIコンポーネントの因子を**正常系バリアント**と**異常系因子**に分類し、それぞれの直積から最低テスト数を算出する。

```
正常系テスト数    = Π(正常系バリアント因子の値数)
異常系パターン数  = Π(異常系因子の値数)
最低テスト数合計  = 正常系テスト数 × 異常系パターン数
```

> Π は「直積（Cartesian product）」。

---

## 正常系 / 異常系の分類ルール

| 因子の種類 | 分類 | 理由 |
|---|---|---|
| 必須 enum/union props（`variant`, `size`, `type` 等） | **正常系バリアント** | 全値が「有効な設定」であり、バリエーションテストの軸 |
| `boolean` 型 props/states | **異常系** | `true` が無効・ロード・エラー状態を表すことが多い |
| optional props（`?` / `\| undefined`） | **異常系** | 省略ケース自体がエッジケース |
| event handlers（`() => void` 等） | **異常系** | コールバックの失敗・エラーを含むエッジケース |
| React states（`useState` 等） | **異常系** | ランタイムで変化する一時的な状態 |
| Union に `'error'` `'loading'` `'disabled'` を含む | **異常系** | エラー状態を示すリテラルが含まれる |

---

## 計算例: Button コンポーネント

```
Props:
  variant: 'primary' | 'secondary' | 'danger'  → 3通り  【正常系バリアント: required enum】
  size: 'sm' | 'md' | 'lg'                      → 3通り  【正常系バリアント: required enum】
  disabled?: boolean                             → 2通り  【異常系: optional boolean】
  onClick: () => void                            → 2通り  【異常系: event handler】

States:
  isLoading: boolean                             → 2通り  【異常系: state】
```

**計算:**
```
正常系: variant(3) × size(3) = 9
異常系パターン: disabled(2) × onClick(2) × isLoading(2) = 8
合計: 9 × 8 = 72
  ├─ 純正常系テスト: 9 × 1 = 9
  └─ 異常系を含むテスト: 9 × 7 = 63
```

**内訳:**
- **9 純正常系テスト**: `disabled=false, loading=false, onClick=正常` で全バリアントを確認
- **9 disabledテスト**: disabled状態 × 全バリアント
- **9 loadingテスト**: loading状態 × 全バリアント
- **9 onClick失敗テスト**: コールバックエラー × 全バリアント
- **残り 27**: disabled/loading/onClick の複合エラーパターン × 全バリアント

---

## なぜ正常系と異常系を分けるのか

### 分けない場合の問題

`variant(3) × disabled(2) × size(3) × onClick(2) × isLoading(2) = 72` だけを示すと、
開発者が 72 個すべてを「正常系のバリアントテスト」として実装してしまう。

実際には:
- **正常系テスト**（9件）: 各バリアントが正しくレンダリングされるか
- **異常系テスト**（63件）: disabled・loading・コールバックエラー時の動作

の 2 種類が必要であり、用途が異なる。

---

## TypeScript型から値数への変換

| 型表現 | 値数 | 分類 |
|---|---|---|
| `boolean` | 2 | 異常系 |
| `'a' \| 'b' \| 'c'` | 3 | 正常系（全リテラルが有効値） |
| `string` | 2 | 正常系（有効値 / 空文字） |
| `number` | 2 | 正常系（正常値 / 境界値） |
| `T \| undefined` | count(T) + 1 | 異常系（optional） |
| `T \| null` | count(T) + 1 | 異常系（optional） |
| `T[]` | 2 | 正常系（空配列 / 非空配列） |
| `ReactNode` | 2 | 正常系（提供あり / なし） |
| `() => void` | 2 | 異常系（event handler） |
| 文字列リテラル `'x'` | 1 | — |

---

## 現実的な解釈

**直積は理論的最小値**であり、実際のプロジェクトでは:

- **優先度付け**: 高リスク・高頻度の組み合わせを優先（全 72 件を網羅する必要はない）
- **ペアワイズテスト**: 2因子間の全組み合わせに限定（直積より少ない）
- **リスクベース**: 重要な機能パスに絞る

`ui_test_coverage.py` が出力する数値は「理論的最小値」であり、実際のテスト追加目標の**下限参考値**として使う。
最低でも `normalTests` 件の純正常系テストと、主要な異常系パターンを網羅する必要がある。

---

## 参考リソース

- スクリプト本体: `${CLAUDE_PLUGIN_ROOT}/scripts/ui_test_coverage.py`
- 実際の分析実行: `ui-test-coverage:analyze` スキル
