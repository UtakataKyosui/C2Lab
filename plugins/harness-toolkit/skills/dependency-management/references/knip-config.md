# Knip 設定リファレンス

## knip.json の完全な設定例

```json
{
  "$schema": "https://unpkg.com/knip@latest/schema.json",
  "entry": [
    "src/index.ts",
    "src/main.ts"
  ],
  "project": [
    "src/**/*.ts",
    "src/**/*.tsx"
  ],
  "ignore": [
    "**/*.test.ts",
    "**/*.spec.ts",
    "src/generated/**"
  ],
  "ignoreDependencies": [
    "@types/*",
    "typescript",
    "eslint",
    "prettier"
  ],
  "ignoreExportsUsedInFile": false,
  "ignoreWorkspaces": [],
  "rules": {
    "files": "error",
    "exports": "warn",
    "types": "warn",
    "dependencies": "error",
    "unlisted": "error"
  }
}
```

## Issue タイプと意味

| タイプ | 意味 | fix コマンド |
|---|---|---|
| `files` | 参照されていないファイル | 削除またはエントリポイントに追加 |
| `exports` | 使用されていない export | export を削除または `ignoreExportsUsedInFile: true` |
| `types` | 使用されていない型定義 | 型を削除 |
| `dependencies` | package.json にあるが使われていない依存 | `npm uninstall <pkg>` |
| `unlisted` | 使われているが package.json にない依存 | `npm install <pkg>` |
| `binaries` | 使われているが package.json にないバイナリ | `npm install <pkg>` |

## Monorepo / Workspace 設定

```json
{
  "workspaces": {
    "packages/*": {
      "entry": ["src/index.ts"],
      "project": ["src/**/*.ts"]
    },
    "apps/web": {
      "entry": ["app/page.tsx", "app/layout.tsx"]
    }
  }
}
```

## プラグイン設定

Knip は多くのフレームワークを自動検出するが、明示的に設定することもできる:

```json
{
  "next": {
    "entry": ["app/**/*.{ts,tsx}", "pages/**/*.{ts,tsx}"]
  },
  "vitest": {
    "entry": ["**/*.test.ts", "**/*.spec.ts"]
  }
}
```

## よくある False Positive の対処

```json
{
  "ignore": [
    "src/polyfills.ts",
    "src/types/global.d.ts"
  ],
  "ignoreDependencies": [
    "reflect-metadata",
    "tslib"
  ],
  "ignoreExportsUsedInFile": true
}
```

## CI での利用

```bash
# エラーがあれば CI を失敗させる
knip --no-exit-code  # exit 0 を強制（CI 失敗させない場合）

# 特定 issue タイプのみチェック
knip --include dependencies,unlisted

# JSON で出力して詳細分析
knip --reporter json > knip-results.json
```
