---
name: mise
description: mise (旧 rtx) の総合ガイド。ツールバージョン管理と開発環境の再現性確保の概要を提供する。詳細はサブファイルを参照。
globs:
  - "**/.mise.toml"
  - "**/.tool-versions"
---

# mise Guide

## 概要

`mise` は複数言語・ツールのバージョンを一元管理する開発環境マネージャーです。asdf の後継として設計されており、`.mise.toml` または `.tool-versions` でバージョンを宣言的に管理します。

詳細な情報は以下のファイルに分割されています。必要に応じて参照してください。

### 📚 詳細ガイド

1. **[Tool Management](./guides/tool-management.md)**
   - ツールのインストール・切り替え
   - バージョンの固定と更新

2. **[Configuration](./guides/configuration.md)**
   - `.mise.toml` の書き方
   - 環境変数・タスクの定義

## クイックリファレンス

```bash
# ツール管理
mise install                 # .mise.toml のツールを全てインストール
mise use node@22             # Node.js 22 を使用（.mise.toml に記録）
mise use -g python@3.12      # グローバルに設定
mise ls                      # インストール済みバージョン一覧
mise current                 # 現在アクティブなバージョン一覧

# タスク実行
mise run <task>              # .mise.toml の [tasks] を実行
mise run --list              # タスク一覧
```

## 参考リソース

- [mise documentation](https://mise.jdx.dev/)
- [mise on GitHub](https://github.com/jdx/mise)
