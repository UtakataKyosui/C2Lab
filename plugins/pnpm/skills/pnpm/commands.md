# pnpm / pnpx コマンドリファレンス

## インストール系

```bash
# 依存関係のインストール
pnpm install                       # package.json の全依存関係をインストール
pnpm install --prod                # dependencies のみ
pnpm install --frozen-lockfile     # lockfile から厳密インストール（CI 推奨）

# パッケージの追加
pnpm add <package>                 # dependencies に追加
pnpm add -D <package>              # devDependencies に追加
pnpm add -g <package>              # グローバルにインストール
pnpm add <package>@<version>       # バージョン指定
pnpm add <package>@latest

# パッケージの削除
pnpm remove <package>
pnpm remove -g <package>
```

## スクリプト実行

```bash
pnpm run <script>                  # scripts フィールドのコマンドを実行
pnpm <script>                      # run を省略可
pnpm test                          # pnpm run test
pnpm start                         # pnpm run start
pnpm run <script> -- --flag        # スクリプトに引数を渡す
```

## ワークスペース操作

```bash
# 特定パッケージのみ操作
pnpm --filter <package-name> run <script>
pnpm --filter ./packages/ui run build
pnpm --filter <pkg>... run build   # 依存関係含めて実行

# 全パッケージで実行
pnpm -r run <script>               # --recursive
pnpm -r --parallel run <script>    # 並列実行

# ルートのみ / ワークスペースのみ
pnpm --workspace-root run <script>
pnpm --filter '!<pkg>' run <script>  # 特定パッケージを除外
```

## パッケージ管理

```bash
pnpm update                        # 全パッケージを更新（semver 範囲内）
pnpm update --latest               # 最新版に更新（semver 範囲を超える）
pnpm update <package>
pnpm outdated                      # 更新可能なパッケージを表示
pnpm list                          # インストール済みパッケージ一覧
pnpm list --depth=0
```

## 公開

```bash
pnpm publish                       # パッケージを公開
pnpm publish --access public
pnpm -r publish                    # ワークスペース全パッケージを公開
```

## pnpx

```bash
pnpx <package>                     # パッケージを一時実行（npx 相当）
pnpx <package>@<version>
```

## pnpm-workspace.yaml

```yaml
# pnpm-workspace.yaml の例
packages:
  - 'packages/*'
  - 'apps/*'
  - '!**/test/**'    # テストディレクトリを除外
```

## pnpm why（依存関係の解析）

```bash
pnpm why <package>                 # パッケージがなぜインストールされているか表示
pnpm why lodash                    # 直接依存か、間接依存かを確認
pnpm why --recursive <package>    # 全ワークスペースで確認
```

## ストア管理（pnpm store）

pnpm はグローバルコンテンツアドレスストアでパッケージを共有します。

```bash
pnpm store path                    # ストアのパスを表示
pnpm store status                  # ストアの整合性を確認
pnpm store prune                   # 未使用のパッケージをストアから削除
pnpm store add <package>           # パッケージをストアにキャッシュ（インストールせず）
```

## pnpm-workspace.yaml 高度設定

```yaml
# pnpm-workspace.yaml の高度な例
packages:
  - 'packages/*'
  - 'apps/*'
  - '!**/test/**'                  # テストディレクトリを除外

# カタログ機能（pnpm v9+）: バージョンを一元管理
catalog:
  react: ^18.3.0
  typescript: ^5.5.0
  vitest: ^2.0.0
```

```bash
# カタログからインストール
pnpm add react                     # catalog: の react バージョンが使用される
```

## .npmrc (pnpm 設定)

```ini
# .npmrc の例
shamefully-hoist=true              # 互換性のためホイスティングを有効化
strict-peer-dependencies=false
public-hoist-pattern[]=*eslint*
public-hoist-pattern[]=*prettier*
```
