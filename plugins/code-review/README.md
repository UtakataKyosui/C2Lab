# code-review-plugin

プログラミング原則とチェックリストに基づいてコードをレビューするプラグイン。

## 概要

SOLID 原則、DRY、YAGNI などのプログラミング原則に従ったコードであるか検証し、包括的なチェックリストでコードの品質を確認する。

## 提供コンポーネント

### Commands (Skills)

| コマンド | 説明 |
|----------|------|
| `code-review:principle` | プログラミング原則（SOLID, DRY, YAGNI 等）に従っているか検証してレビューする |
| `code-review:checklist` | チェックリスト項目を確認してコードの内容を精査する |

### Agents

| エージェント | 説明 |
|--------------|------|
| `Code-Reviewer` | コードレビューをサブエージェントとして実行する |

## 使い方

```
/code-review:principle
/code-review:checklist
```

または Task ツールで `Code-Reviewer` エージェントを指定してレビューを依頼する。

## フック

なし
