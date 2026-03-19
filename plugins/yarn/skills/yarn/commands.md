# Yarn コマンドリファレンス

## インストール系

```bash
# 依存関係のインストール
yarn                               # package.json の全依存関係をインストール
yarn install
yarn install --frozen-lockfile     # lockfile から厳密インストール（v1 CI 推奨）
yarn install --immutable           # lockfile から厳密インストール（v2+ CI 推奨）

# パッケージの追加
yarn add <package>                 # dependencies に追加
yarn add -D <package>              # devDependencies に追加（--dev）
yarn global add <package>          # グローバルにインストール（v1）
yarn add <package>@<version>       # バージョン指定

# パッケージの削除
yarn remove <package>
```

## スクリプト実行

```bash
yarn run <script>                  # scripts フィールドのコマンドを実行
yarn <script>                      # run を省略可
yarn test
yarn start
yarn build
```

## ワークスペース操作

### v1 (Classic)

```bash
yarn workspaces run <script>       # 全ワークスペースで実行
yarn workspace <pkg> <command>     # 特定ワークスペースで実行
yarn workspace @myorg/ui add react
```

### v2+ (Berry)

```bash
yarn workspaces foreach run <script>          # 全ワークスペースで実行
yarn workspaces foreach --parallel run build  # 並列実行
yarn workspaces foreach --topological run build  # 依存順に実行
```

## パッケージ管理

```bash
yarn upgrade                       # 全パッケージを更新（v1）
yarn up <package>                  # パッケージを更新（v2+）
yarn up '*'                        # 全パッケージを更新（v2+）
yarn outdated                      # 更新可能なパッケージを表示（v1）
yarn list                          # インストール済みパッケージ一覧
yarn info <package>                # パッケージ情報を表示
```

## 公開

```bash
yarn publish                       # パッケージを公開（v1）
yarn npm publish                   # パッケージを公開（v2+）
yarn version                       # バージョンを上げる（v1）
```

## Berry (v2+) 固有

```bash
# プラグイン管理
yarn plugin import <plugin>
yarn plugin list

# PnP の診断
yarn dlx @yarnpkg/doctor

# キャッシュ操作
yarn cache clean                   # キャッシュをクリア

# パッチ
yarn patch <package>               # パッケージをパッチ（ローカル修正）
```

## .yarnrc.yml (v2+ 設定)

```yaml
# .yarnrc.yml の例
nodeLinker: node-modules           # PnP を無効にして node_modules を使用
yarnPath: .yarn/releases/yarn-4.x.x.cjs
```
