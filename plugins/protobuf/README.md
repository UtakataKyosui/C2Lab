# protobuf-tools

Protocol Buffers (protobuf) の設計・実装を支援するプラグイン。

## 概要

protobuf のスタイルガイド、ベストプラクティス、ツール活用方法を提供する。`.proto` ファイルの設計から gRPC サービスの実装まで幅広くカバーする。

## 提供コンポーネント

### Skills

| スキル名 | 説明 |
|----------|------|
| `protobuf-tools` | Protocol Buffers の使用ガイド。概要と各ガイドへのリンクを提供する。詳細はサブファイルを参照。 |

**スキルが自動ロードされるファイルパターン**:
- `**/*.proto`
- `**/gen/**`
- `**/*protobuf*/**`
- `**/*grpc*/**`

### ガイド

| ファイル | 内容 |
|----------|------|
| `guides/style-guide.md` | protobuf スタイルガイド（命名規則、フィールド番号、コメント等） |
| `guides/best-practices.md` | 後方互換性、バージョニング、フィールド設計のベストプラクティス |
| `guides/tools.md` | protoc、buf、grpc-gateway 等のツール活用方法 |

## 使い方

`.proto` ファイルや gRPC 関連ファイルを開いているとき、参照情報が自動的に提供される。

```
protobuf でページネーションを設計したい
gRPC サービスのベストプラクティスは？
buf でスキーマを検証する方法は？
```

## フック

なし
