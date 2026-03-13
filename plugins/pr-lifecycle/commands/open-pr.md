---
name: open-pr
description: 現在のブランチから PR を作成する。タイトル・本文を自動生成し、規約に従ったフォーマットで gh pr create を実行する。
argument-hint: "[PR タイトルまたは概要]"
allowed-tools:
  - Bash
  - Read
---

# PR 作成コマンド

現在のブランチのコミット差分を解析して PR を作成する。

## 実行手順

1. 現在のブランチと差分を確認する:
   ```bash
   # jj の場合
   jj log -r 'trunk()..@' --no-graph
   jj diff --stat

   # git の場合
   git log main..HEAD --oneline
   git diff --stat main..HEAD
   ```

2. `.jj` ディレクトリが存在する場合は jj プロジェクトとして扱う。
   存在しない場合は git として扱う。

3. CI チェックが未実施の場合は `/pr-lifecycle:ci-check` を先に実行することを提案する。

4. 引数からタイトルを生成する。引数がない場合はコミット内容から自動生成する。
   タイトル形式: `<type>: <概要>` (feat/fix/refactor/docs/chore/test/ci)

5. `gh pr create` で PR を作成する:
   ```bash
   gh pr create --title "<title>" --body "$(cat <<'EOF'
   ## 概要

   <変更の目的（why）>

   ## 変更内容

   <主な変更点>

   🤖 Generated with Claude Code
   EOF
   )"
   ```

6. 作成した PR の URL を表示する。

## 規約チェック

PR 作成前に以下を確認する:
- タイトルが `<type>: <概要>` 形式になっている
- 本文に「なぜこの変更が必要か」が記載されている
- 関連する Issue 番号があれば `Closes #<issue>` を本文に含める

詳細な規約は `pr-lifecycle` スキルの `references/conventions.md` を参照する。
