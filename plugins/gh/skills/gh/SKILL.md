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
