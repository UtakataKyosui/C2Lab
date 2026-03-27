# SEO・メタデータガイド

## SEO コンポーネント設計

### seo-head.astro パターン

```astro
---
// src/components/seo-head.astro
interface Props {
  title: string;
  description: string;
  pubDate?: Date;
  updatedDate?: Date;
  heroImage?: string;
  ogImageSlug?: string;   // OG画像生成エンドポイントのslug
  canonicalURL?: URL;
  type?: 'website' | 'article';
}

const {
  title,
  description,
  pubDate,
  updatedDate,
  heroImage,
  ogImageSlug,
  canonicalURL = new URL(Astro.url.pathname, Astro.site),
  type = 'website',
} = Astro.props;

// OG 画像 URL の解決
const ogImage = ogImageSlug
  ? new URL(`/og/${ogImageSlug}.png`, Astro.site)
  : heroImage
    ? new URL(heroImage, Astro.site)
    : new URL('/og/default.png', Astro.site);  // デフォルト OG 画像

const fullTitle = title === 'My Site' ? title : `${title} | My Site`;
---

<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width" />
<title>{fullTitle}</title>
<meta name="description" content={description} />
<link rel="canonical" href={canonicalURL} />

<!-- Open Graph -->
<meta property="og:type" content={type} />
<meta property="og:url" content={canonicalURL} />
<meta property="og:title" content={fullTitle} />
<meta property="og:description" content={description} />
<meta property="og:image" content={ogImage} />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:locale" content="ja_JP" />
<meta property="og:site_name" content="My Site" />

<!-- Twitter Cards -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content={fullTitle} />
<meta name="twitter:description" content={description} />
<meta name="twitter:image" content={ogImage} />

<!-- 記事の場合のみ -->
{type === 'article' && pubDate && (
  <meta property="article:published_time" content={pubDate.toISOString()} />
)}
{type === 'article' && updatedDate && (
  <meta property="article:modified_time" content={updatedDate.toISOString()} />
)}
```

### レイアウトでの使用
```astro
---
// layouts/main.astro
import SeoHead from '../components/seo-head.astro';
---
<html lang="ja">
  <head>
    <SeoHead {...Astro.props} />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <!-- RSS フィードの自動検出 -->
    <link rel="alternate" type="application/rss+xml" title="RSS" href="/rss.xml" />
  </head>
  <body>
    <slot />
  </body>
</html>
```

## JSON-LD 構造化データ

構造化データは Google の rich results（リッチリザルト）に影響する。

### Article スキーマ
```astro
---
const jsonLd = JSON.stringify({
  '@context': 'https://schema.org',
  '@type': 'Article',
  headline: title,
  description: description,
  datePublished: pubDate?.toISOString(),
  dateModified: (updatedDate ?? pubDate)?.toISOString(),
  author: {
    '@type': 'Person',
    name: 'Author Name',
    url: Astro.site?.toString(),
  },
  publisher: {
    '@type': 'Organization',
    name: 'Site Name',
    logo: {
      '@type': 'ImageObject',
      url: new URL('/logo.png', Astro.site).toString(),
    },
  },
  image: ogImage.toString(),
  url: canonicalURL.toString(),
});
---
<script type="application/ld+json" set:html={jsonLd} />
```

### BreadcrumbList スキーマ
```astro
---
const breadcrumbs = [
  { name: 'ホーム', url: Astro.site?.toString() },
  { name: 'ブログ', url: new URL('/blog', Astro.site).toString() },
  { name: title, url: canonicalURL.toString() },
];

const breadcrumbJsonLd = JSON.stringify({
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: breadcrumbs.map((item, index) => ({
    '@type': 'ListItem',
    position: index + 1,
    name: item.name,
    item: item.url,
  })),
});
---
<script type="application/ld+json" set:html={breadcrumbJsonLd} />
```

## サイトマップ

```bash
bunx astro add sitemap
```

```js
// astro.config.mjs
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://example.com',  // 必須
  integrations: [
    sitemap({
      // ドラフト記事を除外したい場合
      filter: (page) => !page.includes('/draft/'),
      // 最終更新日を設定
      serialize(item) {
        if (item.url.includes('/blog/')) {
          return { ...item, changefreq: 'weekly', priority: 0.8 };
        }
        return item;
      },
    }),
  ],
});
// ビルド後に /sitemap-index.xml と /sitemap-0.xml が生成される
```

## RSS フィード

```typescript
// src/pages/rss.xml.ts
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIRoute } from 'astro';

export const GET: APIRoute = async (context) => {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  const sorted = posts.sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );

  return rss({
    title: 'My Blog',
    description: 'ブログの説明',
    site: context.site!,
    items: sorted.map((post) => ({
      title: post.data.title,
      pubDate: post.data.pubDate,
      description: post.data.description,
      link: `/blog/${post.id}/`,
      // カスタムフィールド
      customData: post.data.tags?.length
        ? `<category>${post.data.tags[0]}</category>`
        : '',
    })),
    // RSS フィードの自動検出用
    customData: '<language>ja</language>',
    stylesheet: '/rss/styles.xsl',  // オプション: RSS スタイルシート
  });
};
```

## Canonical URL パターン

```astro
---
// 末尾スラッシュの統一（astro.config で trailingSlash 設定と合わせる）
const canonical = new URL(
  Astro.url.pathname.endsWith('/')
    ? Astro.url.pathname
    : `${Astro.url.pathname}/`,
  Astro.site
);
---
<link rel="canonical" href={canonical} />
```

```js
// astro.config.mjs で末尾スラッシュを統一
export default defineConfig({
  trailingSlash: 'always',  // 'always' | 'never' | 'ignore'
});
```

### ページネーションでの canonical
```astro
---
// /blog/page/1 は /blog/ に canonical
const isFirstPage = currentPage === 1;
const canonical = isFirstPage
  ? new URL('/blog/', Astro.site)
  : new URL(Astro.url.pathname, Astro.site);
---
<link rel="canonical" href={canonical} />

<!-- 前後のページリンク -->
{currentPage > 1 && (
  <link rel="prev" href={new URL(`/blog/page/${currentPage - 1}/`, Astro.site)} />
)}
{currentPage < totalPages && (
  <link rel="next" href={new URL(`/blog/page/${currentPage + 1}/`, Astro.site)} />
)}
```

## SEO チェックリスト

- [ ] `Astro.site` が `astro.config.mjs` に設定されている
- [ ] 全ページに `title` と `description` が設定されている（description は 160 文字以内）
- [ ] OG 画像が 1200x630px で設定されている
- [ ] canonical URL が設定されている
- [ ] `@astrojs/sitemap` が導入されている
- [ ] RSS フィードが `/rss.xml` で公開されている
- [ ] 構造化データ（JSON-LD）が記事ページに設定されている
- [ ] `lang` 属性が `<html>` に設定されている（日本語なら `ja`）
