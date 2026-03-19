---
name: yarn
description: Yarn (v1 Classic / v2+ Berry) の総合ガイド。パッケージ管理とワークスペース操作の概要を提供する。詳細はコマンドリファレンスを参照。
globs:
  - "**/yarn.lock"
---

# Yarn Guide

## 概要

`yarn` は Facebook が開発したパッケージマネージャーです。v1（Classic）と v2+（Berry）でアーキテクチャが大きく異なります。

詳細なコマンドリファレンスは **[commands.md](./commands.md)** を参照してください。

## v1 Classic vs v2+ Berry

| 点 | v1 (Classic) | v2+ (Berry) |
|---|---|---|
| インストール | `node_modules/` | Plug'n'Play（PnP）または `node_modules` |
| 設定ファイル | `.yarnrc` | `.yarnrc.yml` |
| プラグイン | なし | プラグイン拡張可能 |
| ゼロインストール | 非対応 | `.yarn/cache/` をコミット可能 |
| バージョン確認 | `yarn --version` | `yarn --version`（2.x 以上） |

## クイックリファレンス

```bash
# インストール
yarn                         # 依存関係をインストール
yarn add <package>           # パッケージを追加
yarn add -D <package>        # devDependencies に追加
yarn install --frozen-lockfile  # lockfile から厳密インストール（CI 推奨）

# スクリプト
yarn run <script>
yarn <script>                # run を省略可

# ワークスペース（v1）
yarn workspaces run <script>
yarn workspace <pkg> <command>

# ワークスペース（v2+）
yarn workspaces foreach run <script>
```

## 参考リソース

- [Yarn v1 documentation](https://classic.yarnpkg.com/)
- [Yarn Berry documentation](https://yarnpkg.com/)
