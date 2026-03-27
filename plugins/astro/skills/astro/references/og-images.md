# OG 画像生成ガイド

## 概要

Astro での OG 画像生成の標準パターンは **Satori + Sharp** の組み合わせ:

1. **Satori** (Vercel製): React JSX / HTML → SVG に変換
2. **Sharp**: SVG → PNG に変換（1200x630px）

```bash
bun add satori sharp
# 日本語フォントが必要な場合
bun add @fontsource/noto-sans-jp
```

## ファイル構成

```
src/
├── lib/
│   └── og-image.tsx        # Satori テンプレート (React JSX)
└── pages/
    └── og/
        └── [slug].png.ts   # API エンドポイント（ビルド時生成）
```

## Satori テンプレート

```tsx
// src/lib/og-image.tsx
// ※ このファイルは React JSX だが、ブラウザでは実行されない（Satori 用）

interface OgImageProps {
  title: string;
  description?: string;
  tags?: string[];
  date?: Date;
  siteName?: string;
}

export function OgImageTemplate({
  title,
  description,
  tags = [],
  date,
  siteName = 'My Site',
}: OgImageProps) {
  const titleFontSize = title.length > 40 ? 48 : 60;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        width: '1200px',
        height: '630px',
        background: '#0f172a',
        padding: '60px',
        fontFamily: 'Noto Sans JP',
      }}
    >
      {/* サイト名 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ width: '4px', height: '28px', background: '#a78bfa' }} />
        <span style={{ color: '#a78bfa', fontSize: '24px' }}>{siteName}</span>
      </div>

      {/* タイトル */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
        <h1
          style={{
            color: '#f1f5f9',
            fontSize: `${titleFontSize}px`,
            lineHeight: 1.4,
            margin: 0,
          }}
        >
          {title}
        </h1>
      </div>

      {/* タグ・日付 */}
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        {tags.slice(0, 3).map((tag) => (
          <span
            key={tag}
            style={{
              background: '#1e293b',
              color: '#94a3b8',
              padding: '6px 16px',
              borderRadius: '9999px',
              fontSize: '20px',
            }}
          >
            #{tag}
          </span>
        ))}
        {date && (
          <span style={{ color: '#64748b', fontSize: '20px', marginLeft: 'auto' }}>
            {date.toLocaleDateString('ja-JP')}
          </span>
        )}
      </div>
    </div>
  );
}
```

## API エンドポイント

```typescript
// src/pages/og/[slug].png.ts
import satori from 'satori';
import sharp from 'sharp';
import { getCollection } from 'astro:content';
import { OgImageTemplate } from '../../lib/og-image';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

// フォントの読み込み（ビルド時に一度だけ実行される）
// 注意: Satori は WOFF2 非対応。WOFF を使うこと。
const fontPath = fileURLToPath(
  new URL(
    '../../node_modules/@fontsource/noto-sans-jp/files/noto-sans-jp-japanese-400-normal.woff',
    import.meta.url
  )
);
const fontData = readFileSync(fontPath);

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.map((post) => ({
    params: { slug: post.id },
    props: { post },
  }));
}

export async function GET({ props }: { props: { post: any } }) {
  const { post } = props;

  // React JSX → SVG
  const svg = await satori(
    OgImageTemplate({
      title: post.data.title,
      description: post.data.description,
      tags: post.data.tags,
      date: post.data.pubDate,
    }),
    {
      width: 1200,
      height: 630,
      fonts: [
        {
          name: 'Noto Sans JP',
          data: fontData,
          weight: 400,
          style: 'normal',
        },
      ],
    }
  );

  // SVG → PNG
  const png = await sharp(Buffer.from(svg)).png().toBuffer();

  return new Response(png, {
    headers: {
      'Content-Type': 'image/png',
      'Cache-Control': 'public, max-age=31536000, immutable',
    },
  });
}
```

## Satori の CSS 制約

Satori は **すべての CSS** に対応しているわけではない。

### 使えるもの
- `display: flex` (flexbox のみ、grid 非対応)
- インラインスタイル（camelCase プロパティ）
- 絶対値・パーセント・`em` 等の単位
- `border-radius`, `box-shadow`, `opacity`
- `overflow: hidden`

### 使えないもの / 注意点
- `display: grid` → flexbox で代替
- **`oklch()` カラー非対応** → `#hex` や `rgb()` を使うこと
- Tailwind ユーティリティクラス（実験的）→ インラインスタイルを使うこと
- `calc()` は限定的サポート
- CSS 変数 (`--var`) は非対応
- `background-image: url()` は限定的（base64 は可）

## フォント処理詳細

```typescript
// 日本語フォントの japanese + latin サブセット両方が必要
const japaneseFontPath = 'noto-sans-jp-japanese-400-normal.woff';
const latinFontPath = 'noto-sans-jp-latin-400-normal.woff';

const fonts = [
  { name: 'Noto Sans JP', data: readFileSync(japaneseFontPath), weight: 400 },
  { name: 'Noto Sans JP', data: readFileSync(latinFontPath), weight: 400 },
];

// 太字が必要な場合（weight: 700 も追加）
const boldFontPath = 'noto-sans-jp-japanese-700-normal.woff';
fonts.push({ name: 'Noto Sans JP', data: readFileSync(boldFontPath), weight: 700 });
```

**@fontsource パスの確認:**
```bash
ls node_modules/@fontsource/noto-sans-jp/files/*.woff
```

## トラブルシューティング

| 症状 | 原因 | 解決策 |
|------|------|-------|
| 日本語が □ (豆腐) になる | フォントが読み込まれていない | WOFF ファイルのパスを確認、japanese サブセットを含める |
| WOFF2 エラー | Satori が WOFF2 非対応 | `.woff2` → `.woff` ファイルに変更 |
| ビルドが極端に遅い | 全記事分の画像をビルドしている | フォントを関数外でキャッシュ、必要なら on-demand 生成に変更 |
| 色が意図と違う | oklch() 非対応 | hex/rgb に変換 |
| レイアウトが崩れる | grid 使用 | flexbox に書き換える |
| `sharp` のバイナリエラー | Node.js バイナリ不一致 | `bun add sharp` を再実行、または `sharp` バージョンを確認 |

## オンデマンド生成（SSR モード）

静的サイトではなく SSR/Hybrid モードで、動的に OG 画像を生成する場合:

```typescript
// src/pages/og/[slug].png.ts (SSR版)
export const prerender = false;  // hybrid モードで動的にする

export async function GET({ params }) {
  const post = await getEntry('blog', params.slug);
  if (!post) return new Response('Not found', { status: 404 });

  const svg = await satori(/* ... */);
  const png = await sharp(Buffer.from(svg)).png().toBuffer();

  return new Response(png, {
    headers: {
      'Content-Type': 'image/png',
      // オンデマンドの場合はキャッシュを短めに
      'Cache-Control': 'public, max-age=3600',
    },
  });
}
```
