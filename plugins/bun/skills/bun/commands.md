# Bun コマンドリファレンス

## ランタイム

```bash
# ファイルの実行
bun run <file.ts>                  # TypeScript/JavaScript を直接実行
bun <file.ts>                      # run を省略可
bun run <script>                   # package.json の scripts を実行
bun <script>                       # run を省略可

# REPL
bun repl                           # 対話モードを起動

# TypeScript
bun run --hot <file.ts>            # ホットリロードで実行
bun run --watch <file.ts>          # ファイル変更を監視して再実行
```

## パッケージ管理

```bash
# インストール
bun install                        # package.json の全依存関係をインストール
bun install --frozen-lockfile      # bun.lockb から厳密インストール（CI 推奨）
bun install --production           # dependencies のみ

# パッケージの追加
bun add <package>                  # dependencies に追加
bun add -d <package>               # devDependencies に追加（--dev）
bun add <package>@<version>

# パッケージの削除
bun remove <package>

# 更新
bun update                         # 全パッケージを更新
bun update <package>               # 特定パッケージを更新
bun outdated                       # 更新可能なパッケージを表示
```

## bunx（一時実行）

```bash
bunx <package>                     # パッケージを一時インストールして実行（npx 相当）
bunx <package>@<version>           # バージョン指定
bunx --bun <package>               # bun ランタイムで実行（node の代わりに）

# よく使う例
bunx create-next-app@latest my-app
bunx prettier --write .
bunx tsc --init
```

## テスト

```bash
bun test                           # テストを実行（*.test.ts, *.spec.ts）
bun test <file>                    # 特定ファイルのみ
bun test --watch                   # ウォッチモード
bun test --coverage                # カバレッジを表示
bun test --bail                    # 最初の失敗で停止
bun test --timeout 5000            # タイムアウト設定（ms）
```

## ビルド

```bash
bun build <entrypoint>             # バンドル
bun build ./index.ts --outdir ./dist
bun build ./index.ts --outfile ./dist/bundle.js
bun build --target browser         # ターゲット: browser / bun / node
bun build --minify                 # ミニファイ
bun build --sourcemap              # ソースマップ生成
bun build --splitting              # コード分割
```

## プロジェクト作成

```bash
bun init                           # 新規プロジェクトを対話的に初期化
bun create <template>              # テンプレートから作成
bun create react my-app
bun create next my-app
```

## ワークスペース（monorepo）

```bash
# --filter で対象ワークスペースを指定
bun run --filter <workspace> <script>
bun run --filter './packages/*' build  # glob 指定
bun run --filter '!./packages/ui' test # 除外

# ワークスペース全体に依存を追加
bun add <package> --filter ./packages/utils
```

```json
// package.json（ルート）
{
  "workspaces": ["packages/*", "apps/*"]
}
```

## TypeScript / JSX ネイティブ設定

bun は TypeScript・JSX をトランスパイルなしで直接実行します。

```bash
# tsconfig.json を自動検出して実行
bun run app.tsx

# JSX ファクトリの変更（デフォルトは React.createElement）
bun build --jsx-factory h --jsx-fragment Fragment ./app.tsx
```

```json
// tsconfig.json（bun 推奨設定）
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true
  }
}
```

## Node.js 互換性

```bash
# Node.js 互換モードで実行
bun --bun run <script>             # bun ランタイムを明示
bun --smol run <script>           # メモリ節約モード

# Node.js との非互換を確認
bun run --no-install <script>     # インストールせず実行
```

bun は多くの Node.js API と npm パッケージに互換性がありますが、ネイティブ拡張（`.node` ファイル）はサポートしていません。
`node:` プレフィックスの組み込みモジュールはほぼ全てサポート済みです。

## その他

```bash
bun pm ls                          # インストール済みパッケージ一覧
bun pm cache rm                    # キャッシュをクリア
bun --version                      # バージョン確認
bun upgrade                        # bun 自体を更新
```
