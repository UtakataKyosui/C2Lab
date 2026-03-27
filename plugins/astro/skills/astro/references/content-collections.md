# Content Collections 詳細ガイド

## Content Layer API (Astro v5+)

Astro v5 から `content.config.ts` を `src/` 直下に配置する形式が標準になった（旧 `src/content/config.ts` は非推奨）。

```typescript
// src/content.config.ts
import { defineCollection, z } from 'astro:content';
import { glob, file } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    heroImage: z.string().optional(),
    tags: z.array(z.string()).optional(),
    draft: z.boolean().default(false),
  }),
});

const authors = defineCollection({
  loader: file('src/data/authors.json'),
  schema: z.object({
    id: z.string(),
    name: z.string(),
    bio: z.string(),
    avatar: z.string().optional(),
  }),
});

export const collections = { blog, authors };
```

## ローダー

### glob ローダー
```typescript
loader: glob({
  pattern: '**/*.md',           // micromatch パターン
  base: './src/content/blog',   // 検索ベースディレクトリ
  // generateId: ({ entry }) => entry.replace(/\.md$/, ''), // カスタム ID 生成
})
```
- MD / MDX / Markdoc / JSON / YAML に対応
- `id` は `base` からの相対パス（拡張子を除く）

### file ローダー
```typescript
// JSON 配列: [{ id: "...", name: "..." }, ...]
loader: file('src/data/tags.json')

// JSON オブジェクト: { "tag-a": { name: "..." }, ... }
// キーが id として使われる
loader: file('src/data/tags.json', {
  parser: (text) => JSON.parse(text)  // カスタムパーサーも可能
})
```

### カスタムローダー（外部 CMS・API 等）
```typescript
import type { Loader } from 'astro/loaders';

const cmsLoader: Loader = {
  name: 'cms-loader',
  async load({ store, meta, logger }) {
    const lastModified = meta.get('lastModified');

    // インクリメンタル更新: 変更がなければスキップ
    const response = await fetch(`https://api.example.com/posts?since=${lastModified}`);
    const { posts, updatedAt } = await response.json();

    for (const post of posts) {
      store.set({ id: post.slug, data: post });
    }
    meta.set('lastModified', updatedAt);
    logger.info(`Loaded ${posts.length} posts`);
  },
};
```

## Zod スキーマ詳細

### よく使うフィールド型
```typescript
z.object({
  title: z.string(),
  description: z.string().max(160),           // 最大文字数
  pubDate: z.coerce.date(),                   // 文字列 → Date 自動変換
  updatedDate: z.coerce.date().optional(),
  draft: z.boolean().default(false),
  tags: z.array(z.string()).default([]),
  category: z.enum(['tech', 'life', 'note']), // 列挙型
  readingTime: z.number().int().positive().optional(),
})
```

### 画像スキーマ（ビルド時最適化）
```typescript
import { z } from 'astro:content';
import { image } from 'astro:assets';

schema: z.object({
  // image() を使うと src/ 内の画像が自動的にビルド時最適化される
  heroImage: image().optional(),
  // 外部 URL の場合は z.string().url() を使う
  externalImage: z.string().url().optional(),
})
```

### コレクション間リファレンス
```typescript
import { reference } from 'astro:content';

schema: z.object({
  title: z.string(),
  author: reference('authors'),              // authors コレクションの ID を参照
  relatedPosts: z.array(reference('blog')).optional(),
})

// 使用時
const post = await getEntry('blog', slug);
const author = await getEntry(post.data.author); // 自動型推論
```

## コレクションのクエリ

### getCollection
```typescript
import { getCollection } from 'astro:content';

// 全エントリ取得
const allPosts = await getCollection('blog');

// フィルタリング（ドラフト除外）
const posts = await getCollection('blog', ({ data }) => !data.draft);

// 日付降順ソート
const sorted = posts.sort(
  (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
);

// 最新N件
const recent = sorted.slice(0, 5);
```

### getEntry
```typescript
import { getEntry } from 'astro:content';

// slug（id）で単一エントリ取得
const post = await getEntry('blog', 'my-post-slug');
if (!post) return Astro.redirect('/404');

// reference 型フィールドの解決
const author = await getEntry(post.data.author);
```

### render() でコンテンツ取得
```typescript
import { render } from 'astro:content';

const { Content, headings, remarkPluginFrontmatter } = await render(post);
// headings: { depth: number, slug: string, text: string }[]
// Content: Astro コンポーネントとして使用
```

```astro
<!-- テンプレートで使用 -->
<article>
  <Content />
</article>

<!-- カスタムコンポーネントのマッピング（MDX の場合） -->
<Content components={{ h2: MyHeading, a: MyLink }} />
```

## よくあるパターン

### ドラフト記事のフィルタリング
```typescript
// 本番環境ではドラフトを除外、開発環境では表示
const posts = await getCollection('blog', ({ data }) => {
  return import.meta.env.PROD ? !data.draft : true;
});
```

### タグ一覧の抽出
```typescript
const allPosts = await getCollection('blog', ({ data }) => !data.draft);

// 全タグを重複なしで抽出
const allTags = [...new Set(
  allPosts.flatMap((post) => post.data.tags ?? [])
)].sort();

// タグごとの記事数
const tagCounts = allPosts.reduce((acc, post) => {
  for (const tag of post.data.tags ?? []) {
    acc[tag] = (acc[tag] ?? 0) + 1;
  }
  return acc;
}, {} as Record<string, number>);
```

### ページネーション
```astro
---
export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  const sorted = posts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

  const PER_PAGE = 10;
  const totalPages = Math.ceil(sorted.length / PER_PAGE);

  return Array.from({ length: totalPages }, (_, i) => ({
    params: { page: String(i + 1) },
    props: {
      posts: sorted.slice(i * PER_PAGE, (i + 1) * PER_PAGE),
      currentPage: i + 1,
      totalPages,
    },
  }));
}
---
```

### 関連記事の取得（タグ一致）
```typescript
async function getRelatedPosts(currentPost: CollectionEntry<'blog'>, limit = 3) {
  const allPosts = await getCollection('blog', ({ data }) => !data.draft);
  const currentTags = new Set(currentPost.data.tags ?? []);

  return allPosts
    .filter((post) => post.id !== currentPost.id)
    .map((post) => ({
      post,
      score: (post.data.tags ?? []).filter((t) => currentTags.has(t)).length,
    }))
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(({ post }) => post);
}
```

## v4 → v5 マイグレーション

| v4 | v5 |
|---|---|
| `src/content/config.ts` | `src/content.config.ts` |
| `type: 'content'` | `loader: glob(...)` |
| `type: 'data'` | `loader: file(...)` または `loader: glob(...)` |
| `slug` フィールド | `id` フィールド（自動生成） |
| `entry.slug` | `entry.id` |
