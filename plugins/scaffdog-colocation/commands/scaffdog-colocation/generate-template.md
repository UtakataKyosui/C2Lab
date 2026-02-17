---
description: 指定されたファイルタイプと設定に基づいてscaffdogテンプレートファイルを生成する。
---

# scaffdog-colocation: generate-template

scaffdog テンプレートファイル（`.scaffdog/<template-name>.md`）を生成します。

## 手順

### 1. ユーザーへの質問

以下の情報をユーザーに確認する:

1. **テンプレート名**: テンプレートの識別名（例: `component`, `hook`, `page`）
2. **ルートディレクトリ**: 生成先のベースパス（例: `src/components`, `src/hooks`）
3. **含めるファイルタイプ**: 以下から複数選択
   - `component` - メインコンポーネントファイル
   - `test` - テストファイル
   - `styles` - スタイルファイル（CSS Modules / vanilla-extract / Tailwind）
   - `types` - 型定義ファイル
   - `barrel` - バレルファイル（index.ts）
   - `hooks` - フックファイル
   - `utils` - ユーティリティファイル
   - `constants` - 定数ファイル
   - `stories` - Storybook ストーリーファイル

### 2. フレームワーク検出

`package.json` からフレームワークを検出し、適切な拡張子とテンプレート構文を決定する。

### 3. scaffdog-template-generator エージェント呼び出し

`scaffdog-template-generator` エージェントを呼び出し、以下のパラメータを渡す:

- テンプレート名
- ルートディレクトリ
- 含めるファイルタイプ
- 検出されたフレームワーク

### 4. テンプレートファイル生成

`.scaffdog/<template-name>.md` ファイルを生成する。

テンプレートは以下の要件を満たすこと:

- 正しい scaffdog frontmatter（name, root, output, questions）
- 選択されたファイルタイプに対応するファイルマーカー
- 条件分岐によるオプショナルファイルの制御
- コロケーションパターンに準拠した命名規則

### 5. 確認

生成されたテンプレートの内容をユーザーに表示し、修正の要望があれば対応する。

## 例

```bash
# コマンド実行
/scaffdog-colocation:generate-template

# 対話
> テンプレート名: form-component
> ルートディレクトリ: src/components
> ファイルタイプ: component, test, types, barrel, styles

# 結果: .scaffdog/form-component.md が生成される
```
