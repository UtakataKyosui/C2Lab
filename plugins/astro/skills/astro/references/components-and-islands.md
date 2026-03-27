# コンポーネントと Island Architecture 詳細

## Astro コンポーネント詳細

### 特殊ディレクティブ
```astro
---
const htmlContent = '<strong>太字</strong>';
const color = 'rebeccapurple';
---

<!-- エスケープなしで HTML を挿入（XSS に注意） -->
<div set:html={htmlContent} />

<!-- フロントマター変数を CSS カスタムプロパティに渡す -->
<div class="box">テキスト</div>
<style define:vars={{ color }}>
  .box { color: var(--color); }
</style>

<!-- バンドルせずスクリプトをそのまま出力 -->
<script is:inline>
  console.log('バンドルされない');
</script>
```

### Props の型定義パターン
```astro
---
interface Props {
  title: string;
  variant?: 'primary' | 'secondary';
  class?: string;  // 外部からクラスを注入するパターン
}
const { title, variant = 'primary', class: className } = Astro.props;
---
<div class:list={['base-styles', variant, className]}>
  {title}
</div>
```

### Named Slots
```astro
<!-- layouts/main.astro -->
<header><slot name="header" /></header>
<main><slot /></main>  <!-- デフォルトスロット -->
<footer><slot name="footer">デフォルトフッター</slot></footer>

<!-- 使用側 -->
<Layout>
  <nav slot="header">ナビ</nav>
  <article>コンテンツ</article>
  <!-- footer スロットは未指定 → デフォルト値が使われる -->
</Layout>
```

### Astro.slots でスロットの有無を確認
```astro
---
const hasFooter = Astro.slots.has('footer');
---
{hasFooter && <footer><slot name="footer" /></footer>}
```

## フレームワークコンポーネント統合

### React (@astrojs/react)
```bash
bunx astro add react
# または
bun add @astrojs/react react react-dom
```

```js
// astro.config.mjs
import react from '@astrojs/react';
export default defineConfig({ integrations: [react()] });
```

```json
// tsconfig.json（React JSX のため）
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "react"
  }
}
```

### Vue (@astrojs/vue)
```bash
bunx astro add vue
```

```astro
<!-- Vue SFC コンポーネントをそのまま使用 -->
<MyVueComponent client:idle />
```

### Svelte (@astrojs/svelte)
```bash
bunx astro add svelte
```

Svelte コンポーネントはバンドルサイズが最小になるため、
パフォーマンスが最優先の場合に最適。

### 複数フレームワーク共存
```js
// astro.config.mjs
import react from '@astrojs/react';
import svelte from '@astrojs/svelte';
import vue from '@astrojs/vue';

export default defineConfig({
  integrations: [react(), svelte(), vue()],
});
```

**注意**: `.astro` ファイル内で JSX を書くには `jsxImportSource` の設定が必要。
複数フレームワークを使う場合、`.tsx` ファイルには React、`.svelte` ファイルには Svelte と
ファイル拡張子で自動判別される。

## ハイドレーション戦略の選び方

```
コンポーネントが必要か?
├── インタラクションなし → client:* なし（静的 HTML のみ）
└── インタラクションあり
    ├── ページ読み込み直後に必要 → client:load
    ├── 最初から必要だが緊急度低 → client:idle
    ├── スクロールしないと見えない → client:visible
    ├── 特定のデバイスのみ → client:media="(条件)"
    └── window/localStorage 依存 → client:only="react"
```

### パフォーマンスへの影響
- `client:load`: 最も重い。ページブロッキングになりうる
- `client:idle`: メインスレッドをブロックしない
- `client:visible`: 画面外の JS を遅延読み込み
- `client:only`: SSR なし → OGP/SEO に影響するコンポーネントに使わないこと

## React 統合の注意点

### useState/useEffect は必ず client:* が必要
```astro
<!-- NG: client:* なし → useState が機能しない -->
<Counter />

<!-- OK -->
<Counter client:load />
```

### Astro から React へ Props を渡す
```astro
---
const posts = await getCollection('blog');
---
<!-- プリミティブ型・オブジェクト・配列 OK、関数は要注意 -->
<SearchComponent
  client:load
  initialPosts={posts.map(p => ({ id: p.id, title: p.data.title }))}
  placeholder="検索..."
/>
```

### shadcn/ui コンポーネントの Astro での使用
```astro
---
// shadcn/ui の Button コンポーネント
import { Button } from '@/components/ui/button';
---

<!-- 純粋な表示のみなら client:* 不要 -->
<Button variant="outline" asChild>
  <a href="/contact">お問い合わせ</a>
</Button>

<!-- onClick 等のイベントが必要なら client:load -->
<Button client:load onClick={() => alert('click')}>
  クリック
</Button>
```

### @base-ui/react（shadcn/ui v4 のプリミティブ）
```tsx
// @base-ui/react はサーバーサイドレンダリング対応
// Dialog, Popover 等のコンポーネントは client:load または client:idle が必要
import * as Dialog from '@base-ui-components/react/dialog';
```

## Islands 間の状態共有

Islands は独立しているため、直接状態を共有できない。

```typescript
// src/lib/store.ts - nanostores（フレームワーク非依存）
import { atom, map } from 'nanostores';

export const cartCount = atom(0);
export const user = map<{ name: string; email: string }>();
```

```tsx
// React Island での使用
import { useStore } from '@nanostores/react';
import { cartCount } from '../lib/store';

export function CartIcon() {
  const count = useStore(cartCount);
  return <span>{count}</span>;
}
```

その他の方法:
- **URL パラメータ / クエリ文字列**: ページ間状態の共有
- **カスタムイベント**: `document.dispatchEvent(new CustomEvent('update', { detail }))`
- **localStorage / sessionStorage**: `client:only` コンポーネントで有効

## コンポーネント設計パターン

### Astro でラップ、React で中身
```astro
<!-- components/interactive-section.astro -->
---
import { ReactWidget } from './ReactWidget.tsx';
const { title, items } = Astro.props;
---
<!-- 静的シェルは Astro で -->
<section class="p-4 bg-white rounded-lg shadow">
  <h2>{title}</h2>
  <!-- インタラクティブ部分だけ React Island -->
  <ReactWidget client:visible items={items} />
</section>
```

### UI コンポーネントの配置方針
```
src/components/
├── MyAstroComp.astro       # 静的・レイアウト系
├── ui/                     # shadcn/ui 等（.tsx, client:* 必要なもの）
│   ├── button.tsx
│   └── dialog.tsx
└── interactive/            # 状態を持つインタラクティブコンポーネント
    ├── SearchBar.tsx
    └── ThemeToggle.tsx
```
