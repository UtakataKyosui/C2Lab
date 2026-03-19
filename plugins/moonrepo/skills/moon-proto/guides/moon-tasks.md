# Tasks and Projects in Moonrepo

## moon.yml の基本構造

プロジェクトディレクトリに置く設定ファイル。タスク定義・プロジェクトメタ・依存関係を記述します。

```yaml
# packages/ui/moon.yml
$schema: 'https://moonrepo.dev/schemas/project.json'

type: 'library'          # library | application | tool | unknown
language: 'typescript'
tags: ['ui', 'frontend']

tasks:
  build:
    command: 'tsc --build'
    inputs:
      - 'src/**/*'
      - 'tsconfig.json'
    outputs:
      - 'dist'

  test:
    command: 'vitest run'
    inputs:
      - 'src/**/*'
      - 'tests/**/*'
    deps:
      - '~:build'        # ~: = 同プロジェクト内の依存タスク

  lint:
    command: 'eslint src'
    inputs:
      - 'src/**/*.ts'
      - '.eslintrc.*'
```

## タスクの実行

```bash
# 特定プロジェクト・タスクを実行
moon run ui:build
moon run ui:test

# 全プロジェクトで同名タスクを実行
moon run :test
moon run :build

# 複数タスクを指定
moon run ui:build api:build

# 変更があったプロジェクトのみ実行
moon run :test --affected
moon run :build --affected --base main    # main からの差分

# ドライラン（実際には実行しない）
moon run :build --dryRun
```

## CI 向けコマンド

```bash
# CI で変更されたプロジェクトのタスクを自動実行
moon ci                   # moon run :build :test :lint --affected に相当
moon ci --base main       # 比較ブランチを指定

# プロジェクト・タスクの状態確認
moon check ui             # ui の全タスクを実行してチェック
moon check --all          # 全プロジェクトをチェック
```

## タスクオプション

```yaml
tasks:
  build:
    command: 'webpack'
    options:
      cache: true              # キャッシュを有効化（デフォルト: true）
      runInCI: true            # CI でも実行する（デフォルト: true）
      outputStyle: 'buffer'    # 出力スタイル: buffer | stream | on-exit
      shell: true              # シェル経由で実行
      os: ['linux', 'macos']   # 特定 OS のみ実行

  deploy:
    command: './scripts/deploy.sh'
    local: false               # ローカルでは実行しない（CI のみ）
    options:
      runInCI: true
      persistent: true         # 長時間実行プロセス（dev server 等）
```

## タスクの依存関係

```yaml
tasks:
  build:
    command: 'tsc'
    deps:
      - '~:codegen'            # 同プロジェクトの codegen タスクを先に実行
      - 'utils:build'          # utils プロジェクトの build を先に実行
      - '^:build'              # 依存プロジェクト全ての build を先に実行
```

## ワークスペースレベルのタスク継承

`.moon/tasks.yml` に定義したタスクは全プロジェクトに継承されます。

```yaml
# .moon/tasks.yml
tasks:
  lint:
    command: 'eslint .'
    inputs:
      - 'src/**/*.ts'
      - '.eslintrc.*'

  format:
    command: 'prettier --check .'
    inputs:
      - 'src/**/*'
```

言語・タグ単位でも設定可能：

```yaml
# .moon/tasks/node.yml  → language: node のプロジェクトに適用
tasks:
  node-version:
    command: 'node --version'
```

## トークンシステム

コマンドや inputs/outputs 内で使えるビルトイン変数：

```yaml
tasks:
  build:
    command: 'tsc --outDir $projectRoot/dist'
    inputs:
      - '@group(sources)'      # groups で定義したファイル群を参照
    outputs:
      - '$projectRoot/dist'

# .moon/workspace.yml で groups を定義
fileGroups:
  sources:
    - 'src/**/*.ts'
  tests:
    - 'tests/**/*.test.ts'
```

主なトークン：

| トークン | 内容 |
|---|---|
| `$projectRoot` | プロジェクトのルートパス |
| `$workspaceRoot` | ワークスペースのルートパス |
| `$target` | `project:task` 形式のターゲット名 |
| `@group(name)` | fileGroups で定義したファイル群 |
| `@globs(pattern)` | glob マッチしたファイル一覧 |

## プロジェクト間依存関係

```yaml
# packages/app/moon.yml
dependsOn:
  - 'utils'
  - 'ui'
  - id: 'api'
    scope: 'peer'    # peer | development | production
```

## クエリ

```bash
# プロジェクト一覧の確認
moon query projects
moon query projects --affected
moon query projects --tags frontend

# タスク一覧の確認
moon query tasks
moon query tasks --affected
```

## グラフの可視化

```bash
moon graph                     # 依存グラフをブラウザで表示
moon graph ui                  # 特定プロジェクトのグラフ
moon graph --dot               # DOT 形式で出力（Graphviz）
```
