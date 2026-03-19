---
name: gh
description: GitHub CLI (gh) の総合ガイド。PR 作成・レビュー・マージ、Issue 管理、リリース操作の概要を提供する。詳細はサブファイルを参照。
---

# GitHub CLI (gh) Guide

## 概要

`gh` は GitHub の公式 CLI ツールです。ブラウザを開かずにターミナルから PR・Issue・リリース・ワークフローを操作できます。

詳細な情報は以下のファイルに分割されています。必要に応じて参照してください。

### 📚 詳細ガイド

1. **[PR Workflow](./guides/pr-workflow.md)**
   - PR の作成・レビュー・マージ
   - レビューコメントへの返信
   - CI ステータスの確認

2. **[Issue & Release](./guides/issue-release.md)**
   - Issue の作成・クローズ・ラベル操作
   - リリースの作成と管理
   - GitHub Actions ワークフロー操作

## 認証セットアップ

```bash
# ブラウザ経由でログイン（推奨）
gh auth login

# トークンでログイン（CI 環境向け）
gh auth login --with-token <<< "$GITHUB_TOKEN"

# 認証状態を確認
gh auth status

# ログアウト
gh auth logout

# 複数アカウントの切り替え（v2.40+）
gh auth switch
```

## gh search（コード・Issue・PR を検索）

```bash
# Issue を検索
gh search issues "memory leak" --repo owner/repo
gh search issues --assignee @me --state open

# PR を検索
gh search prs "fix: auth" --state merged --limit 10

# コードを検索
gh search code "TODO" --repo owner/repo

# レポジトリを検索
gh search repos "mise plugin" --language shell --sort stars
```

## クイックリファレンス

```bash
# PR
gh pr create --title "..." --body "..."
gh pr list
gh pr view <number>
gh pr merge <number>

# Issue
gh issue create --title "..."
gh issue list
gh issue close <number>

# リリース
gh release create v1.0.0 --title "v1.0.0" --notes "..."
gh release list

# ワークフロー
gh run list
gh run view <run-id>
```

## 参考リソース

- [gh documentation](https://cli.github.com/manual/)
- [gh on GitHub](https://github.com/cli/cli)
