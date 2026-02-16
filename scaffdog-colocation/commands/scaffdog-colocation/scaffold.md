---
description: scaffdogテンプレートからファイルをスキャフォールディング（生成）する。CLIまたはClaude直接作成を選択可能。
---

# scaffdog-colocation: scaffold

scaffdog テンプレートを使ってファイルを生成します。

## 手順

### 1. テンプレート一覧表示

`.scaffdog/` ディレクトリ内の `.md` ファイル（`config.js` を除く）を一覧表示する。

各テンプレートの frontmatter から `name` と `root` を抽出して表示:

```
利用可能なテンプレート:
  1. component (root: src/components)
  2. feature (root: src/features)
  3. hook (root: src/hooks)
```

### 2. テンプレート選択

ユーザーに使用するテンプレートを選択させる。

### 3. 生成方法の決定

scaffdog CLI が利用可能か確認する:

```bash
npx scaffdog --version
```

**CLI が使える場合**: scaffdog CLI を使用

```bash
npx scaffdog generate <template-name>
```

**CLI が使えない場合**: Claude が直接ファイルを作成

### 4A. CLI による生成

ユーザーに `npx scaffdog generate <template-name>` の実行を提案する。
`--answer` フラグで対話をスキップすることも提案する:

```bash
npx scaffdog generate component --answer "name:Button"
```

### 4B. Claude による直接生成

CLI が利用できない場合:

1. テンプレートの frontmatter から `questions` を読み取る
2. ユーザーに必要な入力値を質問する
3. テンプレートの内容を解釈し、各ファイルを生成する
4. ファイルマーカー（`# \`path\``）に基づいて、正しいパスにファイルを作成する
5. 条件分岐（`{{ if }}` / `{{ end }}`）を評価し、不要なファイルはスキップする
6. ヘルパー関数（`pascal`, `camel`, `kebab` 等）を適用する

### 5. 生成結果の表示

生成されたファイルの一覧を表示:

```
✓ 以下のファイルを生成しました:
  - src/components/Button/index.ts
  - src/components/Button/Button.tsx
  - src/components/Button/Button.types.ts
  - src/components/Button/Button.test.tsx
  - src/components/Button/Button.module.css
```
