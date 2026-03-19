# Tool Management with mise

## ツールのインストール

```bash
# .mise.toml のツールを全てインストール
mise install

# 特定ツールをインストール
mise install node@22
mise install node@lts
mise install python@3.12.0
mise install go@latest

# 複数バージョンを同時インストール
mise install node@20 node@22
```

## バージョンの選択・切り替え

```bash
# プロジェクトのバージョンを設定（.mise.toml に記録）
mise use node@22
mise use python@3.12

# グローバルのデフォルトバージョンを設定
mise use -g node@22
mise use --global python@3.12

# 一時的なバージョン切り替え
mise exec node@20 -- node --version

# シェルセッション内のみ変更
mise shell node@20
```

## バージョン確認

```bash
mise current                       # 現在アクティブなバージョン一覧
mise ls                            # インストール済みバージョン一覧
mise ls node                       # 特定ツールのバージョン一覧
mise ls-remote node                # インストール可能なバージョン一覧
mise ls-remote node | tail -20     # 最新20件
```

## ツールの更新・削除

```bash
mise upgrade                       # 全ツールを最新版に更新
mise upgrade node                  # 特定ツールを更新
mise uninstall node@20             # 特定バージョンを削除
mise prune                         # 使用されていないバージョンを削除
```

## シェル統合のセットアップ

mise を使うには、シェル起動スクリプトへの統合が必要です。

```bash
# bash
echo 'eval "$(mise activate bash)"' >> ~/.bashrc

# zsh
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc

# fish
echo 'mise activate fish | source' >> ~/.config/fish/config.fish

# 統合の確認
mise doctor                        # 診断情報を表示（PATH・シェル統合・ツール状態）
```

## バージョン優先順位

mise がバージョンを決定する優先順位（高い順）:

1. `mise shell` で設定した一時バージョン（`MISE_<TOOL>_VERSION` 環境変数）
2. カレントディレクトリの `.mise.toml`
3. 親ディレクトリを遡って見つかった `.mise.toml`
4. `~/.config/mise/config.toml`（グローバル設定）
5. `.tool-versions`（asdf 互換）

```bash
# どのバージョンが使われているか確認
mise current
mise which node                    # 実行ファイルのパスを確認
mise env                           # 現在の環境変数を表示
```

## mise doctor（診断）

```bash
mise doctor                        # 設定・PATH・ツールの問題を診断
mise doctor --json                 # JSON 形式で出力
```

`mise doctor` が報告する主な問題:
- シェル統合が未設定（PATH が通っていない）
- ツールバージョンが古い
- プラグインが壊れている

## asdf プラグインとの互換性

mise は asdf プラグインを利用できます。

```bash
# プラグインの追加
mise plugins add java
mise plugins add ruby
mise plugins ls-remote             # 利用可能なプラグイン一覧

# インストール
mise install java@21
```

## .tool-versions との互換性

mise は asdf の `.tool-versions` も読み込みます。

```
# .tool-versions の例（asdf 互換）
nodejs 22.0.0
python 3.12.0
```

ただし新規プロジェクトでは `.mise.toml` の使用を推奨します。
