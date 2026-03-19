---
name: bun
description: Bun の総合ガイド。JavaScript ランタイム・パッケージマネージャー・バンドラー・テストランナーの概要を提供する。詳細はコマンドリファレンスを参照。
globs:
  - "**/bun.lockb"
---

# Bun Guide

## 概要

`bun` は Zig で書かれた高速な JavaScript ランタイムです。Node.js 互換でありながら、パッケージマネージャー・バンドラー・テストランナーを一体化しています。

詳細なコマンドリファレンスは **[commands.md](./commands.md)** を参照してください。

## ランタイム + パッケージマネージャー一体型

| 機能 | Node.js エコシステム | Bun |
|---|---|---|
| ランタイム | `node` | `bun` |
| パッケージ管理 | `npm` / `pnpm` / `yarn` | `bun install` |
| バンドル | `webpack` / `vite` | `bun build` |
| テスト | `jest` / `vitest` | `bun test` |
| TypeScript 実行 | `ts-node` / `tsx` | `bun run` （ネイティブ対応） |

## クイックリファレンス

```bash
# ランタイム
bun run <file.ts>            # TypeScript/JavaScript を直接実行
bun run <script>             # package.json スクリプトを実行
bunx <package>               # パッケージを一時実行（npx 相当）

# パッケージ管理
bun install                  # 依存関係をインストール
bun add <package>            # パッケージを追加
bun add -d <package>         # devDependencies に追加
bun remove <package>         # パッケージを削除

# ビルド・テスト
bun build ./index.ts --outdir ./dist
bun test                     # テストを実行
```

## 参考リソース

- [Bun documentation](https://bun.sh/docs)
