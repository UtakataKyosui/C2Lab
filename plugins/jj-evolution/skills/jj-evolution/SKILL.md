---
name: jj-evolution
description: Jujutsu (jj) の高度なChange操作を活用し、並列開発・修正や履歴の書き換えを効率的に行うためのスキル。
globs:
  - "**/.jj/**"
---

# Jujutsu Evolution Workflow

## 概要

このスキルは、**Jujutsu (jj)** の最大の特徴である「Change（変更）」を中心としたワークフローを習得し、
従来のGitでは難易度の高い「並列開発」「履歴の柔軟な書き換え」を実現するためのガイドです。

### 主な機能

1.  **Parallel Development**: 複数のアイデアを同時に試行し、簡単に切り替える。
    *   `jj new`: 新しい変更を作成
    *   `jj edit`: 作業対象の変更を切り替え
2.  **History Rewriting**: コミット（Change）の内容を後から自在に編集する。
    *   `jj squash`: 変更を親に統合
    *   `jj split`: 変更を分割
    *   `jj rebase`: 変更の適用先を変更
3.  **Conflict Resolution**: コンフリクトを第一級市民として扱い、安全に解消する。
    *   `jj resolve`: マージツールの起動
4.  **PR Review Workflow**: Bookmark を活用し、複数PRのレビュー対応を並行して効率的に進める。
    *   `jj bookmark create/set/delete`: Bookmark の管理
    *   `jj git push -b`: Bookmark を指定して push

## 詳細ガイド

以下のガイドで具体的な手順を確認できます。

1.  **[Parallel Workflows](./guides/parallel-work.md)**
    *   並行して複数の修正案を試す方法 (`jj new`, `jj edit`)
    *   ブランチ（Bookmark）を使わない身軽な開発

2.  **[History Maintenance](./guides/history-maintenance.md)**
    *   コミットの統合・分割・並べ替え (`jj squash`, `jj split`, `jj rebase`)
    *   不要な変更の破棄 (`jj abandon`)

3.  **[Conflict & Collaboration](./guides/conflict-collab.md)**
    *   コンフリクト状態の理解と解消
    *   Gitとの連携（Push/Pull）

4.  **[PR Review Workflow](./guides/pr-review-workflow.md)**
    *   Bookmark の基本概念と Git ブランチとの対比
    *   1PR・複数PR並行時のレビュー対応フロー
    *   Bookmark 衝突への対処と整理

## コマンドリファレンス

困ったときは以下のコマンドでドキュメントを確認できます。

```bash
jj util markdown-help
```
