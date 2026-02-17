---
description: scaffdogとコロケーションパターンをプロジェクトに導入する。フレームワーク検出、scaffdogインストール案内、スターターテンプレート生成を行う。
---

# scaffdog-colocation: init

プロジェクトにscaffdogとコロケーションパターンを導入します。以下の手順を実行してください。

## 1. フレームワーク検出

プロジェクトルートの `package.json` を読み取り、使用フレームワークを特定する:

- `react` / `react-dom` → React
- `vue` → Vue
- `svelte` / `@sveltejs/kit` → Svelte
- `next` → Next.js (React)
- `nuxt` → Nuxt (Vue)
- いずれもなし → TypeScript / Node.js

## 2. パッケージマネージャー検出

以下のロックファイルの存在を確認:

| ファイル | パッケージマネージャー |
|---|---|
| `bun.lockb` | bun |
| `pnpm-lock.yaml` | pnpm |
| `yarn.lock` | yarn |
| `package-lock.json` | npm |

## 3. scaffdog インストール確認

`package.json` の `devDependencies` に `scaffdog` があるか確認する。

**なければ**、ユーザーにインストールコマンドを提示:

```bash
# 検出されたパッケージマネージャーに応じて
npm install -D scaffdog
pnpm add -D scaffdog
yarn add -D scaffdog
bun add -D scaffdog
```

ユーザーの了承を得てからインストールを実行する。

## 4. `.scaffdog/` ディレクトリ作成

`.scaffdog/` ディレクトリが存在しない場合は作成する。

## 5. scaffdog-template-generator エージェント呼び出し

検出されたフレームワークに基づいて、`scaffdog-template-generator` エージェントを呼び出し、以下のスターターテンプレートを生成する:

- `.scaffdog/component.md` - コンポーネントテンプレート
- `.scaffdog/feature.md` - フィーチャーテンプレート

エージェントにはフレームワーク名、スタイルソリューション（CSS Modules / Tailwind / none）、テスト含有の有無をパラメータとして渡す。

## 6. 完了メッセージ

生成されたファイルの一覧と、次のステップを表示:

```
✓ scaffdog-colocation 初期化完了

生成されたテンプレート:
  - .scaffdog/component.md
  - .scaffdog/feature.md

次のステップ:
  1. /scaffdog-colocation:scaffold でファイルを生成
  2. /scaffdog-colocation:generate-template でカスタムテンプレートを追加
  3. /scaffdog-colocation:validate でプロジェクト構造を検証
```
