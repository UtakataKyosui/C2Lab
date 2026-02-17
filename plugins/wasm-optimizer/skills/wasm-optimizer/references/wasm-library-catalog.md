# WASM ライブラリカタログ

カテゴリ別の WebAssembly ライブラリ詳細情報。各ライブラリの特徴、インストール方法、基本的な使い方を記載。

## 画像処理

### wasm-vips

- **npm**: `wasm-vips`
- **サイズ**: ~3MB (gzip)
- **用途**: 画像リサイズ、フォーマット変換、フィルタ適用
- **特徴**: libvips の WASM ビルド。サーバーサイド品質の画像処理をブラウザで実行可能

```js
import Vips from "wasm-vips";

const vips = await Vips();
const image = vips.Image.newFromBuffer(inputBuffer);
const resized = image.resize(0.5);
const output = resized.writeToBuffer(".webp");
```

### @squoosh/lib

- **npm**: `@squoosh/lib`
- **サイズ**: ~1.5MB (gzip, コーデック別)
- **用途**: 画像圧縮、フォーマット変換 (AVIF, WebP, JPEG XL)
- **特徴**: Google Chrome Labs 製。複数コーデックを WASM で提供

```js
import { ImagePool } from "@squoosh/lib";

const imagePool = new ImagePool();
const image = imagePool.ingestImage(inputBuffer);
await image.encode({ webp: { quality: 80 } });
```

## 暗号化・ハッシュ

### libsodium-wrappers

- **npm**: `libsodium-wrappers`
- **サイズ**: ~200KB (gzip)
- **用途**: 暗号化、復号、ハッシュ、署名
- **特徴**: libsodium の WASM ビルド。セキュリティ監査済み

```js
import _sodium from "libsodium-wrappers";

await _sodium.ready;
const sodium = _sodium;
const hash = sodium.crypto_generichash(32, message);
```

### @noble/hashes

- **npm**: `@noble/hashes`
- **サイズ**: ~50KB (gzip)
- **用途**: SHA-256, SHA-512, BLAKE2, RIPEMD160 等のハッシュ
- **特徴**: 純 JS 実装だが高度に最適化。WASM 不要で軽量。CryptoJS の直接置き換え

```js
import { sha256 } from "@noble/hashes/sha256";

const hash = sha256("message");
```

## データ変換

### simd_json_wasm

- **npm**: `simd_json_wasm`
- **サイズ**: ~150KB (gzip)
- **用途**: 高速 JSON パース
- **特徴**: SIMD 命令活用。大量 JSON の一括パースに最適

```js
import { parse } from "simd_json_wasm";

const data = parse(jsonString);
```

### fast-xml-parser

- **npm**: `fast-xml-parser`
- **サイズ**: ~30KB (gzip)
- **用途**: XML パース、XML ビルド
- **特徴**: 純 JS 実装だが高速。DOMParser より 10x 以上高速

```js
import { XMLParser } from "fast-xml-parser";

const parser = new XMLParser();
const result = parser.parse(xmlString);
```

## 圧縮

### fflate

- **npm**: `fflate`
- **サイズ**: ~29KB (gzip)
- **用途**: gzip, deflate, zlib 圧縮・展開
- **特徴**: pako の高速代替。WASM 不使用だが pako より 3-5x 高速

```js
import { gzipSync, gunzipSync } from "fflate";

const compressed = gzipSync(data);
const decompressed = gunzipSync(compressed);
```

### brotli-wasm

- **npm**: `brotli-wasm`
- **サイズ**: ~300KB (gzip)
- **用途**: Brotli 圧縮・展開
- **特徴**: Brotli の WASM ビルド。gzip より高い圧縮率

```js
import brotli from "brotli-wasm";

const instance = await brotli;
const compressed = instance.compress(data);
const decompressed = instance.decompress(compressed);
```

## 数値計算

### @stdlib/stdlib (WASM)

- **npm**: `@stdlib/stdlib` (個別パッケージ推奨)
- **サイズ**: パッケージ依存
- **用途**: 線形代数、統計、FFT、信号処理
- **特徴**: 科学計算ライブラリ。一部に WASM 最適化版あり

```js
import dgemm from "@stdlib/blas-base-dgemm";

// 行列積 C = alpha * A * B + beta * C
dgemm("row-major", "no-transpose", "no-transpose", m, n, k, 1.0, A, k, B, n, 0.0, C, n);
```

### wasm-pack カスタム Rust ビルド

- **ツール**: `wasm-pack`
- **用途**: カスタム数値計算、文字列処理、ドメイン特化ロジック
- **特徴**: Rust で実装し WASM にコンパイル。最高のパフォーマンス

```rust
// src/lib.rs
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn levenshtein(a: &str, b: &str) -> usize {
    // Rust 実装
}
```

```bash
wasm-pack build --target web
```
