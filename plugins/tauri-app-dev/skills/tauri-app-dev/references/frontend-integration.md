# Tauri v2 フロントエンドフレームワーク統合

## 設定の基本構造

Tauri はフレームワーク非依存。`tauri.conf.json` の `build` セクションで統合する。

```json
{
  "build": {
    "beforeDevCommand": "<フレームワークの開発サーバー起動コマンド>",
    "beforeBuildCommand": "<フレームワークのビルドコマンド>",
    "devUrl": "<開発サーバーの URL>",
    "frontendDist": "<ビルド出力ディレクトリ>"
  }
}
```

---

## React + Vite

### セットアップ

```bash
npm create tauri-app@latest -- --template react-ts
# または既存プロジェクトへの追加
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install
npm install --save-dev @tauri-apps/cli
npx tauri init
```

### tauri.conf.json

```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  }
}
```

### vite.config.ts（Tauri 向け設定）

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // Tauri の開発サーバーポートを固定
  server: {
    port: 5173,
    strictPort: true,
    // モバイル開発のためのホスト設定
    host: process.env.TAURI_DEV_HOST || 'localhost',
    hmr: process.env.TAURI_DEV_HOST
      ? {
          protocol: 'ws',
          host: process.env.TAURI_DEV_HOST,
          port: 5183,
        }
      : undefined,
    watch: {
      // Tauri が監視する必要のないファイルを除外
      ignored: ['**/src-tauri/**'],
    },
  },
  // Tauri v2 では clearScreen を使わない
  clearScreen: false,
  // 環境変数のビルドターゲット
  envPrefix: ['VITE_', 'TAURI_ENV_*'],
  build: {
    // Tauri のデフォルトブラウザサポートに合わせる
    target: process.env.TAURI_ENV_PLATFORM === 'windows' ? 'chrome105' : 'safari13',
    // デバッグビルドでソースマップを有効化
    sourcemap: !!process.env.TAURI_ENV_DEBUG,
    minify: !process.env.TAURI_ENV_DEBUG ? 'esbuild' : false,
  },
});
```

### Tauri API の使用例（React）

```tsx
import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';

function App() {
  const [greeting, setGreeting] = useState('');

  async function handleGreet() {
    const result = await invoke<string>('greet', { name: 'React' });
    setGreeting(result);
  }

  return (
    <div>
      <button onClick={handleGreet}>Greet</button>
      <p>{greeting}</p>
    </div>
  );
}

export default App;
```

---

## Vue 3 + Vite

### セットアップ

```bash
npm create tauri-app@latest -- --template vue-ts
```

### tauri.conf.json

```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  }
}
```

### vite.config.ts（Vue）

```typescript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    strictPort: true,
    host: process.env.TAURI_DEV_HOST || 'localhost',
  },
  clearScreen: false,
  envPrefix: ['VITE_', 'TAURI_ENV_*'],
  build: {
    target: 'chrome105',
    sourcemap: !!process.env.TAURI_ENV_DEBUG,
  },
});
```

### Tauri API の使用例（Vue 3 Composition API）

```vue
<script setup lang="ts">
import { ref } from 'vue';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { onMounted, onUnmounted } from 'vue';

const message = ref('');

async function sendCommand() {
  message.value = await invoke<string>('greet', { name: 'Vue' });
}

let unlisten: (() => void) | undefined;

onMounted(async () => {
  unlisten = await listen<string>('backend-event', (event) => {
    message.value = event.payload;
  });
});

onUnmounted(() => {
  unlisten?.();
});
</script>

<template>
  <button @click="sendCommand">Greet</button>
  <p>{{ message }}</p>
</template>
```

---

## Svelte + Vite

### セットアップ

```bash
npm create tauri-app@latest -- --template svelte-ts
```

### tauri.conf.json

```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  }
}
```

### Tauri API の使用例（Svelte）

```svelte
<script lang="ts">
  import { invoke } from '@tauri-apps/api/core';
  import { onMount, onDestroy } from 'svelte';
  import { listen, type UnlistenFn } from '@tauri-apps/api/event';

  let greeting = '';
  let unlisten: UnlistenFn;

  async function greet() {
    greeting = await invoke<string>('greet', { name: 'Svelte' });
  }

  onMount(async () => {
    unlisten = await listen<string>('my-event', (event) => {
      greeting = event.payload;
    });
  });

  onDestroy(() => {
    unlisten?.();
  });
</script>

<button on:click={greet}>Greet</button>
<p>{greeting}</p>
```

---

## Next.js（SSR 無効化が必要）

### 重要: Tauri は静的エクスポートが必要

```bash
# Next.js プロジェクト作成
npx create-next-app@latest my-app --typescript
cd my-app
npm install --save-dev @tauri-apps/cli
npx tauri init
```

### next.config.js（静的エクスポート設定）

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // 静的エクスポート必須
  images: {
    unoptimized: true,  // 画像最適化を無効化（Tauri では不要）
  },
  // 開発サーバーポート
  env: {
    NEXT_PUBLIC_TAURI: 'true',
  },
};

module.exports = nextConfig;
```

### tauri.conf.json

```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:3000",
    "frontendDist": "../out"
  }
}
```

**注意**: Next.js の SSR 機能（API Routes、Server Components など）は Tauri では使用不可。クライアントコンポーネントのみ使用できる。

---

## SvelteKit

```bash
npm create svelte@latest my-app
cd my-app
npm install --save-dev @tauri-apps/cli
npx tauri init
```

### svelte.config.js

```javascript
import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: 'index.html',
      precompress: false,
    }),
  },
};
```

### tauri.conf.json

```json
{
  "build": {
    "beforeDevCommand": "npm run dev -- --open",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:5173",
    "frontendDist": "../build"
  }
}
```

---

## Tauri API の型補完設定

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2021",
    "module": "ESNext",
    "lib": ["ES2021", "DOM", "DOM.Iterable"],
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true
  }
}
```

### @tauri-apps/api のインポート

```bash
npm install @tauri-apps/api
```

利用可能なモジュール:
- `@tauri-apps/api/core` → `invoke`, `Channel`, `convertFileSrc`
- `@tauri-apps/api/event` → `listen`, `once`, `emit`, `emitTo`
- `@tauri-apps/api/window` → `getCurrentWindow`, `WebviewWindow`
- `@tauri-apps/api/webviewWindow` → `WebviewWindow`
- `@tauri-apps/api/path` → `homeDir`, `appDataDir`, etc.
- `@tauri-apps/api/app` → `getName`, `getVersion`, etc.
- `@tauri-apps/api/menu` → `Menu`, `MenuItem`, etc.
- `@tauri-apps/api/tray` → `TrayIcon`
- `@tauri-apps/api/dpi` → `LogicalSize`, `PhysicalSize`, etc.

---

## 画像ファイルの表示（convertFileSrc）

Tauri のセキュリティポリシーにより、ローカルファイルは直接 `<img src>` で表示できない。

```typescript
import { convertFileSrc } from '@tauri-apps/api/core';

const imagePath = '/home/user/photo.jpg';
const assetUrl = convertFileSrc(imagePath);
// → asset://localhost/home/user/photo.jpg

document.querySelector<HTMLImageElement>('#image')!.src = assetUrl;
```

CSP にも `asset:` スキームを追加:
```json
{
  "app": {
    "security": {
      "csp": "default-src 'self'; img-src 'self' asset: https://asset.localhost"
    }
  }
}
```
