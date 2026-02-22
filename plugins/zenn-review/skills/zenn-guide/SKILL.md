---
name: zenn-guide
description: >
  Zenn記法・フロントマター仕様・レビュー基準のクイックリファレンス。
  Zennの記事や書籍を執筆・レビューする際に参照する。
  トリガー: 「Zennの記事をレビューして」「フロントマターの書き方」「Zenn記法を教えて」
  「書籍のconfig.yamlの仕様」「レビュー基準を確認したい」「Zennの構文チェック」
  「:::messageの使い方」「topicsの指定方法」「記事のフロントマター」
globs:
  - "articles/**/*.md"
  - "books/**/*.md"
  - "books/**/config.yaml"
---

# Zenn Guide — クイックリファレンス

## 使い方

- Zenn固有のMarkdown構文（:::message, 埋め込み等）の詳細は [zenn-syntax.md](zenn-syntax.md) を参照する
- フロントマターやconfig.yamlのフィールド仕様・バリデーションは [zenn-frontmatter.md](zenn-frontmatter.md) を参照する
- 記事の品質レビュー（スコアリング・レポート作成）の基準は [review-criteria.md](review-criteria.md) を参照する

## Zenn コンテンツ構造

| 種別 | パス | 説明 |
|------|------|------|
| 記事 | `articles/<slug>.md` | 個別の技術記事（slug: a-z0-9, ハイフン, アンダースコア, 12〜50文字） |
| 書籍 | `books/<slug>/` | 書籍ディレクトリ |
| 書籍設定 | `books/<slug>/config.yaml` | 書籍メタデータ |
| チャプター | `books/<slug>/<chapter>.md` | 各章（ファイル名またはconfig.yamlのchaptersで順序制御） |

## 記事フロントマター（必須フィールド）

```yaml
---
title: "記事タイトル"        # 必須: 60文字以内推奨
emoji: "😊"                  # 必須: 絵文字1つ
type: "tech"                 # 必須: "tech" | "idea"
topics: ["topic1", "topic2"] # 必須: 1〜5個、小文字英数字・ハイフン
published: true              # 必須: true | false
publication_name: "my-publication" # 任意: パブリケーションのslug
published_at: "2024-01-15 09:00" # 任意: 公開日時（YYYY-MM-DD HH:MM, JST）
---
```

## 書籍 config.yaml

```yaml
title: "書籍タイトル"        # 必須
summary: "概要"              # 必須: 200文字以内推奨
topics: ["topic1"]           # 必須: 1〜5個
published: true              # 必須
price: 0                     # 必須: 0（無料）| 200〜5000（100円単位）
chapters:                    # 任意: 章の順序指定
  - intro
  - chapter1
```

## Zenn 固有構文（主要なもの）

| 構文 | 用途 |
|------|------|
| `:::message` | 情報メッセージ |
| `:::message alert` | 警告メッセージ |
| `:::details タイトル` | アコーディオン |
| `$$` ... `$$` | 数式（KaTeX） |
| `@[youtube](VIDEO_ID)` | YouTube埋め込み |
| `@[card](URL)` | リンクカード |
| `` ```diff `` | diff表示コードブロック |
| `^[脚注の内容]` | インライン脚注 |

## 詳細リファレンス

- Zenn固有構文の詳細を確認するには → [zenn-syntax.md](zenn-syntax.md)
- フロントマター・config.yamlのフィールド仕様を確認するには → [zenn-frontmatter.md](zenn-frontmatter.md)
- レビュースコアリングやレポートフォーマットを確認するには → [review-criteria.md](review-criteria.md)
