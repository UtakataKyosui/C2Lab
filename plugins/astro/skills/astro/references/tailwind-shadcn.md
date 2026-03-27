# Tailwind CSS v4 + shadcn/ui v4 in Astro

## Tailwind CSS v4 のセットアップ

Tailwind v4 は **Vite プラグイン方式** が標準。旧 `@astrojs/tailwind` インテグレーションは使わない。

```bash
bun add tailwindcss @tailwindcss/vite
# Typography プラグイン（ブログ等で prose クラスを使う場合）
bun add @tailwindcss/typography
```

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  vite: {
    plugins: [tailwindcss()],
  },
});
```

```css
/* src/styles/global.css */
@import "tailwindcss";

/* プラグインの読み込み */
@plugin "@tailwindcss/typography";

/* カスタムテーマ（CSS 変数ベース） */
@theme inline {
  --color-primary: oklch(0.6 0.2 280);
  --color-background: oklch(0.98 0 0);
  --font-sans: 'Roboto Variable', sans-serif;
}
```

```astro
---
// layouts/main.astro でグローバル CSS をインポート
import '../styles/global.css';
---
```

### v4 の主な変更点

| v3 | v4 |
|---|---|
| `tailwind.config.ts` | `@theme inline {}` in CSS |
| `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| プラグイン: `plugins: [require('@tailwindcss/typography')]` | `@plugin "@tailwindcss/typography"` in CSS |
| `dark:` variant: JS 設定 | `@custom-variant dark (&:where(.dark, .dark *))` |
| `content` 配列でファイル指定 | 自動検出（設定不要） |

### カスタム Variant の定義
```css
/* ダークモードの設定 (class ベース) */
@custom-variant dark (&:where(.dark, .dark *));

/* ホバー時のグループ制御 */
@custom-variant group-hover (&:where(.group:hover *));
```

### oklch カラーの活用
```css
@theme inline {
  /* oklch(明度 彩度 色相) */
  --color-primary-50:  oklch(0.97 0.05 280);
  --color-primary-500: oklch(0.60 0.20 280);
  --color-primary-900: oklch(0.25 0.15 280);

  /* ダークモード対応の CSS 変数 */
  --color-bg: oklch(0.98 0 0);
  --color-text: oklch(0.15 0 0);
}

.dark {
  --color-bg: oklch(0.12 0 0);
  --color-text: oklch(0.95 0 0);
}
```

## shadcn/ui v4 のセットアップ

shadcn/ui v4 は **@base-ui/react** をプリミティブとして使用（旧 Radix UI ではない）。

```bash
# shadcn の CLI を使ってセットアップ
bunx shadcn init
```

```json
// components.json（Astro プロジェクト用の設定）
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "base-lyra",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/styles/global.css",
    "baseColor": "mist",
    "cssVariables": true
  },
  "iconLibrary": "hugeicons",
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

```bash
# コンポーネントの追加
bunx shadcn add button
bunx shadcn add dialog
bunx shadcn add input
```

### @base-ui/react の特徴
- Radix UI の後継にあたるプリミティブライブラリ
- アクセシビリティ対応の Headless コンポーネント
- SSR に対応している

## Astro での shadcn/ui コンポーネント使用

### インタラクションが不要なコンポーネント（client:* 不要）
```astro
---
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
---

<!-- 表示のみ → client:* 不要 -->
<Button variant="outline" asChild>
  <a href="/contact">お問い合わせ</a>
</Button>
<Badge variant="secondary">タグ</Badge>
```

### インタラクションが必要なコンポーネント（client:* 必要）
```astro
---
import { ThemeToggle } from '@/components/interactive/ThemeToggle';
import { SearchDialog } from '@/components/interactive/SearchDialog';
---

<!-- クリックやホバーで状態が変わるもの -->
<ThemeToggle client:load />
<SearchDialog client:idle />
```

### Dialog / Modal の実装例
```tsx
// src/components/interactive/SearchDialog.tsx
'use client';  // ← この行は Astro では不要（Next.js 用）
import * as Dialog from '@base-ui-components/react/dialog';
import { useState } from 'react';

export function SearchDialog() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger className="...">検索</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Backdrop className="..." />
        <Dialog.Popup className="...">
          <input value={query} onChange={(e) => setQuery(e.target.value)} />
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
```

```astro
<SearchDialog client:idle />
```

## cn() ユーティリティ

```typescript
// src/lib/utils.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

```tsx
// 使用例: 条件分岐を含むクラスの結合
<div className={cn(
  'base-class another-class',
  isActive && 'active-class',
  variant === 'primary' ? 'bg-primary text-white' : 'bg-secondary',
  className  // 外部から渡されたクラスは常に優先
)} />
```

## よくあるトラブル

| 症状 | 原因 | 解決策 |
|---|---|---|
| Tailwind クラスが効かない | CSS をインポートし忘れ | `import '../styles/global.css'` を追加 |
| shadcn コンポーネントが動かない | `client:*` がない | `client:load` または `client:idle` を追加 |
| ダークモードが効かない | dark variant の設定漏れ | `@custom-variant dark` を CSS に追加 |
| OG 画像で Tailwind クラスが効かない | Satori は Tailwind 非対応 | インラインスタイルに変換 |
