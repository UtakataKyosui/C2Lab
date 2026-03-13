---
name: pr-lifecycle
description: >
  PR ライフサイクル全体のワークフロースキル。PR 作成・CI ローカル検証・レビュー対応・マージ準備の手順を標準化する。
  以下の場合に使用: (1) PR を作成するとき (2) push 前に CI を検証したいとき (3) マージ前の準備確認をするとき
  (4) 「PR を作る」「CI チェック」「push する前に」「マージ準備」「pre-push」と指示されたとき
---

# PR ライフサイクル

PR 作成から CI 検証・レビュー対応・マージまでの一連の手順。

## ライフサイクル概要

```
1. ブランチ作成 → 2. 実装 → 3. CI ローカル検証 → 4. PR 作成 → 5. レビュー対応 → 6. マージ
```

## ステップ 1: CI ローカル検証（push 前に必ず実施）

push する前に、変更したファイルに対応する CI コマンドをすべて実行する。
詳細なコマンドは `references/ci-checks.md` を参照。

**検出方法**: プロジェクトルートのファイルで言語を判定する。

| ファイル | 言語 | 実行すべき CI |
|---------|------|--------------|
| `package.json` | TypeScript/JS | prettier + eslint |
| `pyproject.toml` / `setup.py` | Python | ruff check + ruff format |
| `Cargo.toml` | Rust | cargo fmt --check + cargo clippy |

**重要**: 1 つの CI を直して push し、別の CI が落ちるのを繰り返さない。
push 前に全種類の CI を一度に確認する。

## ステップ 2: PR 作成

PR を作成するときの規約は `references/conventions.md` を参照。

**要点**:
- タイトル: `<type>: <概要>` 形式（feat, fix, refactor, docs, chore）
- 本文: 変更の目的（why）を記載する
- jj を使う場合: `jj-safe-push` スキルを使って push する

## ステップ 3: レビュー対応

PR レビューコメントへの対応は `review-workflow` プラグインを使用する。

**規約**:
- コード提案には必ず ` ```suggestion` ブロックを使う（plain コメントは不可）
- 各コメントに返信してから resolve する
- 対応後は review-workflow の verify コマンドで再検証する

## ステップ 4: マージ前チェックリスト

マージする前に以下を確認する:

- [ ] すべての CI が green
- [ ] すべてのレビューコメントに返信済み（resolved かどうかではなく replied かどうか）
- [ ] 不要なデバッグコード・console.log がない
- [ ] 関連するテストが追加・更新されている

詳細リファレンスは各 `references/` ファイルを参照。
