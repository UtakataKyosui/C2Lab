---
name: uv
description: uv / uvx の総合ガイド。pip・pipx・pyenv の代替として Python 依存関係とツールを高速管理する。詳細はサブファイルを参照。
globs:
  - "**/pyproject.toml"
  - "**/uv.lock"
---

# uv / uvx Guide

## 概要

`uv` は Rust で書かれた高速な Python パッケージマネージャーです。pip・pip-tools・pipx・pyenv・venv を一つのツールで置き換えます。`uvx` は pipx 相当のツール実行コマンドです。

詳細な情報は以下のファイルに分割されています。必要に応じて参照してください。

### 📚 詳細ガイド

1. **[Package Management](./guides/package-management.md)**
   - 依存関係の追加・削除・同期
   - 仮想環境と lockfile の管理

2. **[Tool Management](./guides/tool-management.md)**
   - `uvx` によるツールの一時実行
   - グローバルツールのインストール・管理

## クイックリファレンス

```bash
# プロジェクト管理
uv init                      # 新規プロジェクト初期化
uv add <package>             # 依存関係を追加
uv remove <package>          # 依存関係を削除
uv sync                      # uv.lock と環境を同期
uv lock                      # lockfile を更新

# スクリプト実行
uv run python <script.py>    # 仮想環境内で実行
uv run <tool>                # pyproject.toml の scripts を実行

# ツール実行（uvx）
uvx <tool>                   # ツールを一時インストールして実行
uvx ruff check .             # 例: ruff を実行

# Python バージョン管理
uv python install 3.12       # Python 3.12 をインストール
uv python pin 3.12           # プロジェクトの Python バージョンを固定
```

## 参考リソース

- [uv documentation](https://docs.astral.sh/uv/)
- [uv on GitHub](https://github.com/astral-sh/uv)
