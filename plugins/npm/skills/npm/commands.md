# npm / npx コマンドリファレンス

## インストール系

```bash
# 依存関係のインストール
npm install                        # package.json の全依存関係をインストール
npm install --production           # dependencies のみ（devDependencies を除く）
npm ci                             # package-lock.json から厳密インストール（CI 推奨）
npm ci --legacy-peer-deps          # peer deps の競合を無視

# パッケージの追加
npm install <package>              # dependencies に追加
npm install -D <package>           # devDependencies に追加（--save-dev）
npm install -g <package>           # グローバルにインストール
npm install <package>@<version>    # バージョン指定
npm install <package>@latest       # 最新版

# パッケージの削除
npm uninstall <package>
npm uninstall -g <package>
```

## スクリプト実行

```bash
npm run <script>                   # scripts フィールドのコマンドを実行
npm test                           # npm run test の省略形
npm start                          # npm run start の省略形
npm run build                      # ビルド
npm run lint                       # lint
npm run <script> -- --flag         # スクリプトに引数を渡す（-- が必要）
```

## パッケージ管理

```bash
npm update                         # 全パッケージを更新（semver 範囲内）
npm update <package>               # 特定パッケージを更新
npm outdated                       # 更新可能なパッケージを表示
npm list                           # インストール済みパッケージ（ツリー表示）
npm list --depth=0                 # トップレベルのみ表示
npm list -g                        # グローバルパッケージ一覧
```

## 公開・レジストリ

```bash
npm publish                        # パッケージを公開
npm publish --access public        # スコープ付きパッケージを公開
npm publish --dry-run              # 実際には公開せずに確認

npm version patch                  # パッチバージョンを上げる（1.0.0 → 1.0.1）
npm version minor                  # マイナーバージョンを上げる（1.0.0 → 1.1.0）
npm version major                  # メジャーバージョンを上げる（1.0.0 → 2.0.0）

npm adduser                        # ログイン
npm whoami                         # 現在のログインユーザー
npm logout
```

## npx

```bash
npx <package>                      # パッケージを一時インストールして実行
npx <package>@<version>            # バージョン指定で実行
npx --yes <package>                # 確認なしで実行
npx --no-install <package>         # インストール済みのみ実行（インストールしない）

# 代表的な使い方
npx create-react-app my-app
npx create-next-app@latest my-app
npx tsc --init
```

## その他

```bash
npm init                           # package.json を対話的に作成
npm init -y                        # デフォルト値で package.json を作成
npm audit                          # 脆弱性チェック
npm audit fix                      # 脆弱性の自動修正
npm cache clean --force            # キャッシュをクリア
npm info <package>                 # パッケージ情報を表示
npm search <keyword>               # パッケージを検索
```

## .npmrc 設定

```ini
# プロジェクト .npmrc の例
registry=https://registry.npmjs.org/
@myorg:registry=https://npm.pkg.github.com/
save-exact=true                    # バージョンを固定（^ なし）
```
