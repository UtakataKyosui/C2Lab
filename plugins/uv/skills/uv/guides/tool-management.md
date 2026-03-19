# Tool Management with uvx

## uvx（ツールの一時実行）

`uvx` は pipx 相当のコマンドです。ツールをグローバルにインストールせず、一時的な環境で実行します。

```bash
uvx <tool>                         # ツールを一時実行
uvx ruff check .                   # ruff で lint
uvx black <file>                   # black でフォーマット
uvx mypy <file>                    # mypy で型チェック
uvx pytest                         # pytest を実行
uvx <tool>==<version>              # バージョン指定
uvx --from <package> <command>     # パッケージ名とコマンド名が異なる場合
```

## uv tool（グローバルツール管理）

pipx の完全な代替として、グローバルツールを管理できます。

```bash
# ツールのインストール
uv tool install ruff               # グローバルにインストール
uv tool install black
uv tool install mypy

# ツールの実行（インストール済み）
ruff check .                       # 直接コマンドとして使用可能

# ツールの更新
uv tool upgrade ruff               # 特定ツールを更新
uv tool upgrade --all              # 全ツールを更新

# ツールの削除
uv tool uninstall ruff

# インストール済みツール一覧
uv tool list

# ツールのパスを確認
uv tool dir                        # ツールインストールディレクトリ
```

## Python バージョン管理

```bash
# Python のインストール
uv python install 3.12             # Python 3.12 をインストール
uv python install 3.11 3.12 3.13   # 複数バージョンを同時インストール

# バージョンの固定
uv python pin 3.12                 # .python-version に書き込む
uv python pin pypy@3.10            # PyPy も対応

# インストール済みバージョン一覧
uv python list
uv python list --only-installed    # インストール済みのみ

# Python の検索
uv python find 3.12                # 3.12 の実行ファイルパスを表示
```

## CI での使い方

```yaml
# GitHub Actions の例
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    version: "latest"

- name: Set up Python
  run: uv python install 3.12

- name: Install dependencies
  run: uv sync --frozen

- name: Run tests
  run: uv run pytest
```

## よく使うツールの uvx コマンド

```bash
# Linting / Formatting
uvx ruff check .
uvx ruff format .
uvx black .
uvx isort .

# 型チェック
uvx mypy .
uvx pyright .

# テスト
uvx pytest
uvx coverage run -m pytest

# ドキュメント生成
uvx mkdocs build
uvx sphinx-build docs docs/_build

# パッケージ公開
uvx twine upload dist/*
uvx build                          # パッケージのビルド（python-build）
```
