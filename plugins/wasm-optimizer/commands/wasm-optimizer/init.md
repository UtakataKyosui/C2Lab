---
description: プロジェクトのバンドラー・WASM設定状況を検出し、WASM最適化の準備状況を確認する。
---

# wasm-optimizer: init

プロジェクトの WASM 最適化準備状況を確認します。

## 手順

### 1. プロジェクト検出

以下のファイルを確認し、プロジェクトの種類を特定する:

- `package.json` → Node.js / フロントエンドプロジェクト
- `vite.config.ts` / `vite.config.js` → Vite
- `webpack.config.js` / `next.config.js` → Webpack 系
- `rollup.config.js` → Rollup
- `tsconfig.json` → TypeScript プロジェクト

### 2. 既存 WASM 設定の確認

以下の WASM 関連設定が既に存在するか確認する:

| チェック項目 | 確認方法 |
|---|---|
| WASM プラグイン | バンドラー設定内の `wasm` プラグイン |
| asyncWebAssembly | Webpack の `experiments.asyncWebAssembly` |
| vite-plugin-wasm | `package.json` の devDependencies |
| .wasm ファイル | プロジェクト内の `*.wasm` ファイル |
| wasm-pack 設定 | `Cargo.toml` + `wasm-pack` |

### 3. 依存関係の確認

`package.json` から WASM 最適化候補のライブラリを検出する:

| 現在のライブラリ | WASM 代替候補 |
|---|---|
| crypto-js | @noble/hashes, libsodium-wrappers |
| pako | fflate, brotli-wasm |
| xml2js | fast-xml-parser |
| jimp | wasm-vips, @squoosh/lib |

### 4. レポート出力

```
## WASM 最適化 初期診断

### プロジェクト情報
- フレームワーク: [Vite / Next.js / etc.]
- TypeScript: [Yes / No]
- バンドラー: [Vite / Webpack / Rollup]

### WASM 対応状況
- [x] or [ ] バンドラー WASM プラグイン設定済み
- [x] or [ ] Top-level await 対応
- [x] or [ ] Web Worker 設定あり

### 最適化候補ライブラリ
| 現在 | 推奨 WASM 代替 | 優先度 |
|---|---|---|
| crypto-js | @noble/hashes | High |

### 次のステップ
1. `/wasm-optimizer:scan` でプロジェクト全体をスキャン
2. `/wasm-optimizer:suggest [file]` で個別ファイルを分析
```
