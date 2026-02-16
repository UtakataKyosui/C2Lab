---
name: scaffdog-colocation
description: コロケーションパターンに基づくファイル分割とscaffdogテンプレート生成を支援する。コンポーネント・機能単位でファイルをグループ化し、一貫した構造を維持する。
globs:
  - ".scaffdog/**/*.md"
---

# Colocation Pattern + scaffdog Guide

## コロケーションとは

関連するファイルを同じディレクトリに配置するパターン。コンポーネントのソースコード、テスト、スタイル、型定義などを1つのディレクトリにまとめることで、見通しと保守性を向上させる。

## Quick Reference

| ファイル種別 | 命名パターン | 例 |
|---|---|---|
| メインファイル | `{Name}.{tsx,vue,svelte,ts}` | `Button.tsx` |
| テスト | `{Name}.test.{ts,tsx}` | `Button.test.tsx` |
| スタイル | `{Name}.module.css` or `{Name}.css.ts` | `Button.module.css` |
| 型定義 | `{Name}.types.ts` | `Button.types.ts` |
| バレル | `index.ts` | `index.ts` |
| フック | `use{Name}.ts` | `useButton.ts` |
| ユーティリティ | `{Name}.utils.ts` | `Button.utils.ts` |
| 定数 | `{Name}.constants.ts` | `Button.constants.ts` |
| ストーリー | `{Name}.stories.tsx` | `Button.stories.tsx` |

## 標準ディレクトリ構造

```
src/components/Button/
├── index.ts            # バレルエクスポート（公開API）
├── Button.tsx          # メインコンポーネント
├── Button.test.tsx     # テスト
├── Button.module.css   # スタイル
├── Button.types.ts     # 型定義
└── Button.stories.tsx  # Storybook（オプション）
```

## scaffdog テンプレート基本形

`.scaffdog/component.md` の最小構成:

```markdown
---
name: "component"
root: "src/components"
output: "**/*"
questions:
  name: "Component name (PascalCase):"
---

# `{{ inputs.name }}/index.ts`

\```ts
export { {{ inputs.name }} } from './{{ inputs.name }}';
export type { {{ inputs.name }}Props } from './{{ inputs.name }}.types';
\```

# `{{ inputs.name }}/{{ inputs.name }}.tsx`

\```tsx
import type { {{ inputs.name }}Props } from './{{ inputs.name }}.types';

export const {{ inputs.name }} = (props: {{ inputs.name }}Props) => {
  return <div>{{ inputs.name }}</div>;
};
\```
```

## 詳細ドキュメント

- [colocation-patterns.md](./colocation-patterns.md) - コアパターン、拡張パターン、アンチパターン
- [scaffdog-syntax.md](./scaffdog-syntax.md) - scaffdogテンプレート構文リファレンス
- [file-naming-conventions.md](./file-naming-conventions.md) - 命名規則詳説
- [framework-examples.md](./framework-examples.md) - React/Vue/Svelte/TS/Node.js テンプレート例
