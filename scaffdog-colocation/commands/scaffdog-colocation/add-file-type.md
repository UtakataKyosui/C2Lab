---
description: 既存のコンポーネントディレクトリに新しいファイルタイプ（stories, constants, hooks等）を追加する。
---

# scaffdog-colocation: add-file-type

既存のコロケーションディレクトリに、不足しているファイルタイプを追加します。

## 手順

### 1. 対象ディレクトリの指定

ユーザーに以下のいずれかの方法で対象を指定させる:

- **直接パス指定**: `src/components/Button` のように具体的なパスを指定
- **検索**: コンポーネント名で検索して候補を表示

### 2. 現在のファイル構成を確認

対象ディレクトリ内のファイル一覧を表示し、現在の構成を確認:

```
src/components/Button/
├── index.ts          ✓
├── Button.tsx        ✓
├── Button.types.ts   ✓
├── Button.test.tsx   ✓
├── Button.module.css ✓
├── Button.stories.tsx  (なし)
├── Button.constants.ts (なし)
├── Button.utils.ts     (なし)
└── useButton.ts        (なし)
```

### 3. 追加するファイルタイプの選択

不足しているファイルタイプから、追加したいものを選択させる:

- `stories` - Storybook ストーリー
- `constants` - 定数定義
- `utils` - ユーティリティ関数
- `hooks` - カスタムフック
- `test` - テストファイル
- `styles` - スタイルファイル
- `types` - 型定義ファイル

### 4. ファイル生成

選択されたファイルタイプに対応するファイルを、コロケーション命名規則に従って生成する。

既存ファイルからコンポーネント名や型情報を読み取り、生成内容に反映する。
例えば `Button.types.ts` の `ButtonProps` を stories ファイルで参照するなど。

### 5. バレルファイル更新

新しいファイルで公開APIが追加された場合、`index.ts` を更新して新しいエクスポートを追加する。

### 6. scaffdog テンプレート更新（オプション）

ユーザーに、対応する scaffdog テンプレートにも新しいファイルタイプを追加するか確認する。
追加する場合は、`.scaffdog/<template-name>.md` に新しいファイルマーカーと条件分岐を追加する。
