# フレームワーク比較ガイド

## Astro を選ぶべき場面

### 向いているユースケース
- **コンテンツ駆動サイト**: ブログ・技術ドキュメント・ポートフォリオ・ランディングページ
- **パフォーマンス最優先**: Core Web Vitals スコアが SEO や UX に直結するサイト
- **マルチフレームワーク**: React と Svelte を混在させたい等、特定フレームワークに縛られたくない
- **静的サイトジェネレーター置き換え**: Hugo / Jekyll / 11ty からの移行

### 向いていないユースケース
- **高度にインタラクティブな SPA**: リアルタイムコラボレーション・コードエディタ・複雑なダッシュボード
- **フレームワーク依存が強い**: すでに Next.js で大量の RSC を書いている、Nuxt エコシステムを使いたい
- **複雑なグローバル状態管理**: Redux / Zustand で管理された複雑な状態がある SaaS アプリ

## Astro vs Next.js

| 観点 | Astro | Next.js |
|---|---|---|
| **主な用途** | コンテンツ駆動サイト | フルスタック React アプリ |
| **デフォルト JS** | ゼロ | React ランタイム込み |
| **Island** | ネイティブ対応 | RSC で部分的に実現 |
| **マルチフレームワーク** | React + Vue + Svelte 同居可 | React のみ |
| **バンドルサイズ** | 最小（JSなしも可） | 常に React ランタイムが含まれる |
| **レンダリング** | SSG・SSR・Hybrid | SSR・SSG・ISR・RSC |
| **データフェッチ** | Content Collections / fetch | Server Components / fetch |
| **学習曲線** | 低い | 中〜高い（RSC の概念が複雑） |
| **エコシステム** | 成長中 | 巨大（最大） |
| **バッキング** | Cloudflare（2026〜）| Vercel |

**Astro を選ぶ**: パフォーマンスが最優先、コンテンツ中心、JS を最小化したい<br>
**Next.js を選ぶ**: React エコシステムへの深い依存、認証・DB・フルスタック機能が必要

## Astro vs Nuxt

| 観点 | Astro | Nuxt |
|---|---|---|
| **フレームワーク** | フレームワーク非依存 | Vue 専用 |
| **自動インポート** | なし（明示的 import） | コンポーネント自動インポート |
| **コンテンツ管理** | Content Collections | Nuxt Content |
| **バンドルサイズ** | 最小 | Vue ランタイム込み |
| **フルスタック** | 良好（SSR, API） | 優秀（Nitro エンジン） |
| **Vue 開発者** | 使えるが最適ではない | 最高の選択肢 |

**Astro を選ぶ**: Vue にこだわりがない、パフォーマンス最優先<br>
**Nuxt を選ぶ**: Vue チーム・Vue エコシステムを活用したい

## Astro vs SvelteKit

| 観点 | Astro | SvelteKit |
|---|---|---|
| **JS 出力** | ゼロ〜最小 | コンパイル後の最小 JS |
| **Island** | ネイティブ | なし（ページ全体がアプリ） |
| **フルスタック** | 良好 | 優秀（専用ルーティング・フォーム処理） |
| **コンテンツ** | Content Collections が強力 | MDsvex 等が必要 |
| **インタラクション** | 局所的な Island | Svelte stores でグローバル |
| **Svelte 開発者** | 使えるが最適ではない | 最高の選択肢 |

**Astro を選ぶ**: コンテンツ多め、静的サイト寄り<br>
**SvelteKit を選ぶ**: インタラクションが多め、Svelte エコシステム

## 特徴的な差異：Island Architecture の本質的優位性

```
Next.js / Nuxt / SvelteKit:
┌─────────────────────────────────┐
│     JavaScript Application      │ ← 全体が JS アプリ
│ ┌──────┐ ┌──────┐ ┌──────────┐ │
│ │ Btn  │ │ Nav  │ │ Content  │ │
└─────────────────────────────────┘

Astro Islands:
┌─────────────────────────────────┐
│         Static HTML              │ ← 大部分が静的 HTML
│ ┌──────┐         ┌────────────┐ │
│ │ 🏝  │ (静的)   │    🏝      │ │ ← 独立した JS Islands
│ │ Btn  │         │ SearchBar  │ │
└─────────────────────────────────┘
```

各 Island は **独立したバンドル** を持つため:
- 不要な Island の JS は読み込まれない
- Island A が React、Island B が Svelte でも衝突しない
- ページ全体の JS は使われる Island の合計のみ

## フレームワーク選定フローチャート

```
アプリの性質は?
├── コンテンツ中心（ブログ・ドキュメント・LP）
│   └── → Astro（第一選択）
│
├── 高度にインタラクティブ（SaaS・エディタ・ゲーム）
│   ├── React チーム → Next.js / Vite + React
│   ├── Vue チーム → Nuxt
│   └── Svelte を使いたい → SvelteKit
│
└── バランス型（ブログ + 管理画面等）
    ├── パフォーマンス優先 → Astro (hybrid モード)
    └── 開発速度優先 → Next.js または SvelteKit

チームのスキルは?
├── 特定フレームワーク経験あり → そのフレームワーク対応のものを選ぶ
└── 新規学習するなら → Astro（学習曲線が最も緩やか）
```

## 2026年の状況

- **Astro 6 リリース** (2026年3月): workerd ベース dev server、CSP サポート、Fonts API、Live Content Collections
- **Cloudflare 買収** (2026年1月): The Astro Technology Company が Cloudflare に買収。MIT ライセンスのオープンソースは継続、Cloudflare Workers との first-class 統合
- **Next.js**: React Server Components が主流になりつつある。Vercel との密接な関係
- **SvelteKit 2**: Runes API（Svelte 5）で状態管理が大幅改善
