# Toolchain Management with proto

[proto](https://moonrepo.dev/proto) は多言語対応のツールチェーン管理ツールです。`.prototools` でバージョンを宣言し、チーム全員・CI が同じバージョンを使うことを保証します。

## インストール

```bash
# proto 自体のインストール
curl -fsSL https://moonrepo.dev/install/proto.sh | bash

# インストール確認
proto --version
```

## .prototools

プロジェクトルートに置くバージョン定義ファイルです。`proto install` で全ツールが一括インストールされます。

```toml
# .prototools の例
node = "22"
npm = "10"
pnpm = "9"
python = "3.12"
rust = "stable"
go = "1.22"
bun = "latest"

# バージョン範囲指定も可能
node = ">=20 <23"
```

## 基本コマンド

```bash
# .prototools の全ツールをインストール
proto install

# 特定ツール・バージョンを指定してインストール
proto install node 22
proto install node lts
proto install python 3.12.0
proto install rust stable

# インストール済みバージョン一覧
proto list node
proto list --all              # 全ツール一覧

# インストール可能なバージョンを確認
proto list-remote node
proto list-remote node | grep "^22"
```

## バージョン切り替え

```bash
# グローバルデフォルトを設定
proto pin node 22 --global

# プロジェクトのバージョンを固定（.prototools に書き込む）
proto pin node 22

# 一時的なバージョン切り替え
proto run node@20 -- --version

# シェルの PATH に proto 管理ツールを追加（初回セットアップ）
proto activate
```

## シェル統合

```bash
# .bashrc / .zshrc への自動統合
proto setup                   # PATH・シェル補完を設定

# 手動で有効化（setup 済みなら不要）
eval "$(proto activate bash)"
eval "$(proto activate zsh)"
```

## ツール情報

```bash
proto bin node                # node の実行ファイルパスを表示
proto which node              # 現在有効な node のパスを表示
proto upgrade                 # proto 自体を最新版に更新
proto clean                   # 未使用バージョンを削除してディスクを節約
```

## プラグイン拡張

proto は WASM プラグインで対応ツールを拡張できます。

```toml
# .prototools でプラグインを追加
[plugins]
my-tool = "https://example.com/my-tool.wasm"
```

```bash
proto plugin list             # 利用可能なプラグイン一覧
proto plugin add <name> <url> # プラグインを追加
```

## Moonrepo との連携

`.moon/toolchain.yml` を設定すると、Moon が自動で proto を使ってツールをセットアップします。

```yaml
# .moon/toolchain.yml
node:
  version: '22'
  packageManager: 'pnpm'
  pnpm:
    version: '9'

typescript:
  version: '5.4'

rust:
  edition: '2021'
```

`moon run` 実行時、必要なツールが `.moon/toolchain.yml` の定義に基づいて自動インストールされます。

## グローバル設定

```toml
# ~/.proto/config.toml
[settings]
auto-install = true           # コマンド実行時に自動インストール
auto-clean = true             # 古いバージョンを自動削除
telemetry = false             # テレメトリを無効化
```
