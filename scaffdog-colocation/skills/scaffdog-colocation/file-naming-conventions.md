# ファイル命名規則

## ディレクトリ命名

### コンポーネントディレクトリ

**PascalCase** を使用する。

```
src/components/
├── Button/           # ✅ PascalCase
├── DataTable/        # ✅ PascalCase
├── UserProfile/      # ✅ PascalCase
├── button/           # ❌ camelCase
└── data-table/       # ❌ kebab-case
```

### フィーチャー / ページディレクトリ

**kebab-case** を使用する。

```
src/features/
├── user-auth/        # ✅ kebab-case
├── data-export/      # ✅ kebab-case
├── UserAuth/         # ❌ PascalCase
└── dataExport/       # ❌ camelCase

src/pages/
├── dashboard/        # ✅ kebab-case
├── user-settings/    # ✅ kebab-case
└── Dashboard/        # ❌ PascalCase
```

## ファイル命名

### コンポーネント関連ファイル

コンポーネント名を接頭辞として PascalCase で統一する。

| ファイル種別 | パターン | 例 |
|---|---|---|
| コンポーネント | `{Name}.{tsx,vue,svelte}` | `Button.tsx` |
| テスト | `{Name}.test.{ts,tsx}` | `Button.test.tsx` |
| スタイル (CSS Modules) | `{Name}.module.css` | `Button.module.css` |
| スタイル (vanilla-extract) | `{Name}.css.ts` | `Button.css.ts` |
| 型定義 | `{Name}.types.ts` | `Button.types.ts` |
| バレル | `index.ts` | `index.ts` |
| フック | `use{Name}.ts` | `useButton.ts` |
| ユーティリティ | `{Name}.utils.ts` | `Button.utils.ts` |
| 定数 | `{Name}.constants.ts` | `Button.constants.ts` |
| ストーリー | `{Name}.stories.tsx` | `Button.stories.tsx` |

### 特殊なファイル名

| ファイル | 命名規則 | 説明 |
|---|---|---|
| バレルファイル | `index.ts` | TypeScriptプロジェクトでは `index.ts` を推奨。JSXを含む場合は `index.tsx`、JavaScriptプロジェクトでは `index.js`/`index.jsx` も可 |
| フック | `use{Name}.ts` | React hooks 命名規則に従う |
| コンテキスト | `{Name}Context.tsx` | `{Name}Provider` もここに含む |
| HOC | `with{Name}.tsx` | Higher-Order Component |

## フレームワーク別の拡張子

### React

```
Button/
├── index.ts          # バレル（.ts）
├── Button.tsx        # JSX を含む → .tsx
├── Button.test.tsx   # JSX を含むテスト → .tsx
├── Button.types.ts   # 型のみ → .ts
└── Button.module.css # スタイル
```

### Vue

```
Button/
├── index.ts          # バレル
├── Button.vue        # SFC → .vue
├── Button.test.ts    # テスト → .ts
├── Button.types.ts   # 型定義
└── composables/
    └── useButton.ts  # Composition API
```

### Svelte

```
Button/
├── index.ts          # バレル
├── Button.svelte     # コンポーネント → .svelte
├── Button.test.ts    # テスト
├── Button.types.ts   # 型定義
└── Button.module.css # スタイル
```

### Node.js / TypeScript（非UI）

```
user-service/
├── index.ts                # バレル
├── user-service.ts         # メインロジック（kebab-case）
├── user-service.test.ts    # テスト
├── user-service.types.ts   # 型定義
├── user-service.utils.ts   # ユーティリティ
└── user-service.constants.ts
```

**注意**: 非UIモジュールでは **kebab-case** を使用する。

## scaffdog テンプレートでの命名制御

```markdown
---
name: "component"
root: "src/components"
output: "**/*"
questions:
  name: "Component name (PascalCase):"
---

# `{{ inputs.name | pascal }}/index.ts`

export { {{ inputs.name | pascal }} } from './{{ inputs.name | pascal }}';

# `{{ inputs.name | pascal }}/{{ inputs.name | pascal }}.tsx`

// PascalCase でコンポーネント名を生成

# `{{ inputs.name | pascal }}/{{ inputs.name | pascal }}.test.tsx`

// テストファイルも PascalCase
```

ユーザーが `button` と入力しても `Button/Button.tsx` が生成される。

## カスタマイズ可能な設定項目

scaffdog の questions を使って、プロジェクトごとに命名規則をカスタマイズできる。

```yaml
questions:
  namingStyle:
    message: "Directory naming style:"
    choices:
      - label: "PascalCase (React standard)"
        value: "pascal"
      - label: "kebab-case (Angular style)"
        value: "kebab"
```

テンプレート内での使用:

```
{{ if inputs.namingStyle == "pascal" }}
# `{{ inputs.name | pascal }}/index.ts`
{{ else }}
# `{{ inputs.name | kebab }}/index.ts`
{{ end }}
```
