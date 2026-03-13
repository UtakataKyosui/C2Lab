---
name: obsidian-consolidate
description: >
  作業区切りに会話の要点を整理し、デイリーノートへ書き込む。
  「今日の作業をまとめて」「Obsidianに固定化して」「セッションの学びを記録して」
  「/obsidian-consolidate」といった指示で使用する。
  再利用性が高い知識は独立したトピックノートにも切り出す。
---

# obsidian-consolidate

作業区切りにセッションの学びをデイリーノートへ書き出す（システム固定化）。

## なぜ SessionEnd ではなく手動呼び出しなのか

`SessionEnd` は Claude Code が閉じられる瞬間に発火するため、そのタイミングでの要約生成はできない。
「この作業はここまで」と感じたタイミングで手動で呼び出す運用にする。

## 手順

1. **セッション中の主な学びを3〜5点に要約する**

   以下の観点で振り返る:
   - 解決したエラーとその原因
   - 新しく理解したライブラリの挙動
   - 設計・実装上の意思決定とその理由
   - 次回への申し送り事項

2. **デイリーノートへ追記する**

   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" daily:append content="<要約テキスト>"
   ```

3. **汎用性の高い知識を独立したノートとして切り出す**

   ライブラリの挙動・デバッグのコツなど再利用できる知識は `knowledge/` へ:
   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" create \
     name="<トピック名>" \
     path="knowledge/" \
     content="<ノート内容>"
   ```

4. **切り出したノートをデイリーノートから `[[リンク]]` で参照する**

   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" daily:append \
     content="- [[<トピック名>]] を作成"
   ```

## 書き込みフォーマット例

```markdown
## <プロジェクト名> - <日付>

### 学んだこと
- jj の `--ignore-immutable` フラグで immutable commit を強制変更できる → [[jj-immutable-commits]]
- React の `useEffect` クリーンアップは依存配列の変更前にも実行される

### 意思決定
- obsidian-knowledge と obsidian-memory は別プラグインとして分離した
  理由: 用途（コーディング知識 vs Claude メモリ同期）が異なるため

### 次回への申し送り
- obsidian-consolidate の hook 化を検討（SessionEnd 代替）
```
