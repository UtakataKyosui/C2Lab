# WASM 統合パターン

WebAssembly ライブラリをプロジェクトに統合する際のバンドラー設定、Web Worker、dynamic import パターン。

## Dynamic Import パターン

WASM モジュールは初回ロードが重いため、dynamic import で遅延読み込みする。

```ts
// utils/image-processor.ts
export async function processImage(buffer: ArrayBuffer) {
  const { default: Vips } = await import("wasm-vips");
  const vips = await Vips();
  const image = vips.Image.newFromBuffer(new Uint8Array(buffer));
  return image.resize(0.5).writeToBuffer(".webp");
}
```

## Web Worker パターン

メインスレッドをブロックしないよう、WASM 処理は Worker で実行する。

### Worker ファイル

```ts
// workers/wasm-worker.ts
self.onmessage = async (e: MessageEvent) => {
  const { type, payload } = e.data;

  switch (type) {
    case "compress": {
      const { gzipSync } = await import("fflate");
      const result = gzipSync(new Uint8Array(payload));
      self.postMessage({ type: "result", payload: result.buffer }, [result.buffer]);
      break;
    }
    case "hash": {
      const sodium = (await import("libsodium-wrappers")).default;
      await sodium.ready;
      const hash = sodium.crypto_generichash(32, new Uint8Array(payload));
      self.postMessage({ type: "result", payload: hash.buffer }, [hash.buffer]);
      break;
    }
  }
};
```

### メインスレッドからの呼び出し

```ts
// utils/wasm-bridge.ts
export function createWasmWorker() {
  const worker = new Worker(new URL("../workers/wasm-worker.ts", import.meta.url), {
    type: "module",
  });

  return {
    execute<T>(type: string, payload: ArrayBuffer): Promise<T> {
      return new Promise((resolve, reject) => {
        worker.onmessage = (e) => resolve(e.data.payload as T);
        worker.onerror = reject;
        worker.postMessage({ type, payload }, [payload]);
      });
    },
    terminate() {
      worker.terminate();
    },
  };
}
```

## バンドラー設定

### Vite

```ts
// vite.config.ts
import { defineConfig } from "vite";
import wasm from "vite-plugin-wasm";
import topLevelAwait from "vite-plugin-top-level-await";

export default defineConfig({
  plugins: [wasm(), topLevelAwait()],
  optimizeDeps: {
    exclude: ["wasm-vips", "brotli-wasm"],
  },
});
```

### Webpack 5

```js
// webpack.config.js
module.exports = {
  experiments: {
    asyncWebAssembly: true,
  },
  module: {
    rules: [
      {
        test: /\.wasm$/,
        type: "webassembly/async",
      },
    ],
  },
};
```

### Rollup

```js
// rollup.config.js
import { wasm } from "@rollup/plugin-wasm";

export default {
  plugins: [
    wasm({
      maxFileSize: 0, // 全 .wasm を別ファイルとして出力
    }),
  ],
};
```

### Next.js

```js
// next.config.js
/** @type {import('next').NextConfig} */
module.exports = {
  webpack: (config) => {
    config.experiments = {
      ...config.experiments,
      asyncWebAssembly: true,
    };
    return config;
  },
};
```

## パフォーマンス測定パターン

WASM 移行の効果を測定するベンチマークテンプレート。

```ts
async function benchmark(name: string, fn: () => Promise<void> | void, iterations = 100) {
  const times: number[] = [];
  for (let i = 0; i < iterations; i++) {
    const start = performance.now();
    await fn();
    times.push(performance.now() - start);
  }
  const avg = times.reduce((a, b) => a + b, 0) / times.length;
  const p95 = times.sort((a, b) => a - b)[Math.floor(times.length * 0.95)];
  console.log(`${name}: avg=${avg.toFixed(2)}ms, p95=${p95.toFixed(2)}ms`);
}

// 使用例（import はループ外で事前に行う）
const { parse: simdParse } = await import("simd_json_wasm");

await benchmark("JS JSON.parse", () => JSON.parse(largeJsonString));
await benchmark("WASM simd_json", () => simdParse(largeJsonString));
```
