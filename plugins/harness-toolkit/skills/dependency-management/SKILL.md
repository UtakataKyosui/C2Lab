---
name: 依存関係管理（proto / Knip / dependency-cruiser / ncu）
description: This skill should be used when the user asks to "依存関係を整理", "未使用コードを検出", use "proto", "Knip", "dependency-cruiser", "npm-check-updates", "ncu", "依存関係のバージョン管理", "不要な依存を削除", "依存グラフを可視化", or "パッケージを最新版に更新". Also activates when user mentions "ツールバージョン管理", "Node.js バージョン固定", or "循環依存の検出".
version: 0.1.0
---

# 依存関係管理（proto / Knip / dependency-cruiser / ncu）

4 つのツールでアプリケーションの依存関係を多角的に整理する：

- **proto**: 言語・パッケージマネージャのバージョン管理
- **Knip**: 未使用ファイル・エクスポート・依存関係の検出
- **dependency-cruiser**: 依存関係のバリデーションと可視化
- **npm-check-updates (ncu)**: package.json の依存関係を最新バージョンに更新

## proto — ツールバージョン管理

### 基本使用法

```bash
# 利用可能なツール一覧
proto list-remote node

# ツールをインストール
proto install node 22.0.0

# バージョンを固定（.prototools に記録）
proto pin node 22.0.0

# 現在のバージョン確認
proto list

# .prototools のバージョンで環境を揃える
proto use
```

### .prototools の設定

プロジェクトルートに `.prototools` を配置してバージョンを固定:

```toml
# .prototools
node = "22.0.0"
pnpm = "9.0.0"
```

チームメンバーが `proto use` を実行するだけで同じ環境になる。

### proto vs mise

| ツール | 特徴 |
|---|---|
| proto | Rust + WASM プラグインで任意ツールを管理可能 |
| mise | 広く使われ、既存の asdf プラグインと互換 |

プロジェクトに `mise.toml` が既にある場合は mise を継続使用する。

## Knip — 未使用コードの検出

### 基本使用法

```bash
# 未使用のファイル・エクスポート・依存関係を検出
knip

# JSON で出力
knip --reporter json

# 特定の issue タイプのみ表示
knip --include files         # 未使用ファイルのみ
knip --include exports       # 未使用エクスポートのみ
knip --include dependencies  # 未使用依存関係のみ

# 修正候補を表示
knip --fix
```

### knip.json の設定

```json
{
  "entry": ["src/index.ts"],
  "project": ["src/**/*.ts"],
  "ignore": ["**/*.test.ts"],
  "ignoreDependencies": ["@types/*"]
}
```

### よくある False Positive への対処

```json
{
  "ignoreExportsUsedInFile": true,
  "ignoreWorkspaces": ["packages/legacy-*"]
}
```

## dependency-cruiser — 依存関係のバリデーション

### 基本使用法

```bash
# 依存関係グラフの生成（SVG）
depcruise --output-type dot src | dot -T svg > deps.svg

# JSON で依存関係を出力
depcruise --output-type json src

# ルール違反を検出
depcruise --validate .dependency-cruiser.json src

# 設定ファイルを生成
depcruise --init
```

### .dependency-cruiser.json の設定例

```json
{
  "forbidden": [
    {
      "name": "no-circular",
      "severity": "error",
      "from": {},
      "to": { "circular": true }
    },
    {
      "name": "no-orphans",
      "severity": "warn",
      "from": { "orphan": true },
      "to": {}
    },
    {
      "name": "no-reach-into-node_modules",
      "severity": "error",
      "from": {},
      "to": { "path": "node_modules/.+" }
    }
  ]
}
```

### CI での利用

```bash
# 循環依存をエラーとして検出
depcruise --validate .dependency-cruiser.json --output-type err src
echo "Exit code: $?"
```

## npm-check-updates (ncu) — 依存関係の更新

### 基本使用法

```bash
# 更新可能なパッケージを確認（変更なし）
ncu

# package.json を直接更新
ncu -u

# 特定パッケージのみ更新
ncu -u react react-dom

# パターンでフィルタ
ncu -u --filter '@types/*'

# メジャーバージョン更新を除外
ncu -u --target minor

# patch のみ更新
ncu -u --target patch
```

### 安全な更新フロー

```bash
# 1. 更新可能なパッケージを確認
ncu

# 2. patch・minor のみ先に適用
ncu -u --target minor
pnpm install

# 3. テストを実行して問題がないか確認
pnpm test

# 4. メジャーバージョン更新は個別に対応
ncu -u --target latest react
```

### Workspace 対応

```bash
# 全 workspace のパッケージを確認
ncu --workspaces

# 特定 workspace のみ
ncu --workspace packages/frontend
```

## ツール間の使い分け

| 課題 | 使うツール |
|---|---|
| Node.js のバージョンをプロジェクトで統一したい | proto |
| 使っていないコードを削除してバンドルを軽くしたい | Knip |
| 循環依存や依存のアーキテクチャ違反を検出したい | dependency-cruiser |
| パッケージを最新バージョンに更新したい | ncu |

## 定期メンテナンスフロー

```bash
# 週次メンテナンスの流れ
ncu                    # 1. 更新可能パッケージを確認
knip                   # 2. 未使用コードがあれば削除
depcruise --validate . # 3. 依存関係ルールを確認
```

## Additional Resources

- **`references/knip-config.md`** - Knip 設定の詳細リファレンス
- **`references/dep-cruiser-rules.md`** - dependency-cruiser ルール集
