# activitypub-c2s

ActivityPub Client-to-Server (C2S) インタラクションの実装を支援するプラグイン。

## 概要

ActivityPub プロトコルの C2S 仕様に基づいた実装ガイドを提供する。Actor の構造設計、Inbox/Outbox の動作、Activity Types の実装などをカバーする。

## 提供コンポーネント

### Skills

| スキル名 | 説明 |
|----------|------|
| `activitypub-c2s` | ActivityPub C2S インタラクションの実装ガイド。概要とリファレンスを提供し、詳細はサブファイルを参照。 |

**スキルが自動ロードされるファイルパターン**:
- `**/*activitypub*/**`
- `**/ap/**`
- `**/*federation*/**`

### ガイド

| ファイル | 内容 |
|----------|------|
| `guides/concepts.md` | JSON-LD & Context、Actor 構造、ID & URI の設計 |
| `guides/messaging.md` | Inbox/Outbox の動作、Side Effects |
| `guides/activities.md` | Activity Types（Create, Update, Delete 等）の実装 |

## 使い方

ActivityPub 関連のファイルを開いているとき、またはスキル名でメンションすると参照情報が自動的に提供される。

```
ActivityPub の Outbox に投稿する実装を教えて
Actor の JSON-LD 構造を設計したい
```

## フック

なし
