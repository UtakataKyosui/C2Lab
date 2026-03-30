# playwright-e2e-tester

Playwright（ライブラリ）を使ったWebアプリのE2Eテスト自動化プラグイン。
開発中の機能確認とPRレビュー時の変更確認の2種類のSubAgentを提供します。

## 概要

このプラグインは、Playwright MCP ではなく **`@playwright/test` ライブラリ** を直接使用して TypeScript のE2Eテストを生成・実行します。
AgentがPlaywrightテストコードを書いてBashで実行するため、既存のPlaywright環境と自然に統合できます。

## 提供するコンポーネント

### Agents

| エージェント | 用途 | トリガー例 |
|---|---|---|
| `playwright-dev-tester` | 開発中の機能をE2Eテストで確認 | 「ログイン機能をPlaywrightで確認して」 |
| `playwright-review-tester` | PRの変更をE2Eテストで確認 | 「PR #42 をPlaywrightで検証して」 |

### Skills

| スキル | 内容 |
|---|---|
| `playwright-testing` | TypeScript Playwrightのロケーター・アサーション・テストパターン |

## 前提条件

```bash
# プロジェクトに Playwright をインストール
npm install -D @playwright/test
npx playwright install chromium
```

また、GitHub PR を確認する場合は `gh` CLI の認証が必要です:
```bash
gh auth login
```

## 使い方

### 開発時の機能確認

実装が完了したら、Agentに確認を依頼します:

```
「カート追加機能が正しく動くか、Playwrightで確認してほしい」
「ログインページのE2Eテストを書いて実行して」
```

Agentが自動的に:
1. Dev サーバーを起動（`npm run dev`）
2. TypeScript テストファイルを生成
3. Playwright でテストを実行
4. 結果を報告
5. テストファイルを保存するか削除するか確認

### PRレビュー時の確認

レビュー中にPlaywrightテストで変更を検証:

```
「PR #42 の変更をPlaywrightで動作確認して」
「このPRのUI変更が正しく機能しているか確認したい」
```

Agentが自動的に:
1. `gh pr diff <NUMBER>` で差分を取得
2. 変更されたファイルを解析
3. 変更箇所に絞ったテストを生成
4. テストを実行して結果を報告

## テストファイルの扱い

テスト実行後、Agentは毎回「テストファイルを保存するか削除するか」をユーザーに確認します。

- **保存する場合**: `e2e/` ディレクトリにそのまま残ります（再利用・改修可能）
- **削除する場合**: `e2e/` から削除されます（一時確認のみ）

## 生成されるテストの特徴

- **TypeScript** で記述
- `getByRole`, `getByLabel`, `getByText` 等の**セマンティックロケーター**を優先
- フラジルなCSSセレクタは使用しない
- ユーザー操作フローを忠実に再現
