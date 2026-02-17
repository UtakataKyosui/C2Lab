# scaffdog テンプレート構文リファレンス

## テンプレートファイル構造

scaffdog テンプレートは `.scaffdog/` ディレクトリに配置する Markdown ファイル。

```
.scaffdog/
├── config.js          # オプション: グローバル設定
├── component.md       # コンポーネント用テンプレート
├── feature.md         # フィーチャー用テンプレート
└── page.md            # ページ用テンプレート
```

## Frontmatter

テンプレートファイルの先頭に YAML frontmatter を記述する。

```yaml
---
name: "component"        # テンプレート名（scaffdog generate で指定）
root: "src/components"   # 生成先のルートディレクトリ
output: "**/*"           # 出力パターン
questions:
  name:
    message: "Component name:"      # プロンプトメッセージ
  withTest:
    confirm: "Include tests?"       # Yes/No 質問
    initial: true                   # デフォルト値
  style:
    message: "Style solution:"
    choices:
      - "css-modules"               # 選択肢
      - "vanilla-extract"
      - "tailwind"
      - "none"
---
```

### Frontmatter フィールド

| フィールド | 必須 | 説明 |
|---|---|---|
| `name` | Yes | テンプレート識別名 |
| `root` | Yes | 出力ルートディレクトリ |
| `output` | Yes | 出力パス glob パターン |
| `questions` | No | ユーザーへの対話的質問 |

### Questions の種類

```yaml
questions:
  # テキスト入力
  name:
    message: "Name:"

  # 短縮形（message のみ）
  name: "Name:"

  # 確認（boolean）
  withTest:
    confirm: "Include tests?"
    initial: true

  # 選択
  style:
    message: "Style:"
    choices:
      - "css-modules"
      - "tailwind"

  # 選択（ラベル付き）
  style:
    message: "Style:"
    choices:
      - label: "CSS Modules"
        value: "css-modules"
      - label: "Tailwind CSS"
        value: "tailwind"
```

## ファイルマーカー

H1（`#`）で始まる行がファイル区切り。バッククォートで囲んだパスが出力ファイルパスになる。

```markdown
# `{{ inputs.name }}/index.ts`

ファイル内容...

# `{{ inputs.name }}/{{ inputs.name }}.tsx`

ファイル内容...
```

**条件付きファイル生成**:

```markdown
# `{{ inputs.name }}/{{ inputs.name }}.test.tsx`

{{ if inputs.withTest }}
import { render } from '@testing-library/react';
import { {{ inputs.name }} } from './{{ inputs.name }}';

describe('{{ inputs.name }}', () => {
  it('renders', () => {
    render(<{{ inputs.name }} />);
  });
});
{{ end }}
```

`{{ if }}` ブロックが空の場合、そのファイルは生成されない。

## テンプレート変数

### 組み込み変数

| 変数 | 説明 |
|---|---|
| `inputs.*` | questions で定義したユーザー入力 |
| `document.name` | テンプレートのファイル名（拡張子なし） |

### ヘルパー関数（フィルター）

scaffdog は Handlebars ベースのヘルパーを提供する。

#### 文字列変換

```
{{ inputs.name | camel }}      → "myComponent"
{{ inputs.name | pascal }}     → "MyComponent"
{{ inputs.name | kebab }}      → "my-component"
{{ inputs.name | snake }}      → "my_component"
{{ inputs.name | upper }}      → "MYCOMPONENT"
{{ inputs.name | lower }}      → "mycomponent"
{{ inputs.name | constant }}   → "MY_COMPONENT"
```

#### 文字列操作

```
{{ inputs.name | replace "old" "new" }}    # 文字列置換
{{ inputs.name | trim }}                    # 前後の空白除去
{{ inputs.name | plur }}                    # 複数形
```

## 条件分岐

```
{{ if inputs.withTest }}
  テストありの場合の内容
{{ end }}

{{ if inputs.style == "css-modules" }}
  CSS Modules の場合
{{ else if inputs.style == "tailwind" }}
  Tailwind の場合
{{ else }}
  その他
{{ end }}
```

## 繰り返し

```
{{ for item in inputs.items }}
  {{ item }}
{{ end }}
```

## 変数定義

```
{{ define "fileName" (inputs.name | pascal) }}
{{ fileName }}.tsx
```

## config.js（オプション）

`.scaffdog/config.js` でグローバル設定を行える。

```javascript
export default {
  files: ['.scaffdog/**/*.md'],
  helpers: [
    // カスタムヘルパーの定義
    {
      registry: (registry) => {
        registry.set('prefix', (context, value) => {
          return `Prefix${value}`;
        });
      },
    },
  ],
};
```

## CLI コマンド

```bash
# テンプレート一覧表示
npx scaffdog list

# テンプレートからファイル生成
npx scaffdog generate <template-name>

# ドライラン（ファイル生成なし）
npx scaffdog generate <template-name> --dry-run

# 対話をスキップして値を直接指定
npx scaffdog generate component --answer "name:Button"
```

## テンプレート設計のベストプラクティス

1. **questions を活用**: ユーザー入力でテンプレートを柔軟にする
2. **条件分岐でオプション対応**: テスト、スタイル、ストーリーなどをオプションに
3. **命名規則を統一**: `pascal` / `camel` / `kebab` フィルターで一貫性を保つ
4. **バレルファイルは必ず生成**: `index.ts` をテンプレートに含める
5. **型定義ファイルを分離**: `.types.ts` でコンポーネントの型を管理
