# repomix.config.json 完全リファレンス

## 設定ファイルの配置

プロジェクトルートに `repomix.config.json` を配置する。

## 完全な設定例

```json
{
  "output": {
    "filePath": "CONTEXT.md",
    "style": "markdown",
    "headerText": "This file is a packed representation of the repository contents.",
    "fileSummary": true,
    "directoryStructure": true,
    "showLineNumbers": false,
    "copyToClipboard": false,
    "instructionFilePath": "repomix-instructions.md"
  },
  "include": [
    "src/**",
    "tests/**",
    "*.config.ts",
    "*.config.js"
  ],
  "ignore": {
    "useGitignore": true,
    "useDefaultPatterns": true,
    "customPatterns": [
      "*.lock",
      "*.log",
      "dist/**",
      "build/**",
      ".next/**",
      "coverage/**",
      "node_modules/**",
      "*.min.js",
      "*.d.ts"
    ]
  },
  "security": {
    "enableSecurityCheck": true
  }
}
```

## フィールド説明

### output

| フィールド | 型 | デフォルト | 説明 |
|---|---|---|---|
| `filePath` | string | `repomix-output.txt` | 出力ファイルパス |
| `style` | `markdown` \| `xml` \| `plain` | `plain` | 出力フォーマット |
| `headerText` | string | - | ファイル先頭に追加するテキスト |
| `fileSummary` | boolean | `true` | ファイル概要セクションを含める |
| `directoryStructure` | boolean | `true` | ディレクトリ構造を含める |
| `showLineNumbers` | boolean | `false` | 行番号を表示 |
| `copyToClipboard` | boolean | `false` | クリップボードにコピー |

### include / ignore

```json
{
  "include": ["src/**", "lib/**"],
  "ignore": {
    "useGitignore": true,
    "useDefaultPatterns": true,
    "customPatterns": ["dist/**", "*.test.ts"]
  }
}
```

`include` が空の場合、全ファイルが対象。`ignore.useGitignore: true` で `.gitignore` を自動尊重。

## スタイル別の特徴

### markdown スタイル

```markdown
# File: src/index.ts

\`\`\`typescript
// file contents
\`\`\`
```

人間可読で、ほとんどの AI モデルが理解しやすい。

### xml スタイル

```xml
<file path="src/index.ts">
<![CDATA[
// file contents
]]>
</file>
```

構造化されており、パース処理向け。

### plain スタイル

```
=== File: src/index.ts ===
// file contents
```

最小トークン。シンプルな処理向け。

## 差分ベース生成（推奨）

Stop Hook での差分ベース生成では設定ファイルを使わず、コマンドライン引数で制御:

```bash
repomix --include "changed-file1.ts,changed-file2.ts" --output CONTEXT.md --style markdown
```

## 用途別の推奨設定

### セッション引き継ぎ用（CONTEXT.md）

```json
{
  "output": {
    "filePath": "CONTEXT.md",
    "style": "markdown",
    "directoryStructure": true,
    "fileSummary": true
  },
  "ignore": {
    "useGitignore": true,
    "useDefaultPatterns": true,
    "customPatterns": ["CONTEXT*.md", "*.lock", "dist/**"]
  }
}
```

### AI レビュー用（コードのみ）

```json
{
  "output": {
    "style": "xml",
    "showLineNumbers": true
  },
  "include": ["src/**"],
  "ignore": {
    "useGitignore": true,
    "customPatterns": ["**/*.test.ts", "**/*.spec.ts"]
  }
}
```
