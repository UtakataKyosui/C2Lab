# レンダリングモードとルーティング詳細

## レンダリングモード

### Static（SSG）— デフォルト
```js
// astro.config.mjs（output 指定なし、または output: 'static'）
export default defineConfig({ site: 'https://example.com' });
```

- 全ページがビルド時に HTML として生成される
- アダプター不要
- CDN で完全にキャッシュ可能
- **動的ルートは `getStaticPaths` が必須**
- 最適なユースケース: ブログ・ドキュメント・ポートフォリオ・マーケティングサイト

### Hybrid — 大部分 Static + 一部 SSR
```js
// astro.config.mjs
import node from '@astrojs/node';
export default defineConfig({
  output: 'hybrid',
  adapter: node({ mode: 'standalone' }),
});
```

```astro
---
// SSR にしたいページのみ以下を追加
export const prerender = false;
---
```

- デフォルトは static、`prerender = false` でページ単位に SSR にする
- 最適なユースケース: 大部分が静的だがログイン・ダッシュボード・フォーム等の動的ページが一部ある

### Server（SSR）— 全ページ動的
```js
import cloudflare from '@astrojs/cloudflare';
export default defineConfig({
  output: 'server',
  adapter: cloudflare(),  // または node, vercel, netlify
});
```

```astro
---
// 静的にしたいページだけ以下を追加
export const prerender = true;
---
```

- 全ページがリクエスト時にレンダリングされる
- 最適なユースケース: 認証・パーソナライズ・リアルタイムデータ・フォーム処理

### アダプター比較
| アダプター | コマンド | 用途 |
|---|---|---|
| Node.js | `bunx astro add node` | セルフホスト・Docker |
| Cloudflare | `bunx astro add cloudflare` | Cloudflare Workers/Pages |
| Vercel | `bunx astro add vercel` | Vercel Edge/Serverless |
| Netlify | `bunx astro add netlify` | Netlify Functions |

## ファイルベースルーティング

```
src/pages/
├── index.astro              → /
├── about.astro              → /about
├── blog/
│   ├── index.astro          → /blog
│   ├── [slug].astro         → /blog/:slug
│   └── [...slug].astro      → /blog/* (catch-all)
├── [lang]/
│   └── about.astro          → /:lang/about
└── api/
    └── search.ts            → /api/search
```

**ルート優先度**: 静的 > 動的 (`[param]`) > Rest (`[...param]`)

## 動的ルート

### getStaticPaths の基本
```astro
---
// src/pages/blog/[slug].astro
import { getCollection } from 'astro:content';
import type { GetStaticPaths } from 'astro';

export const getStaticPaths: GetStaticPaths = async () => {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.map((post) => ({
    params: { slug: post.id },
    props: { post },
  }));
};

const { post } = Astro.props;
const { Content } = await render(post);
---
```

### Rest パラメータ（多段階パス）
```astro
---
// src/pages/docs/[...slug].astro
// /docs/guide/getting-started → params.slug = 'guide/getting-started'
export async function getStaticPaths() {
  const docs = await getCollection('docs');
  return docs.map((doc) => ({
    params: { slug: doc.id },  // 'guide/getting-started'
    props: { doc },
  }));
}
---
```

### paginate() ヘルパー
```astro
---
export async function getStaticPaths({ paginate }) {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  const sorted = posts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
  return paginate(sorted, { pageSize: 10 });
}

const { page } = Astro.props;
// page.data: 現在ページの記事配列
// page.currentPage / page.lastPage: ページ番号
// page.url.prev / page.url.next: 前後のページ URL
---
```

## API エンドポイント

### GET エンドポイント
```typescript
// src/pages/api/posts.ts
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async ({ url }) => {
  const tag = url.searchParams.get('tag');
  const posts = await getCollection('blog', ({ data }) => {
    if (!data.draft && tag) return data.tags?.includes(tag) ?? false;
    return !data.draft;
  });

  return new Response(
    JSON.stringify(posts.map((p) => ({ id: p.id, title: p.data.title }))),
    { headers: { 'Content-Type': 'application/json' } }
  );
};
```

### POST エンドポイント（SSR/Hybrid のみ）
```typescript
export const POST: APIRoute = async ({ request, locals }) => {
  // 認証確認
  if (!locals.user) {
    return new Response('Unauthorized', { status: 401 });
  }

  const body = await request.json();
  // バリデーション
  if (!body.title || typeof body.title !== 'string') {
    return new Response('Invalid request', { status: 400 });
  }

  // 処理...
  return new Response(JSON.stringify({ success: true }), {
    status: 201,
    headers: { 'Content-Type': 'application/json' },
  });
};
```

### ファイル生成エンドポイント（Static モード）
```typescript
// src/pages/rss.xml.ts  → /rss.xml として生成
export const GET: APIRoute = async () => {
  return new Response('<rss>...</rss>', {
    headers: { 'Content-Type': 'application/xml' },
  });
};
```

## ミドルウェア

```typescript
// src/middleware.ts
import { defineMiddleware, sequence } from 'astro:middleware';

// 認証ミドルウェア
const auth = defineMiddleware(async (context, next) => {
  const token = context.cookies.get('session')?.value;
  context.locals.user = token ? await validateSession(token) : null;
  return next();
});

// ログミドルウェア
const logger = defineMiddleware(async (context, next) => {
  const start = Date.now();
  const response = await next();
  console.log(`${context.request.method} ${context.url.pathname} - ${Date.now() - start}ms`);
  return response;
});

// 複数のミドルウェアをチェーン
export const onRequest = sequence(logger, auth);
```

### locals の型定義
```typescript
// src/env.d.ts
/// <reference types="astro/client" />

declare namespace App {
  interface Locals {
    user: {
      id: string;
      name: string;
      email: string;
    } | null;
  }
}
```

### ミドルウェアでの認証ガード
```typescript
const authGuard = defineMiddleware(async (context, next) => {
  const protectedPaths = ['/dashboard', '/admin'];
  const isProtected = protectedPaths.some(
    (path) => context.url.pathname.startsWith(path)
  );

  if (isProtected && !context.locals.user) {
    return context.redirect('/login?next=' + context.url.pathname);
  }
  return next();
});
```

## リダイレクト

```js
// astro.config.mjs で静的リダイレクト
export default defineConfig({
  redirects: {
    '/old-path': '/new-path',
    '/blog/[slug]': '/posts/[slug]',       // 動的リダイレクト
    '/legacy': { status: 301, destination: '/new' },  // ステータスコード指定
  },
});
```

```astro
---
// SSR: Astro.redirect() でリダイレクト
if (!Astro.locals.user) {
  return Astro.redirect('/login', 302);
}
---
```

## Astro.request / Astro.url (SSR での利用)

```astro
---
// SSR のみ利用可能（Static では URL の動的取得不可）
const { pathname, searchParams } = Astro.url;
const userAgent = Astro.request.headers.get('user-agent');
const cookie = Astro.cookies.get('theme');
---
```
