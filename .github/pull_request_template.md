# 🚀 Plugin PR Template for Claude Code

## 🧩 概要
このPRでは、以下の機能を追加・変更します。

- [ ] 新しいHookの追加
- [ ] SubAgentの実装
- [ ] カスタムコマンドの追加
- [ ] バグ修正 / 改善
- [ ] ドキュメント更新
- [ ] その他（詳細を下記に記載）

### 対象言語
<!-- 例: Rust / TypeScript / Python / Go など -->
`<language-name>`

### Plugin名 / 機能名
<!-- Pluginフォルダ名やコマンド名を明記 -->
`<plugin-name>`

---

## 🧠 目的・背景
この変更が必要になった理由や、解決したい課題を記述してください。

例：
- Rust用のSubAgentで、`cargo`操作を自動化したい  
- TypeScript用Pluginで、コード生成時にLintを自動実行したい  

---

## 🛠 変更内容
主な変更点を箇条書きでまとめてください。

例：
- `src/hooks/` に `onCodeGenerate.ts` を追加  
- `subagents/format_checker.rs` を新規追加  
- `commands.json` に `run-lint` コマンドを登録  

---

## ✅ 動作確認
動作確認方法を具体的に記載してください。

例：
1. `claude code --plugin <plugin-name>` を実行  
2. コマンド `run-lint` を呼び出す  
3. 成功メッセージ「Lint completed successfully」が出ることを確認  

- [ ] 手動での動作確認済み
- [ ] 自動テストを追加・更新済み

---

## 📘 補足・備考
追加の情報、注意点、関連Issue/PRなどがあれば記載してください。

- 関連Issue: #123  
- 参考: Claude Code Plugin開発ガイドライン（docs/plugin_dev.md）

---

## 🧩 Reviewerへのお願い
- [ ] コードスタイルと命名の確認
- [ ] Hook/Command登録の正しさ確認
- [ ] 不要な依存関係が含まれていないかチェック
- [ ] README更新が適切か確認

---

**👤 Author:** @<your-github-username>  
**📅 Date:** YYYY-MM-DD  
