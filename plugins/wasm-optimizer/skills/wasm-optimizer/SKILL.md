---
name: wasm-optimizer
description: JS/TSコードの重い処理パターンを検出し、WebAssembly (WASM) やその他の高速代替ライブラリへの最適化を提案する。「WASMで高速化」「パフォーマンス改善」「重い処理を最適化」「Canvas処理が遅い」「JSON.parseが遅い」「crypto-jsの代替」や、画像処理、暗号化、数値計算、圧縮、大量データ操作のパフォーマンス改善に関する質問時に使用する。
globs:
  - "**/*.js"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.mjs"
---

# WebAssembly Optimization Guide

JS/TS コードに含まれる重い処理パターンを検出し、WebAssembly ベースのライブラリへの置き換えを提案する。

## 重い処理パターンと WASM 代替ライブラリ

| パターン | 検出シグナル | WASM 代替 | 期待改善 |
|---|---|---|---|
| 画像処理 | Canvas, ImageData, getPixel ループ | `wasm-vips`, `@squoosh/lib` | 5-20x |
| 暗号化 | CryptoJS, crypto-js, 手動ハッシュ | `libsodium-wrappers` (WASM), `@noble/hashes` (純JS高速) | 3-10x |
| JSON 大量パース | ループ内 JSON.parse, 巨大 JSON | `simd_json_wasm` | 2-5x |
| 文字列距離計算 | Levenshtein, editDistance, diff | wasm-pack カスタム Rust ビルド | 10-50x |
| 行列演算 | 3重ループ (i,j,k), 行列積 | `@stdlib/stdlib` WASM, wasm-pack | 5-20x |
| 圧縮/展開 | pako, zlib, gzip 処理 | `fflate` (純JS高速), `brotli-wasm` (WASM) | 2-8x |
| XML パース | DOMParser ループ, xml2js | `fast-xml-parser` (WASM版) | 2-5x |
| 数値計算 | 大量 Math.*, ループ内演算 | wasm-pack Rust ビルド | 5-30x |

## パターン検出の判断基準

以下の条件に該当する場合、WASM 最適化の候補とする:

1. **ネストループ（深さ >= 2）** でデータ処理を行っている
2. **Canvas API** (`getImageData`, `putImageData`, ピクセル操作) を使用
3. **crypto-js** / **CryptoJS** を import している
4. **ループ内で `JSON.parse`** を呼び出している
5. **手動実装の文字列距離関数** (Levenshtein, Hamming, Jaro-Winkler)
6. **3重ループの行列演算** (`result[i][j] += a[i][k] * b[k][j]`)
7. **大量データの sort/filter/reduce** (1万件以上が見込まれる)

## 提案時の注意事項

- WASM は初回ロードのオーバーヘッドがあるため、**頻繁に呼ばれる処理** に限定して提案
- バンドルサイズへの影響を必ず言及
- **dynamic import** + **Web Worker** の組み合わせを推奨
- 既存のテストがある場合、移行後もテストがパスすることを確認するよう促す

## 詳細ドキュメント

- [wasm-library-catalog.md](./references/wasm-library-catalog.md) - カテゴリ別 WASM ライブラリ詳細カタログ
- [integration-patterns.md](./references/integration-patterns.md) - バンドラー設定、Worker、dynamic import パターン
