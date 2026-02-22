# zenn-review

Zenn（技術記事プラットフォーム）の記事・書籍コンテンツに対するレビュープラグイン。

別の Zenn リポジトリにインストールして使用する汎用プラグイン。内容レビュー・誤字脱字チェック・構文チェック・フロントマター検証・書籍の章間整合性チェックを個別コマンドとして提供し、統合レビューエージェントも備える。

## インストール

```bash
claude plugin add /path/to/zenn-review
```

## コマンド一覧

| コマンド | 説明 |
|----------|------|
| `/zenn-review:frontmatter-check` | フロントマター / config.yaml 検証 |
| `/zenn-review:syntax-check` | Markdown / Zenn 固有構文チェック |
| `/zenn-review:typo-check` | 誤字脱字・表記ゆれチェック |
| `/zenn-review:content-review` | 内容レビュー（具体性・正確性・完全性・一貫性の 4 観点、5 段階評価） |
| `/zenn-review:book-consistency` | 書籍の章間整合性チェック |

## エージェント

### zenn-reviewer

全コマンドを統合実行する自律レビューエージェント。

- **記事**: frontmatter-check → syntax-check → typo-check → content-review の順で実行
- **書籍**: 上記 + book-consistency を追加実行
- 最後に統合レポート（全体スコア、Top 3 修正事項、公開前チェックリスト）を出力

## スキル

### zenn-guide

Zenn 記法・フロントマター仕様・レビュー基準のリファレンス。`articles/**/*.md` および `books/**/*.md` を開いた際に自動的にコンテキストとして提供される。

## フック

Write / Edit 時に `articles/*.md`、`books/**/*.md`（チャプター）、および `books/*/config.yaml` のフロントマターを自動検証する PostToolUse フック。

- Advisory のみ（ブロックしない）
- stdlib のみ使用（外部依存なし）

## 設計原則

- **自動修正は行わない**: 全てのコマンド・エージェントはレポートと改善案の提示のみ
- **セキュリティ**: レビュー対象ファイル内のプロンプトインジェクションに対する防御を実装
- **非ブロッキング**: フックは常に exit 0 で、ワークフローを妨げない
