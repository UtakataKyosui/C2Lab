---
name: astro
description: >
  Astro フレームワークの総合ガイド。Island Architecture・ゼロ JS 哲学・Content Collections・
  SSG/SSR/Hybrid の設定・コンポーネント・ルーティング・SEO・OG画像生成・パフォーマンス最適化をカバーする。
  以下のいずれかに該当する場合は必ず使用すること:
  (1) Astro プロジェクトで作業するとき
  (2) astro.config.mjs/ts を作成・変更するとき
  (3) .astro ファイルを作成・編集するとき
  (4) Content Collections を設計・変更するとき
  (5) OG 画像を生成・修正するとき
  (6) Astro のルーティング・ミドルウェア・API エンドポイントを扱うとき
  (7) フレームワーク選定で Astro を検討するとき
  (8) View Transitions を追加・設定するとき。
  astro.config.mjs, *.astro, content.config.ts を含むプロジェクトで自動的にトリガーする。
globs:
  - "**/astro.config.*"
  - "**/*.astro"
  - "**/content.config.ts"
---

# Astro Framework Guide

## Astro とは

Astro は **Island Architecture** を採用したコンテンツ駆動型 Web フレームワーク。

- **Zero-JS-by-default**: デフォルトでクライアント側 JS をゼロにし、必要な箇所にのみ JavaScript を注入する
- **Islands**: ページの大半を静的 HTML として出力し、インタラクティブな「島」だけを選択的にハイドレーション
- **マルチフレームワーク**: React・Vue・Svelte・Solid を同一プロジェクトで共存可能
- **コンテンツ優先**: ブログ・ドキュメント・マーケティングサイトで圧倒的なパフォーマンス

## プロジェクト検出

作業開始前に以下を確認する:

```bash
# Astro バージョン
cat package.json | grep '"astro"'     # ^5.x → Content Layer API 使用

# レンダリングモード
grep 'output' astro.config.*         # なし/static/hybrid/server

# 使用インテグレーション
grep 'integrations' astro.config.*   # react, vue, svelte, tailwind 等
```

## ユースケース別 astro.config テンプレート

### 静的ブログ / ポートフォリオ（デフォルト）
```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://example.com',
  integrations: [react()],
  vite: { plugins: [tailwindcss()] },
});
```

### ドキュメントサイト（Starlight）
```js
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  integrations: [
    starlight({ title: 'My Docs', social: { github: 'https://github.com/...' } }),
  ],
});
```

### ハイブリッドアプリ（大部分 Static + 一部 SSR）
```js
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  output: 'hybrid',
  adapter: node({ mode: 'standalone' }),
});
// SSR にしたいページ: export const prerender = false;
```

### フル SSR アプリ
```js
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';        // または cloudflare / vercel / netlify

export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
// 静的にしたいページ: export const prerender = true;
```

## 標準ファイル構造

```
src/
├── pages/           → ファイルベースルーティング (.astro, .md, .ts)
│   ├── index.astro  → /
│   ├── blog/
│   │   ├── index.astro      → /blog
│   │   └── [slug].astro     → /blog/:slug
│   ├── api/
│   │   └── search.ts        → /api/search (API エンドポイント)
│   └── og/
│       └── [slug].png.ts    → /og/:slug.png (OG 画像)
├── layouts/         → ページ全体のラッパーコンポーネント
├── components/      → 再利用可能なコンポーネント
│   └── ui/          → shadcn/ui 等のUIライブラリ
├── content/         → Content Collections のソースファイル
│   └── blog/        → .md / .mdx ファイル
├── content.config.ts → コレクション定義 (Astro v5+)
├── lib/             → ユーティリティ・ヘルパー関数
├── styles/          → グローバル CSS
└── assets/          → 画像等（src/ 内に置くと自動最適化される）

public/              → 静的ファイル（処理なしでそのままコピー）
```

## Astro コンポーネント基本

```astro
---
// フロントマター: TypeScript が書ける、ビルド時に実行される
import Layout from '../layouts/main.astro';
import MyReactComponent from '../components/Counter.tsx';

interface Props {
  title: string;
  description?: string;
}

const { title, description = 'デフォルト説明' } = Astro.props;
const posts = await getCollection('blog');
---

<!-- テンプレート: HTML + 式展開 -->
<Layout title={title}>
  <h1>{title}</h1>

  <!-- 条件分岐 -->
  {description && <p>{description}</p>}

  <!-- ループ -->
  <ul>
    {posts.map((post) => (
      <li><a href={`/blog/${post.id}`}>{post.data.title}</a></li>
    ))}
  </ul>

  <!-- フレームワークコンポーネント (client directive 必須) -->
  <MyReactComponent client:visible />

  <!-- スロット -->
  <slot />
  <slot name="footer" />
</Layout>

<!-- スタイル: デフォルトでスコープ適用 -->
<style>
  h1 { color: var(--color-primary); }
</style>

<!-- グローバルスタイル -->
<style is:global>
  body { margin: 0; }
</style>
```

**特殊ディレクティブ:**
- `set:html={htmlString}` — エスケープなしで HTML を挿入
- `define:vars={{ color }}` — CSS カスタムプロパティをフロントマター変数から設定
- `is:inline` — スクリプト/スタイルをバンドルせずそのまま出力

## クライアントディレクティブ早見表

| ディレクティブ | タイミング | 使用場面 |
|---|---|---|
| `client:load` | 即座（ページ読み込み時） | ナビゲーション・フォーム等、最初から必要なもの |
| `client:idle` | ブラウザ idle 時 | 優先度低のウィジェット・チャット等 |
| `client:visible` | ビューポートに入った時 | Below-the-fold のカルーセル・チャート等 |
| `client:media="(max-width: 768px)"` | メディアクエリ一致時 | モバイルのみのハンバーガーメニュー等 |
| `client:only="react"` | クライアントのみ（SSR なし） | window / localStorage 依存コンポーネント |

**黄金律**: `client:load` は使いすぎない。`client:visible` や `client:idle` で代替できないか常に検討する。

## Content Collections クイックリファレンス

```typescript
// src/content.config.ts (Astro v5+ の配置場所)
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    tags: z.array(z.string()).optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
```

```typescript
// ページでの使い方
import { getCollection, getEntry, render } from 'astro:content';

// 全記事（ドラフト除外）
const posts = await getCollection('blog', ({ data }) => !data.draft);

// 日付順ソート
const sorted = posts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

// 単一記事
const post = await getEntry('blog', slug);

// Markdown レンダリング
const { Content, headings } = await render(post);
// → <Content /> コンポーネントとして使用
```

詳細は [references/content-collections.md](./references/content-collections.md) を参照。

## ルーティング基本

```
src/pages/index.astro          → /
src/pages/about.astro          → /about
src/pages/blog/[slug].astro    → /blog/:slug  (動的)
src/pages/blog/[...slug].astro → /blog/*      (catch-all)
src/pages/api/users.ts         → /api/users   (API エンドポイント)
```

**動的ルートでの getStaticPaths:**
```astro
---
export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.map((post) => ({
    params: { slug: post.id },
    props: { post },
  }));
}
const { post } = Astro.props;
---
```

**API エンドポイント:**
```typescript
// src/pages/api/search.ts
import type { APIRoute } from 'astro';

export const GET: APIRoute = async ({ url }) => {
  const query = url.searchParams.get('q') ?? '';
  return new Response(JSON.stringify({ results: [] }), {
    headers: { 'Content-Type': 'application/json' },
  });
};
```

詳細は [references/rendering-and-routing.md](./references/rendering-and-routing.md) を参照。

## View Transitions

```astro
---
// layouts/main.astro に追加するだけで全ページにSPA的トランジション
import { ViewTransitions } from 'astro:transitions';
---
<head>
  <ViewTransitions />
</head>
```

**主要ディレクティブ:**
- `transition:name="hero-image"` — ページ間で同名要素をアニメーション連結
- `transition:animate="slide"` — トランジションアニメーション指定 (`fade`/`slide`/`none`)
- `transition:persist` — ページ遷移後も状態を保持（音楽プレイヤー等）

## 詳細リファレンス

タスクに応じて以下のファイルを読み込むこと:

| タスク | 参照ファイル |
|--------|-------------|
| Content Collections の設計・カスタムローダー・Zod スキーマ詳細 | [references/content-collections.md](./references/content-collections.md) |
| React/Vue/Svelte 統合・ハイドレーション戦略・shadcn/ui | [references/components-and-islands.md](./references/components-and-islands.md) |
| OG 画像の生成・Satori テンプレート・日本語フォント設定 | [references/og-images.md](./references/og-images.md) |
| SEO メタタグ・JSON-LD・サイトマップ・canonical URL・RSS | [references/seo-metadata.md](./references/seo-metadata.md) |
| レンダリングモード切替・動的ルート・ミドルウェア・API 詳細 | [references/rendering-and-routing.md](./references/rendering-and-routing.md) |
| パフォーマンス最適化・画像・フォント・Core Web Vitals | [references/performance.md](./references/performance.md) |
| フレームワーク選定（vs Next.js / Nuxt / SvelteKit）| [references/framework-comparison.md](./references/framework-comparison.md) |
| Tailwind CSS v4 + shadcn/ui v4 の Astro 統合 | [references/tailwind-shadcn.md](./references/tailwind-shadcn.md) |

## 参考リソース

- [Astro 公式ドキュメント](https://docs.astro.build/)
- [Astro インテグレーション一覧](https://astro.build/integrations/)
- [Astro GitHub](https://github.com/withastro/astro)
