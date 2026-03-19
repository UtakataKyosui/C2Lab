---
name: pnpm
description: pnpm / pnpx の総合ガイド。高速・効率的なパッケージ管理とワークスペース操作の概要を提供する。詳細はコマンドリファレンスを参照。
globs:
  - "**/pnpm-lock.yaml"
  - "**/pnpm-workspace.yaml"
---

# pnpm / pnpx Guide

## 概要

`pnpm` は npm 互換の高速パッケージマネージャーです。ハードリンクによるディスク節約と厳格な依存関係解決が特徴です。`pnpx` は npx 相当の実行ランナーです。

詳細なコマンドリファレンスは **[commands.md](./commands.md)** を参照してください。

## npm との主な違い

| 点 | npm | pnpm |
|---|---|---|
| ディスク使用量 | 各プロジェクトにコピー | グローバルストアをハードリンク |
| node_modules 構造 | フラット（ホイスティング） | 厳格（phantom deps 防止） |
| ワークスペース | `workspaces` フィールド | `pnpm-workspace.yaml` |
| フィルタ実行 | 不可 | `--filter` で特定パッケージのみ |

## クイックリファレンス

```bash
# インストール
pnpm install                 # 依存関係をインストール
pnpm add <package>           # パッケージを追加
pnpm add -D <package>        # devDependencies に追加
pnpm install --frozen-lockfile  # lockfile から厳密インストール（CI 推奨）

# スクリプト
pnpm run <script>
pnpm <script>                # run を省略可

# ワークスペース
pnpm --filter <pkg> run <script>   # 特定パッケージのみ実行
pnpm -r run <script>               # 全パッケージで実行
```

## 参考リソース

- [pnpm documentation](https://pnpm.io/)
