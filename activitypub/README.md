# ActivityPub C2S Plugin

Claude Code で ActivityPub Client-to-Server (C2S) インタラクションを効率的に実装するためのプラグインです。

## 特徴

- **段階的な情報提供**: 基本概念、メッセージング、アクティビティ仕様の3つの詳細ガイドに分かれています。
- **実装ガイド**: JSON-LD Context や Actor モデル、Inbox/Outbox の挙動について詳しく解説しています。

## 構成

- `skills/activitypub-c2s/SKILL.md`: メインエントリポイント
- `skills/activitypub-c2s/guides/`: 詳細ガイドディレクトリ
    - `concepts.md`: 基本概念（JSON-LD, Actor, ID等）
    - `messaging.md`: メッセージング（Inbox, Outbox, Side Effects）
    - `activities.md`: 主要なアクティビティ定義と例
