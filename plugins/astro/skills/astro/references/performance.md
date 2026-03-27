# パフォーマンス最適化

## Astro のデフォルト優位性

Astro は **Zero-JS-by-default** により、追加設定なしで他フレームワークを大きく上回るパフォーマンスを発揮する。

- 静的 Astro サイトの Core Web Vitals 「Good」達成率: **60%**（WordPress: 38%, Gatsby: 46%）
- 典型的な初回ページロード: **500ms 未満**

## ハイドレーション監査

### チェックリスト
- [ ] `client:load` を使っているコンポーネントをリストアップ
- [ ] それぞれ `client:idle` や `client:visible` で代替できないか検討
- [ ] `client:only` は本当に SSR が不可能なコンポーネントに限定
- [ ] 日付ライブラリ（date-fns 等）を `client:load` コンポーネント内で import していないか

### 重いライブラリの影響例
```
react: ~45KB gzip
@radix-ui/react-dialog: ~12KB gzip
date-fns (全import): ~50KB gzip → tree-shaking で最小化必須
```

### 軽量化のパターン
```astro
<!-- Before: 重いコンポーネントを即時ロード -->
<DatePicker client:load />

<!-- After: スクロールしたら読み込む -->
<DatePicker client:visible />
```

## 画像最適化

### Astro の <Image /> コンポーネント
```astro
---
import { Image, Picture } from 'astro:assets';
import heroImg from '../assets/hero.jpg';
---

<!-- 自動で WebP/AVIF 変換・適切なサイズに最適化 -->
<Image
  src={heroImg}
  alt="ヒーロー画像"
  width={800}
  height={400}
  format="webp"
  quality={80}
  loading="lazy"    <!-- デフォルト -->
/>

<!-- レスポンシブ画像 (srcset 自動生成) -->
<Picture
  src={heroImg}
  alt="レスポンシブ画像"
  widths={[400, 800, 1200]}
  sizes="(max-width: 800px) 100vw, 800px"
  formats={['avif', 'webp']}
/>
```

### src/ vs public/ の使い分け
| 配置場所 | 処理 | 使用例 |
|---|---|---|
| `src/assets/` | ビルド時に最適化・ハッシュ付き URL | ページ内の画像 |
| `public/` | そのままコピー・処理なし | favicon, robots.txt, OG画像の参照先 |

### リモート画像の許可
```js
// astro.config.mjs
export default defineConfig({
  image: {
    domains: ['images.example.com'],
    remotePatterns: [{ hostname: '*.unsplash.com' }],
  },
});
```

## フォント最適化

### @fontsource でセルフホスティング
```bash
# 可変フォント（ファイルサイズ最小）
bun add @fontsource-variable/roboto

# 固定ウェイト
bun add @fontsource/noto-sans-jp
```

```astro
---
// layouts/main.astro
// 必要なサブセットとウェイトのみインポート
import '@fontsource-variable/roboto/latin.css';
import '@fontsource/noto-sans-jp/japanese-400.css';
import '@fontsource/noto-sans-jp/japanese-700.css';
---
```

### CSS での font-display 設定
```css
/* src/styles/global.css */
@font-face {
  font-family: 'Roboto Variable';
  font-display: swap;     /* 代替フォントで先に表示 → CLS に注意 */
  /* または: optional → フォントが遅い場合は使わない → CLS なし */
}
```

### 日本語フォントのサブセット化
日本語フォントはファイルサイズが大きいため（Noto Sans JP 全体: ~5MB）、
サブセットを活用する:
- `japanese` サブセット: ひらがな・カタカナ・常用漢字
- `latin` サブセット: 英数字・記号

## CSS 最適化

### Tailwind CSS v4 のビルド最適化
```js
// astro.config.mjs (Vite プラグイン方式 - v4 標準)
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  vite: {
    plugins: [tailwindcss()],
  },
});
// 旧: @astrojs/tailwind インテグレーション（非推奨）
```

### スコープドスタイルの活用
```astro
<style>
  /* このスタイルはこのコンポーネント内にのみ適用される */
  /* バンドル時に自動的にスコープ用クラスが付与される */
  h1 { font-size: 2rem; }
</style>
```

## ビルド最適化

### prefetch の活用
```js
// astro.config.mjs
export default defineConfig({
  prefetch: {
    prefetchAll: true,          // 全リンクをプリフェッチ
    defaultStrategy: 'viewport', // 'hover' | 'tap' | 'viewport' | 'load'
  },
});
```

```astro
<!-- ページ単位でプリフェッチ指定 -->
<a href="/heavy-page" data-astro-prefetch="viewport">重いページ</a>
<a href="/fast-page" data-astro-prefetch="hover">速いページ</a>
```

### バンドル分析
```bash
bun run build -- --mode=production
# または
bunx rollup-plugin-visualizer を追加してバンドルサイズを可視化
```

## Core Web Vitals 対策

### LCP（最大コンテンツの描画）
- ヒーロー画像に `loading="eager"` と `fetchpriority="high"` を設定
- 画像を `src/assets/` に置いて自動最適化
- フォントの `font-display: swap` または `optional`
- ファーストビューで使う CSS をインライン化（Astro は自動でやってくれる）

### INP（インタラクションから次の描画まで）
- `client:load` コンポーネントを最小化
- 重い処理は Web Worker に移動
- `client:idle` で不要な JS 遅延読み込み

### CLS（累積レイアウトシフト）
```astro
<!-- 必ず width と height を指定（アスペクト比の確保） -->
<Image src={img} alt="..." width={800} height={400} />

<!-- テキストの CLS を防ぐ -->
<style>
  /* font-display: swap の場合、フォント切り替え時にシフトが起きる */
  /* フォールバックフォントのサイズを合わせる size-adjust で改善 */
  @font-face {
    font-family: 'Roboto Fallback';
    src: local('Arial');
    size-adjust: 99%;
    ascent-override: 90%;
  }
</style>
```

## キャッシュ戦略

```typescript
// SSR の API エンドポイントでキャッシュヘッダーを設定
export const GET: APIRoute = async () => {
  const data = await fetchExpensiveData();
  return new Response(JSON.stringify(data), {
    headers: {
      'Content-Type': 'application/json',
      // 1時間キャッシュ、その後 stale-while-revalidate
      'Cache-Control': 'public, max-age=3600, stale-while-revalidate=86400',
    },
  });
};
```

静的サイトは CDN で自動的にキャッシュされる（対応ホスティング: Cloudflare, Vercel, Netlify 等）。
