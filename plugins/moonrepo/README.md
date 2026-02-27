# moon-proto

Moonrepo（タスクランナー）と proto（ツールチェーンマネージャー）の統合利用を支援するプラグイン。

## 概要

moon によるモノレポのタスク管理と、proto によるツールチェーン（Node.js、Rust、Go 等）のバージョン管理をカバーする。ワークスペース設定からタスク定義、proto ツールの管理まで網羅したガイドを提供する。

## 提供コンポーネント

### Skills

| スキル名 | 説明 |
|----------|------|
| `moon-proto` | Moonrepo と proto の統合利用ガイド。環境構築・タスク管理・ワークスペース設定の概要を提供する。詳細はサブファイルを参照。 |

**スキルが自動ロードされるファイルパターン**:
- `**/.moon/**`
- `**/moon.yml`
- `**/.prototools`

### ガイド

| ファイル | 内容 |
|----------|------|
| `guides/proto-management.md` | proto によるツールチェーン管理（インストール、バージョン固定、`.prototools` 設定） |
| `guides/moon-tasks.md` | moon タスクの定義・実行・継承・依存関係 |
| `guides/workspace-config.md` | ワークスペース設定（`moon.yml`、`.moon/workspace.yml`）と CI 連携 |

## 使い方

moon や proto 関連のファイルを開いているとき、または操作について質問すると参照情報が自動的に提供される。

```
moon でタスクを定義する方法は？
proto で Node.js のバージョンを固定したい
.moon/workspace.yml の設定方法を教えて
```

## フック

なし
