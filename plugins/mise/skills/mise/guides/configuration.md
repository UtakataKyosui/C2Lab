# mise Configuration Guide

## .mise.toml の基本構造

```toml
[tools]
node = "22"
python = "3.12"
go = "latest"
rust = "stable"

[env]
NODE_ENV = "development"
DATABASE_URL = "postgres://localhost/myapp"

[tasks.build]
run = "npm run build"
description = "プロジェクトをビルド"

[tasks.test]
run = "npm test"
description = "テストを実行"
```

## ツールのバージョン指定

```toml
[tools]
# 完全バージョン指定
node = "22.0.0"

# マイナーバージョン以降を自動選択
node = "22"

# エイリアス
node = "lts"
node = "latest"

# バージョン範囲
node = ">=20"

# 複数バージョンをインストール（最初のものがデフォルト）
node = ["22", "20"]
```

## 環境変数

```toml
[env]
# 固定値
NODE_ENV = "development"
API_URL = "http://localhost:3000"

# 既存の環境変数を参照
DATABASE_URL = "{{env.DATABASE_URL}}"

# パスの追加
_.PATH = "./bin:{{env.PATH}}"

# .env ファイルを読み込む
_.file = ".env"
```

## タスク定義

```toml
[tasks.dev]
run = "npm run dev"
description = "開発サーバーを起動"

[tasks.test]
run = ["npm run lint", "npm test"]  # 複数コマンドを順次実行
description = "lint とテストを実行"

[tasks.build]
run = "npm run build"
depends = ["test"]                  # 依存タスク（先に実行される）

[tasks.deploy]
run = "./scripts/deploy.sh"
env = { DEPLOY_ENV = "production" } # タスク固有の環境変数
```

## タスクの実行

```bash
mise run <task>                    # タスクを実行
mise run --list                    # タスク一覧を表示
mise run build                     # ビルド
mise run test -- --watch           # タスクに引数を渡す（-- の後）
```

## 設定の継承

`.mise.toml` はディレクトリ階層に従って読み込まれます。

```
$HOME/.config/mise/config.toml    # グローバル設定
/project/.mise.toml               # プロジェクト設定（上書き）
/project/src/.mise.toml           # サブディレクトリ設定（さらに上書き）
```

## グローバル設定

```bash
# グローバル設定ファイルの場所
~/.config/mise/config.toml

# グローバルツールの設定
mise use -g node@22
mise use -g python@3.12
```

## mise の設定（動作オプション）

```toml
# .mise.toml の [settings] セクション
[settings]
verbose = false
experimental = false
jobs = 4                           # 並列インストール数
```
