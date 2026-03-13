# PR 規約リファレンス

このプロジェクトで PR を作成・対応する際の規約。

## PR タイトル形式

```
<type>: <概要（日本語可）>
```

type の種類:
- `feat`: 新機能
- `fix`: バグ修正
- `refactor`: リファクタリング
- `docs`: ドキュメント
- `chore`: ビルド・設定変更
- `test`: テスト追加・修正
- `ci`: CI 設定変更

## PR 本文テンプレート

```markdown
## 概要

<!-- why（なぜこの変更が必要か）を書く -->

## 変更内容

-

## テスト

- [ ] ローカルで動作確認済み
- [ ] 関連テストを追加・更新済み
```

## レビューコメントへの返信規約

- コード修正を提案する場合は必ず ` ```suggestion` ブロックを使う
- plain インラインコメントではなく、必ず suggestion 形式にする
- 各レビューコメントに対して「修正した内容」を日本語で返信する
- 「resolved」にするだけでなく、**返信してから** resolve する

例（正しい形式）:
````markdown
ご指摘ありがとうございます。修正しました。

```suggestion
const result = items.filter(Boolean);
```
````

## 設定ファイルの規約

- ローカル/個人設定: `.claude/settings.local.json`（git ignore 済み）
- プロジェクト共有設定: `.claude/settings.json`（コミット対象）
- カスタム設定ファイルを独自に作らない

## VCS（バージョン管理）

- jj（Jujutsu）を使うプロジェクトでは `jj-safe-push` スキルを経由して push する
- `git push` の直接実行は避ける
- 単一コミットのみでの push は原則行わない
