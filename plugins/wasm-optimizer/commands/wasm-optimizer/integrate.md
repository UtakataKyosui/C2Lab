---
description: 指定したWASMライブラリの統合ガイドを表示する。パッケージインストールからバンドラー設定、Worker設定までのステップバイステップガイド。
argument-hint: "<library-name>"
---

# wasm-optimizer: integrate

WASM ライブラリの統合ガイドを表示します。

## 引数

- `$ARGUMENTS`: 統合するライブラリ名（例: `@noble/hashes`, `wasm-vips`, `fflate`）

## 手順

### 1. ライブラリの確認

`$ARGUMENTS` で指定されたライブラリが WASM ライブラリカタログに含まれるか確認する。

対応ライブラリ:

| ライブラリ | カテゴリ |
|---|---|
| `wasm-vips` | 画像処理 |
| `@squoosh/lib` | 画像処理 |
| `libsodium-wrappers` | 暗号化 |
| `@noble/hashes` | ハッシュ |
| `simd_json_wasm` | JSON パース |
| `fast-xml-parser` | XML パース |
| `fflate` | 圧縮 |
| `brotli-wasm` | 圧縮 |
| `@stdlib/stdlib` | 数値計算 |

未対応のライブラリが指定された場合は、一般的な WASM 統合ガイドを表示する。

### 2. プロジェクト設定の確認

- `package.json` からパッケージマネージャーを検出（npm / yarn / pnpm / bun）
- バンドラーの種類を検出（Vite / Webpack / Rollup / Next.js）

### 3. 統合ガイドの表示

以下のステップバイステップガイドを表示する:

```markdown
## [ライブラリ名] 統合ガイド

### Step 1: パッケージインストール

\```bash
npm install [パッケージ名]
# or
pnpm add [パッケージ名]
\```

### Step 2: バンドラー設定

[検出されたバンドラーに応じた設定]

### Step 3: 基本的な使い方

\```ts
// import と初期化
\```

### Step 4: Web Worker 設定（推奨）

\```ts
// Worker ファイルの作成
\```

### Step 5: 既存コードの置き換え

\```ts
// Before (現在のコード)
// After (WASM ライブラリ使用)
\```

### Step 6: テスト

既存のテストが引き続きパスすることを確認してください:

\```bash
npm test
\```

### 注意事項

- バンドルサイズ影響: +XXX KB
- 初回ロード時間の増加に注意
- dynamic import で遅延読み込み推奨
```

### 4. 追加リソース

- ライブラリの公式ドキュメントへのリンク
- パフォーマンスベンチマークの実行方法
