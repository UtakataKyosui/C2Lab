---
name: npm
description: npm / npx の総合ガイド。パッケージのインストール・スクリプト実行・公開の概要を提供する。詳細はコマンドリファレンスを参照。
globs:
  - "**/package.json"
  - "**/package-lock.json"
---

# npm / npx Guide

## 概要

`npm` は Node.js の標準パッケージマネージャーです。`npx` はパッケージをインストールせずに直接実行するランナーです。

詳細なコマンドリファレンスは **[commands.md](./commands.md)** を参照してください。

## クイックリファレンス

```bash
# インストール
npm install                  # package.json の依存関係をインストール
npm install <package>        # パッケージを追加（dependencies）
npm install -D <package>     # パッケージを追加（devDependencies）
npm ci                       # lockfile から厳密インストール（CI 推奨）

# スクリプト
npm run <script>             # scripts フィールドのコマンドを実行
npm test                     # npm run test の省略形
npm start                    # npm run start の省略形

# パッケージ管理
npm update                   # パッケージを更新
npm uninstall <package>      # パッケージを削除
npm list                     # インストール済みパッケージ一覧
npm outdated                 # 更新可能なパッケージを表示

# npx
npx <package>                # パッケージを一時的に実行
npx <package>@<version>      # バージョン指定で実行
```

## 参考リソース

- [npm documentation](https://docs.npmjs.com/)
- [npmjs.com](https://www.npmjs.com/)
